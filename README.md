# ✨ AI Presentation Generator — Enhanced Designer

Create beautiful, designer-quality PowerPoint presentations from text using **Claude** (best quality) or your local Ollama models (`llama3:70b`, `hermes-auditor:latest`, `dolphin-hennie:latest`).

## ✨ Features

- **🤖 Claude + Local Models**: Claude Sonnet for punchy, memorable content; Ollama models for fully local/private runs
- **🎨 13 Designer Themes**: Classic + Neon Cyber, Sunset Gradient, Ocean Deep, Lavender Dream, and more
- **✨ Designer Layouts**: Geometric accents, gradient simulation, modern visual hierarchy
- **💻 Two Interfaces**: Web UI (easy) or CLI (powerful)
- **📊 Native PowerPoint**: Fully editable `.pptx` export

## 📋 Requirements

- Python 3.8+
- For Claude: `ANTHROPIC_API_KEY` environment variable
- For local models: Ollama running with `llama3:70b`, `hermes-auditor:latest`, and/or `dolphin-hennie:latest` (exact names from `ollama list`)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Choose Your Interface

#### Option A: Desktop App (easiest on Mac)

```bash
cd ~/Wellbeing-Log
chmod +x install_desktop_shortcuts.sh
./install_desktop_shortcuts.sh
```

Then on the Desktop, double-click in order:

1. **1. Setup Presentation Generator** — creates `venv` and installs packages  
2. **2. Set Claude API Key** — pastes your Anthropic key into `.env`  
3. **4. Open Presentation Generator** — launches the app  

Later: **3. Update Presentation Generator** pulls the latest from GitHub and refreshes packages.

If macOS blocks a shortcut: **right-click → Open → Open**.

Or run once from the project folder:

```bash
python desktop_app.py
```

#### Option B: Web UI in browser

```bash
export ANTHROPIC_API_KEY=your_key_here   # for Claude
python web_ui.py
```

Open http://localhost:5050

(Port defaults to **5050** so it doesn’t clash with macOS AirPlay on 5000. Override with `PORT=8080 python web_ui.py` if needed.)

#### Option C: Command Line

```bash
export ANTHROPIC_API_KEY=your_key_here
python cli.py example_lesson_plan.txt -m claude -n 12 -t sunset_gradient
```
## 🎯 Usage Examples

```bash
# List models / themes
python cli.py --list-models
python cli.py --list-themes

# Claude + Sunset Gradient (recommended)
python cli.py lesson_plan.txt -m claude -t sunset_gradient -n 12

# Quick local draft (your custom Dolphin)
python cli.py notes.txt -m dolphin_hennie -t mint_fresh

# Technical / auditor-style content
python cli.py lecture_notes.txt -m hermes_auditor -t education -n 20

# Local Llama 3 70B
python cli.py notes.txt -m llama3_70b -t sunset_gradient
```

## 🤖 Model Selection Guide

| Model (UI / CLI key) | Ollama `model_id` | When to Use |
|----------------------|-------------------|-------------|
| **Claude** (`claude`) | Anthropic API | Best writing & structure (default) |
| **Llama 3 70B** (`llama3_70b`) | `llama3:70b` | Strong local general-purpose |
| **Hermes Auditor** (`hermes_auditor`) | `hermes-auditor:latest` | Technical / educational / review |
| **Dolphin Hennie** (`dolphin_hennie`) | `dolphin-hennie:latest` | Fast local drafts in your style |

## 🎨 Available Themes

**Classic:** Modern Professional, Dark Tech, Education Blue, Warm Earth

**Designer:** Neon Cyberpunk, Sunset Gradient (default), Ocean Deep, Lavender Dream, Forest Minimal, Royal Purple, Coral Pink, Midnight Blue, Mint Fresh

**Photo (Unsplash backgrounds):** Ocean, Forest, Sunset, Mountain, City Night, Desert, Classroom, Library, Chalkboard, Aurora, Beach, Workspace, Flowers, Lake, Snow, Rain

Add color themes in `config.yaml` with `primary_color`, `accent_color`, `background`, `text_color`, and optional `gradient_colors`. Photo themes also set `style: photo` and `background_image: theme_assets/...`. Refresh photos with `python scripts/fetch_theme_photos.py`.

## 🎬 Transitions & text-line animations

Choose in the Web UI or CLI (`--transition`, `--bullet-anim`). Catalog lives in `config.yaml` under `animations:` — slide transitions (fade, push, wipe, cover, split, zoom, …) and per-line bullet effects (fade in, fly from sides, wipe, zoom, float up, …).

## 🛠️ Configuration

Edit `config.yaml` for models, themes, and defaults. Claude settings:

```yaml
claude:
  model_id: "claude-sonnet-5"
```

Set the API key via environment (preferred):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## 📚 Project Structure

```
.
├── config.yaml                  # Models + themes + animation catalogs
├── presentation_generator.py    # Core designer engine
├── cli.py                       # Command-line interface
├── web_ui.py                    # Flask web interface
├── templates/index.html         # Web UI
├── theme_assets/                # Photo theme backgrounds (Unsplash)
├── scripts/fetch_theme_photos.py
├── demo_designer_claude.py      # Standalone designer demo
├── demo_enhanced_claude.py      # Standalone enhanced demo
├── requirements.txt
└── README.md
```

## 🔧 Troubleshooting

### Ollama: connection refused / local model errors

`llama3:70b`, `hermes-auditor:latest`, and `dolphin-hennie:latest` run through **local Ollama**, not Claude. Claude does not need Ollama.

```bash
# 1. Open the Ollama app (Mac) or run: ollama serve
# 2. Confirm your models are listed exactly as configured
ollama list
curl http://localhost:11434/api/tags
```

The Web UI marks each local model as **Ready** or **Needs setup** after checking Ollama. Edit `config.yaml` `model_id` values if your local names differ.

### Claude: missing API key
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Model not found (Ollama)
Confirm the name matches `ollama list` and `config.yaml`, e.g. `hermes-auditor:latest`.

## 🎉 Get Started

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python web_ui.py
```
