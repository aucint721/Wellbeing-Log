#!/bin/bash
# Certificate Generator - Show Available Themes and Help

cd "$(dirname "$0")/.."

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
