# 🚀 Quick Start Guide

Get your AI presentation generator running in 3 minutes!

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `python-pptx` - Creates PowerPoint files
- `flask` - Web interface
- `requests` - Talks to Ollama
- `pyyaml` - Configuration

## Step 2: Verify Ollama is Running

```bash
# Check if Ollama is running
ollama list
```

**If you get an error**, start Ollama:
```bash
ollama serve
```

**Verify your models are available:**
```bash
ollama list
```

You should see:
- `dolphin-llama3:8b`
- `dolphin-llama3:70b`
- `hermes3` (or similar)

**If models are missing**, pull them:
```bash
ollama pull dolphin-llama3:8b
ollama pull dolphin-llama3:70b
ollama pull hermes3
```

## Step 3: Choose Your Interface

### Option A: Web Interface (Easiest!)

```bash
python web_ui.py
```

Then open: **http://localhost:5000**

### Option B: Command Line

```bash
# Try the example
python cli.py example_lesson_plan.txt

# Use your own file
python cli.py my_content.txt -m dolphin_70b -n 15
```

## 🎉 That's It!

You now have a FREE presentation generator that rivals $20-30/month services!

## 🆘 Troubleshooting

### Problem: "ModuleNotFoundError"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Problem: "Connection refused to localhost:11434"
**Solution:** Start Ollama: `ollama serve`

### Problem: "Model not found"
**Solution:** Pull the model: `ollama pull dolphin-llama3:70b`

### Problem: Slow generation
**Solution:** Use Dolphin 8B instead: `-m dolphin_8b`

## 📖 Next Steps

- Read the full README.md for advanced usage
- Edit config.yaml to customize themes
- Create presentations from your lesson plans!

## 💡 Quick Tips

1. **Start fast**: Use Dolphin 8B to test, then use Dolphin 70B for final
2. **Structure matters**: Clear sections = better presentations
3. **Choose right model**: 
   - Business → Dolphin 70B
   - Technical → Hermes
   - Quick draft → Dolphin 8B

---

**Need help?** Check README.md or the built-in help:
```bash
python cli.py --help
```
