#!/bin/bash
# Install Certificate Generator shortcuts to Mac Desktop

echo "Installing Certificate Generator shortcuts to Desktop..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP="$HOME/Desktop"

if [ ! -d "$DESKTOP" ]; then
    echo "❌ Desktop folder not found at $DESKTOP"
    exit 1
fi

# Copy shortcuts to Desktop
cp "$SCRIPT_DIR/mac_shortcuts/5_create_certificate.command" "$DESKTOP/"
cp "$SCRIPT_DIR/mac_shortcuts/6_certificate_help.command" "$DESKTOP/"

# Make them executable
chmod +x "$DESKTOP/5_create_certificate.command"
chmod +x "$DESKTOP/6_certificate_help.command"

echo "✓ Installed to Desktop:"
echo "  • 5_create_certificate.command - Double-click to create certificates"
echo "  • 6_certificate_help.command - Double-click to see available themes"
echo ""
echo "Double-click these files on your Desktop to use them!"
