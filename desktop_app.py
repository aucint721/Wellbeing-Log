#!/usr/bin/env python3
"""
Desktop launcher for AI Presentation Generator.

Starts the Flask Web UI in the background and opens it in a native window
(pywebview). Falls back to your default browser if a native window isn't available.
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Always run from the project root (this file's directory)
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env if present (optional)
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except Exception:
    pass


def _pick_port(preferred: int = 5050) -> int:
    env_port = os.getenv("PORT")
    if env_port:
        return int(env_port)
    for port in (preferred, 5051, 5052, 8080, 8000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port found for the desktop app")


def _wait_for_server(host: str, port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return True
            except OSError:
                time.sleep(0.2)
    return False


def main() -> int:
    port = _pick_port()
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    # Import after chdir so templates/config resolve correctly
    from web_ui import app

    def run_server():
        # use_reloader=False is required when embedding in a desktop thread
        app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    if not _wait_for_server(host, port):
        print(f"Could not start server on {url}")
        return 1

    print("=" * 60)
    print("AI Presentation Generator — Desktop")
    print("=" * 60)
    print(f"Running at: {url}")
    print("Close the window (or press Ctrl+C) to quit.")
    print("=" * 60)

    # Prefer a native desktop window
    try:
        import webview

        window = webview.create_window(
            "AI Presentation Generator",
            url,
            width=1280,
            height=900,
            min_size=(900, 700),
        )
        webview.start()
        return 0
    except Exception as exc:
        print(f"Native window unavailable ({exc}). Opening your browser instead…")
        webbrowser.open(url)
        try:
            while thread.is_alive():
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
