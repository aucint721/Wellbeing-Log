#!/usr/bin/env python3
"""
Local File Triage web UI.

Default bind is 127.0.0.1:5051 so only this computer can see your file list.
This app can move files on disk after you confirm Apply — keep it local.
"""

from __future__ import annotations

import mimetypes
import os
import threading
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, send_file

from file_triage import (
    TriageSession,
    default_destinations,
    format_bytes,
    session_dir,
    suggested_scan_roots,
)

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True
ROOT = Path(__file__).resolve().parent

_lock = threading.Lock()
_session: TriageSession | None = None
_session_path: Path | None = None
_scan = {
    "running": False,
    "error": None,
    "phase": None,
    "visited": 0,
    "files": 0,
    "hashed": 0,
    "to_hash": 0,
    "seconds": None,
    "root": None,
}


def _current() -> TriageSession:
    if _session is None:
        abort(400, description="No scan yet. Choose a folder first.")
    return _session


def _save_locked() -> None:
    global _session_path
    if _session is None:
        return
    path = _session_path or (session_dir(ROOT) / f"{_session.id}.json")
    _session.save(path)
    _session_path = path


@app.get("/")
def home():
    return render_template("file_triage.html")


@app.get("/api/bootstrap")
def bootstrap():
    with _lock:
        payload = {
            "suggested_roots": suggested_scan_roots(),
            "default_destinations": default_destinations(),
            "scan": dict(_scan),
            "session": _session.summary() if _session else None,
            "session_path": str(_session_path) if _session_path else None,
        }
    return jsonify(payload)


@app.post("/api/scan")
def start_scan():
    data = request.get_json(silent=True) or {}
    folder = (data.get("folder") or "").strip()
    if not folder:
        return jsonify({"ok": False, "error": "Choose a folder to scan."}), 400
    skip_hidden = bool(data.get("skip_hidden", True))
    destinations = data.get("destinations") or {}

    with _lock:
        if _scan["running"]:
            return jsonify({"ok": False, "error": "A scan is already running."}), 409
        _scan.update(
            {
                "running": True,
                "error": None,
                "phase": "starting",
                "visited": 0,
                "files": 0,
                "hashed": 0,
                "to_hash": 0,
                "seconds": None,
                "root": folder,
            }
        )

    def _work():
        global _session, _session_path
        try:
            session = TriageSession()
            if destinations:
                session.set_destinations(destinations)

            def progress(info):
                with _lock:
                    _scan.update({k: info.get(k, _scan.get(k)) for k in info})
                    _scan["running"] = info.get("phase") != "done"

            session.scan(folder, skip_hidden=skip_hidden, progress=progress)
            with _lock:
                _session = session
                _session_path = session_dir(ROOT) / f"{session.id}.json"
                _save_locked()
                _scan["running"] = False
                _scan["phase"] = "done"
                _scan["error"] = None
        except Exception as exc:
            with _lock:
                _scan["running"] = False
                _scan["phase"] = "error"
                _scan["error"] = str(exc)

    threading.Thread(target=_work, daemon=True).start()
    return jsonify({"ok": True, "scan": dict(_scan)})


@app.get("/api/scan/status")
def scan_status():
    with _lock:
        return jsonify({"ok": True, "scan": dict(_scan), "ready": _session is not None and not _scan["running"]})


@app.post("/api/destinations")
def set_destinations():
    data = request.get_json(silent=True) or {}
    with _lock:
        session = _current()
        session.set_destinations(data.get("destinations") or data)
        _save_locked()
        return jsonify({"ok": True, "destinations": session.destinations})


@app.get("/api/summary")
def summary():
    with _lock:
        return jsonify(_current().summary())


@app.get("/api/files")
def list_files():
    args = request.args
    with _lock:
        session = _current()
        result = session.list_files(
            q=args.get("q", ""),
            type_group=args.get("type_group", ""),
            decision=args.get("decision", ""),
            folder=args.get("folder", ""),
            duplicates_only=args.get("duplicates") in ("1", "true", "yes"),
            min_size=int(args.get("min_size") or 0),
            older_than_days=int(args.get("older_than_days") or 0),
            sort=args.get("sort") or "size",
            limit=min(int(args.get("limit") or 80), 300),
            offset=int(args.get("offset") or 0),
        )
        return jsonify(result)


@app.get("/api/files/<fid>")
def file_detail(fid: str):
    with _lock:
        rec = _current().get_file(fid)
    if not rec:
        return jsonify({"error": "File not found"}), 404
    return jsonify(rec)


@app.get("/api/files/<fid>/preview")
def file_preview(fid: str):
    with _lock:
        rec = _current().files.get(fid)
    if not rec:
        abort(404)
    path = Path(rec["path"])
    if not path.exists():
        abort(404)
    mime, _ = mimetypes.guess_type(path.name)
    return send_file(path, as_attachment=False, mimetype=mime or "application/octet-stream")


@app.post("/api/files/<fid>/decide")
def decide_one(fid: str):
    data = request.get_json(silent=True) or {}
    decision = data.get("decision")
    with _lock:
        try:
            rec = _current().decide(fid, decision)
        except KeyError:
            return jsonify({"error": "File not found"}), 404
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        _save_locked()
        return jsonify({"ok": True, "file": rec, "summary": _session.summary()})


@app.post("/api/decide-many")
def decide_many():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    decision = data.get("decision")
    if not ids:
        return jsonify({"ok": False, "error": "No files selected."}), 400
    with _lock:
        count = _current().decide_many(ids, decision)
        _save_locked()
        return jsonify({"ok": True, "count": count, "summary": _session.summary()})


@app.post("/api/decide-folder")
def decide_folder():
    data = request.get_json(silent=True) or {}
    folder = (data.get("folder") or "").strip()
    if not folder:
        return jsonify({"ok": False, "error": "Folder is required."}), 400
    with _lock:
        count = _current().decide_folder(folder, data.get("decision"))
        _save_locked()
        return jsonify({"ok": True, "count": count, "summary": _session.summary()})


@app.get("/api/duplicates")
def duplicates():
    with _lock:
        return jsonify({"groups": _current().duplicate_groups()})


@app.post("/api/duplicates/<group_id>/keep")
def keep_duplicate(group_id: str):
    data = request.get_json(silent=True) or {}
    keep_id = data.get("keep_id")
    if not keep_id:
        return jsonify({"error": "keep_id is required"}), 400
    with _lock:
        try:
            count = _current().decide_duplicates(group_id, keep_id)
        except KeyError:
            return jsonify({"error": "Unknown duplicate group"}), 404
        _save_locked()
        return jsonify({"ok": True, "count": count, "summary": _session.summary()})


@app.get("/api/plan")
def plan():
    with _lock:
        actions = _current().planned_actions()
        total = sum(item["size"] for item in actions)
        return jsonify(
            {
                "count": len(actions),
                "size": total,
                "size_label": format_bytes(total),
                "actions": actions[:400],
                "truncated": len(actions) > 400,
            }
        )


@app.post("/api/apply")
def apply():
    data = request.get_json(silent=True) or {}
    dry_run = bool(data.get("dry_run", True))
    with _lock:
        result = _current().apply(dry_run=dry_run)
        _save_locked()
        return jsonify(result)


def main() -> None:
    host = os.getenv("TRIAGE_HOST", "127.0.0.1")
    port = int(os.getenv("TRIAGE_PORT") or os.getenv("PORT") or 5051)
    print("=" * 60)
    print("File Triage — gather, view, decide")
    print("=" * 60)
    print(f"Open: http://{host}:{port}")
    print("This stays on your computer. Nothing is uploaded.")
    print("Delete moves files into Triage Trash until you empty it.")
    print("=" * 60)
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
