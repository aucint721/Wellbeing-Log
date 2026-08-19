#!/bin/bash
# Certificate Generator - Interactive Mode
# Double-click this file to create teacher aide certificates

# Find the Wellbeing-Log directory
if [ -d "$HOME/Desktop/Wellbeing-Log" ]; then
    cd "$HOME/Desktop/Wellbeing-Log"
elif [ -d "$HOME/Documents/Wellbeing-Log" ]; then
    cd "$HOME/Documents/Wellbeing-Log"
elif [ -d "$(dirname "$0")/.." ]; then
    cd "$(dirname "$0")/.."
else
    echo "❌ Error: Could not find Wellbeing-Log folder."
    echo "Please make sure it's in ~/Desktop/Wellbeing-Log or ~/Documents/Wellbeing-Log"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

echo "============================================================"
echo "       TEACHER AIDE CERTIFICATE GENERATOR"
echo "============================================================"
echo ""
echo "This will create a professional certificate with your school logo placeholder."
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "📦 Installing required packages..."
    pip3 install --user -r requirements.txt
    echo ""
fi

# Run the certificate generator in interactive mode
python3 certificate_generator.py

echo ""
echo "============================================================"
echo "✓ Done! Open the .pptx file to add your school logo."
echo "============================================================"
echo ""
read -p "Press Enter to close..."
