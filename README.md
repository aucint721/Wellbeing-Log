# ✨ AI Presentation Generator — Enhanced Designer

Create beautiful, designer-quality PowerPoint presentations from text using **Claude** (best quality) or your local Ollama models (Dolphin 8B, Dolphin 70B, Hermes).

## ✨ Features

- **🤖 Claude + Local Models**: Claude Sonnet for punchy, memorable content; Ollama models for fully local/private runs
- **🎨 13 Designer Themes**: Classic + Neon Cyber, Sunset Gradient, Ocean Deep, Lavender Dream, and more
- **✨ Designer Layouts**: Geometric accents, gradient simulation, modern visual hierarchy
- **💻 Two Interfaces**: Web UI (easy) or CLI (powerful)
- **📊 Native PowerPoint**: Fully editable `.pptx` export

## 📋 Requirements

- Python 3.8+
- For Claude: `ANTHROPIC_API_KEY` environment variable
- For local models: Ollama running with `dolphin-llama3:8b`, `dolphin-llama3:70b`, and/or `hermes3`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Choose Your Interface

#### Option A: Desktop App (easiest on Mac)

```bash
pip install -r requirements.txt
./install_desktop_shortcut.sh
```

Then double-click **Presentation Generator** on your Desktop.

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

# Quick local draft
python cli.py notes.txt -m dolphin_8b -t mint_fresh

# Technical content with Hermes
python cli.py lecture_notes.txt -m hermes -t education -n 20
```

## 🤖 Model Selection Guide

| Model | Provider | When to Use | Quality |
|-------|----------|-------------|---------|
| **Claude** | Anthropic API | Best writing & structure (default) | Premium++ |
| **Dolphin 8B** | Ollama (local) | Quick drafts, offline | Good |
| **Dolphin 70B** | Ollama (local) | Strong local quality | Premium |
| **Hermes** | Ollama (local) | Technical / educational | Premium+ |

## 🎨 Available Themes

**Classic:** Modern Professional, Dark Tech, Education Blue, Warm Earth

**Designer:** Neon Cyberpunk, Sunset Gradient (default), Ocean Deep, Lavender Dream, Forest Minimal, Royal Purple, Coral Pink, Midnight Blue, Mint Fresh

Add your own in `config.yaml` with `primary_color`, `accent_color`, `background`, `text_color`, and optional `gradient_colors`.

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
├── config.yaml                  # Models + 13 themes
├── presentation_generator.py    # Core designer engine
├── cli.py                       # Command-line interface
├── web_ui.py                    # Flask web interface
├── templates/index.html         # Web UI
├── demo_designer_claude.py      # Standalone designer demo
├── demo_enhanced_claude.py      # Standalone enhanced demo
├── requirements.txt
└── README.md
```

## 🔧 Troubleshooting

### Claude: missing API key
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Ollama: connection refused
```bash
ollama serve
```

### Model not found (Ollama)
```bash
ollama pull dolphin-llama3:8b
```

## 🎉 Get Started

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python web_ui.py
```
