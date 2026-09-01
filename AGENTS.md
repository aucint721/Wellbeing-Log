# AGENTS.md

## Cursor Cloud specific instructions

This repo is a Python AI Presentation Generator (CLI + Flask Web UI). Designer layouts and Claude/Ollama backends are the main product path.

### Services

| Service | Command | Notes |
|---------|---------|-------|
| Desktop app | `python desktop_app.py` | Native window via `pywebview` (falls back to browser). Install Desktop icon with `./install_desktop_shortcut.sh` |
| Web UI | `python web_ui.py` | http://localhost:5050 — Flask on `0.0.0.0` (default port **5050** to avoid macOS AirPlay on 5000; override with `PORT=...`) |
| CLI | `python cli.py <input.txt> -m claude -t sunset_gradient` | Core generation path |
| File Triage | `python file_triage_ui.py` | http://127.0.0.1:5051 — local gather/view/decide for overflowing folders (iCloud Drive). Desktop: `python desktop_file_triage.py`. Binds localhost only. |

Standard install/run details: see `README.md`, `QUICKSTART.md`, and `package` scripts in those docs. Dependencies: `pip install -r requirements.txt` (includes `pyyaml` and `anthropic`).

### Non-obvious gotchas

- **Claude requires `ANTHROPIC_API_KEY`** in the environment. Without it, `-m claude` / Web UI Claude selection fails. Local Ollama models use the exact `model_id` values in `config.yaml` (currently `llama3:70b`, `hermes-auditor:latest`, `dolphin-hennie:latest`) and need the Ollama app/`ollama serve` on `localhost:11434` — optional if using Claude only. `/api/models` reports live Ready/Needs setup status for the UI. CLI `-m` choices are loaded from `config.yaml`.
- **Default model/theme** in `config.yaml` are `claude` and `sunset_gradient`. Prefer those for demos unless testing Ollama.
- **No automated test/lint suite** is configured in-repo. Sanity-check with `python cli.py --list-models`, `python cli.py --list-themes`, Flask homepage/`/api/models`, and a short `cli.py` generation that writes a `.pptx`.
- **Generated `.pptx` files and `outputs/` are gitignored.** Copy demos to `/opt/cursor/artifacts/` when you need reviewable evidence.
- Web UI keeps generated decks under `outputs/` with sidecar `.json` outlines: preview + **re-theme without another AI call** via `/api/presentations` and `/api/presentations/<id>/retheme`.
- **Text-line animations** must use PowerPoint’s real click-group skeleton: outer `par` (`delay=indefinite`) → mid `par` → effect `par` (`nodeType=clickEffect`, `presetClass=entr`, `grpId`) with `<p:set>`/`<p:animEffect>` inside, plus a `p:bldLst`/`p:bldP` entry per shape and `sldTgt` on prev/next conditions. Missing `bldLst` or the 3-level nesting makes Mac PowerPoint hide lines and advance the slide on click. Animations only play in **Slide Show**; rebuild PPTX after animation code changes.
- **Photo themes** use local files under `theme_assets/` referenced by `background_image` in `config.yaml`. Real Unsplash photos are fetched with `python scripts/fetch_theme_photos.py` (do not put remote URLs in `background_image`). Transition/bullet catalogs live in `config.yaml` `animations:` and must stay in sync with `_add_transition` / `_add_appear_animations` mappings in `presentation_generator.py`.
- **Mac Desktop shortcuts:** run `./install_desktop_shortcuts.sh` once after clone. It writes numbered `.command` launchers to `~/Desktop` (Setup, Set Claude API Key, Update, Open). In-repo copies live in `mac_shortcuts/`. First-time flow: Setup → Set API Key → Open. Updates: double-click Update. **Set Claude API Key** prefers clipboard (`pbpaste`): copy the key, press Enter — Terminal paste is optional.
- Standalone demos (`demo_*.py`) still exist; production path is `presentation_generator.py` via `cli.py` / `web_ui.py`.
- **File Triage** (`file_triage.py` / `file_triage_ui.py`) is a local inventory + decision tool, not an iCloud API. Destinations default to `~/Current`, `~/Documents-Local`, `~/Archive`, and `_TriageTrash` on this Mac. Scan a local copy of Drive (after copying off iCloud), sort by size, bucket files, then Apply. Demo tree: `python scripts/make_triage_demo.py`. Do not bind it to `0.0.0.0` — it can move files on disk. Duplicate Detective / Photo Sweeper / Calibre / Hazel stay in their own lanes (see `FILE_TRIAGE.md`).
