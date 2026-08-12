# 🎨 AI Presentation Generator

Create beautiful, professional presentations from text using **your local AI models** (Dolphin 8B, Dolphin 70B, and Hermes). No subscriptions, no cloud uploads, completely private and free forever.

## ✨ Features

- **🤖 Multiple AI Models**: Choose between Dolphin 8B (fast), Dolphin 70B (premium), or Hermes (technical)
- **🎨 Beautiful Themes**: Modern Professional, Dark Tech, Education Blue, Warm Earth
- **💻 Two Interfaces**: Web UI (easy) or CLI (powerful)
- **📊 PowerPoint Export**: Native PPTX files, fully editable
- **🔒 100% Private**: Everything runs locally on your machine
- **💰 Zero Cost**: No API fees, no subscriptions, completely free

## 📋 Requirements

- Python 3.8+
- Ollama installed and running
- Your local models: `dolphin-llama3:8b`, `dolphin-llama3:70b`, `hermes3`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Make Sure Ollama is Running

```bash
# Start Ollama (if not already running)
ollama serve
```

### 3. Choose Your Interface

#### Option A: Web UI (Recommended for Beginners)

```bash
python web_ui.py
```

Then open http://localhost:5000 in your browser.

#### Option B: Command Line

```bash
# Basic usage
python cli.py example_lesson_plan.txt

# With options
python cli.py my_content.txt -m dolphin_70b -n 15 -t modern -o my_presentation.pptx
```

## 🎯 Usage Examples

### Web UI

1. Start the web server: `python web_ui.py`
2. Open http://localhost:5000
3. Paste your lesson plan or content
4. Select your preferred AI model
5. Choose a theme
6. Click "Generate Presentation"
7. Download your PPTX file

### Command Line Interface

```bash
# Quick draft with fast model
python cli.py lesson_plan.txt -m dolphin_8b -n 10

# Professional presentation with premium model
python cli.py business_plan.txt -m dolphin_70b -n 15 -t modern

# Technical presentation with Hermes
python cli.py lecture_notes.txt -m hermes -n 20 -t education

# Custom output filename
python cli.py content.txt -m dolphin_70b -o quarterly_review.pptx
```

### List Available Models

```bash
python cli.py --list-models
```

## 🤖 Model Selection Guide

| Model | When to Use | Speed | Quality |
|-------|-------------|-------|---------|
| **Dolphin 8B** | Quick drafts, simple content, fast iterations | 5-10x faster | Good |
| **Dolphin 70B** | Professional presentations, business use | Standard | Premium |
| **Hermes** | Technical content, education, complex topics | Standard | Premium+ |

## 🎨 Available Themes

- **Modern Professional**: Clean, corporate look (default)
- **Dark Tech**: Dark background, tech-focused
- **Education Blue**: Friendly, educational style
- **Warm Earth**: Warm tones, creative presentations

## 📝 Input Format

Your input can be any text format:

- Lesson plans
- Lecture notes
- Meeting notes
- Project proposals
- Training materials
- Business plans
- Research summaries

**Example:**

```text
Introduction to Machine Learning

Topics:
- What is ML?
- Supervised vs Unsupervised Learning
- Neural Networks
- Applications
- Getting Started with ML

Key Points:
Machine learning is transforming industries...
```

## 🛠️ Configuration

Edit `config.yaml` to customize:

- Model names and descriptions
- Themes and colors
- Default settings
- Ollama connection

## 💡 Tips for Best Results

1. **Structure your content**: Use clear sections and bullet points
2. **Be specific**: Include key points you want covered
3. **Choose the right model**:
   - Dolphin 70B: General business/professional
   - Hermes: Technical/educational content
   - Dolphin 8B: Quick drafts
4. **Iterate**: Start with Dolphin 8B for speed, refine with Dolphin 70B

## 📊 Cost Comparison

| Solution | Cost | Your Setup |
|----------|------|------------|
| Gamma | $8-20/month | ✅ FREE |
| Presentations.AI | $20/month | ✅ FREE |
| Perceptis AI | $29/month | ✅ FREE |
| **Your Local Setup** | **$0/month** | 🎉 |

## 🔧 Troubleshooting

### "ollama: command not found"

Install Ollama from https://ollama.com

### "Connection refused to localhost:11434"

Make sure Ollama is running:
```bash
ollama serve
```

### Model not found

Pull your models:
```bash
ollama pull dolphin-llama3:8b
ollama pull dolphin-llama3:70b
ollama pull hermes3
```

### Generation is slow

- Use Dolphin 8B for faster results
- Close other applications using GPU/CPU
- Reduce number of slides

### Poor quality output

- Try Dolphin 70B or Hermes for better quality
- Provide more structured input
- Be more specific about what you want

## 📚 Project Structure

```
.
├── config.yaml                  # Configuration
├── presentation_generator.py    # Core generation engine
├── cli.py                       # Command-line interface
├── web_ui.py                    # Web interface
├── templates/
│   └── index.html              # Web UI template
├── requirements.txt             # Python dependencies
├── example_lesson_plan.txt     # Example input
└── README.md                    # This file
```

## 🚀 Advanced Usage

### Python API

```python
from presentation_generator import PresentationGenerator

generator = PresentationGenerator()

# Generate from text
result = generator.generate_from_text(
    content="Your content here...",
    model_key="dolphin_70b",
    num_slides=15,
    theme="modern",
    output_path="output.pptx"
)
```

### Custom Themes

Edit `config.yaml` to add your own themes with custom colors.

## 🤝 Contributing

This is your personal presentation tool! Feel free to modify and customize it to your needs.

## 📄 License

Free to use, modify, and distribute.

## 🎉 Get Started Now!

```bash
# Install dependencies
pip install -r requirements.txt

# Start web UI
python web_ui.py

# Or use CLI
python cli.py example_lesson_plan.txt
```

---

**Made with ❤️ for creating beautiful presentations without subscriptions or fees!**
