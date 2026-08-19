#!/bin/bash
# Certificate Generator - Show Available Themes and Help

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
echo "       CERTIFICATE GENERATOR - HELP & THEMES"
echo "============================================================"
echo ""

python3 certificate_generator.py --list-themes

echo ""
echo "============================================================"
echo "QUICK EXAMPLES:"
echo "============================================================"
echo ""
echo "Interactive mode (easiest):"
echo "  python3 certificate_generator.py"
echo ""
echo "Create a blank template:"
echo "  python3 certificate_generator.py -o my_certificate.pptx"
echo ""
echo "Create with specific name:"
echo "  python3 certificate_generator.py -n \"Sarah Johnson\" -d \"August 2026\" -s \"Jane Smith\""
echo ""
echo "Use a different theme:"
echo "  python3 certificate_generator.py --theme education"
echo ""
echo "============================================================"
echo ""
echo "For full documentation, see CERTIFICATE_USAGE.md"
echo ""
read -p "Press Enter to close..."
