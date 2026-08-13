# AGENTS.md

## Cursor Cloud specific instructions

This repo is a Python AI Presentation Generator (CLI + Flask Web UI). Designer layouts and Claude/Ollama backends are the main product path.

### Services

| Service | Command | Notes |
|---------|---------|-------|
| Desktop app | `python desktop_app.py` | Native window via `pywebview` (falls back to browser). Install Desktop icon with `./install_desktop_shortcut.sh` |
| Web UI | `python web_ui.py` | http://localhost:5050 — Flask on `0.0.0.0` (default port **5050** to avoid macOS AirPlay on 5000; override with `PORT=...`) |
| CLI | `python cli.py <input.txt> -m claude -t sunset_gradient` | Core generation path |

Standard install/run details: see `README.md`, `QUICKSTART.md`, and `package` scripts in those docs. Dependencies: `pip install -r requirements.txt` (includes `pyyaml` and `anthropic`).

### Non-obvious gotchas

- **Claude requires `ANTHROPIC_API_KEY`** in the environment. Without it, `-m claude` / Web UI Claude selection fails. Local Ollama models (`dolphin_8b`, `dolphin_70b`, `hermes`) need `ollama serve` on `localhost:11434` and pulled models — optional if using Claude only.
- **Default model/theme** in `config.yaml` are `claude` and `sunset_gradient`. Prefer those for demos unless testing Ollama.
- **No automated test/lint suite** is configured in-repo. Sanity-check with `python cli.py --list-models`, `python cli.py --list-themes`, Flask homepage/`/api/models`, and a short `cli.py` generation that writes a `.pptx`.
- **Generated `.pptx` files and `outputs/` are gitignored.** Copy demos to `/opt/cursor/artifacts/` when you need reviewable evidence.
- Web UI keeps generated decks under `outputs/` with sidecar `.json` outlines: preview + **re-theme without another AI call** via `/api/presentations` and `/api/presentations/<id>/retheme`.
- Standalone demos (`demo_*.py`) still exist; production path is `presentation_generator.py` via `cli.py` / `web_ui.py`.
