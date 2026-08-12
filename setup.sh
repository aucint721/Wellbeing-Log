#!/bin/bash

echo "========================================"
echo "AI Presentation Generator Setup"
echo "========================================"
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✓ Python found: $(python3 --version)"
echo ""

# Check Ollama
echo "Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found."
    echo "Please install from: https://ollama.com"
    exit 1
fi
echo "✓ Ollama found"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo ""

# Check if Ollama is running
echo "Checking if Ollama is running..."
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "✓ Ollama is running"
else
    echo "⚠️  Ollama is not running. Start it with: ollama serve"
fi
echo ""

# Check for models
echo "Checking for required models..."
models=("dolphin-llama3:8b" "dolphin-llama3:70b" "hermes3")
missing_models=()

for model in "${models[@]}"; do
    if ollama list | grep -q "$model"; then
        echo "✓ Found: $model"
    else
        echo "❌ Missing: $model"
        missing_models+=("$model")
    fi
done
echo ""

if [ ${#missing_models[@]} -gt 0 ]; then
    echo "To install missing models, run:"
    for model in "${missing_models[@]}"; do
        echo "  ollama pull $model"
    done
    echo ""
fi

# Create outputs directory
mkdir -p outputs
echo "✓ Created outputs directory"
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Quick Start:"
echo "  Web UI:  python web_ui.py"
echo "  CLI:     python cli.py example_lesson_plan.txt"
echo ""
echo "See QUICKSTART.md or README.md for details"
