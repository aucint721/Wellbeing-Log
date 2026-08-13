#!/bin/zsh
# One-time helper: copies a double-click launcher to your Desktop.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Desktop/Presentation Generator.command"

cat > "$DEST" <<EOF
#!/bin/zsh
set -e
cd "$ROOT"
if [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"
fi
python3 desktop_app.py
EOF

chmod +x "$DEST"
chmod +x "$ROOT/Launch Presentation Generator.command" 2>/dev/null || true
chmod +x "$ROOT/desktop_app.py" 2>/dev/null || true

echo ""
echo "Desktop shortcut created:"
echo "  $DEST"
echo ""
echo "Double-click \"Presentation Generator\" on your Desktop to open the app."
echo "If macOS blocks it: right-click → Open → Open."
echo ""
