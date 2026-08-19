#!/bin/bash
# Certificate Generator - Interactive Mode
# Double-click this file to create teacher aide certificates

cd "$(dirname "$0")/.."

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
