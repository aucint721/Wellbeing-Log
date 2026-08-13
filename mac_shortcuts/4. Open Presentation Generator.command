#!/bin/zsh
# Open the Presentation Generator desktop app.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
else
  echo "Setup is not done yet."
  echo "Double-click: 1. Setup Presentation Generator"
  echo ""
  read -k 1 "?Press any key to close..."
  exit 1
fi

if [ ! -f ".env" ] || ! grep -q "ANTHROPIC_API_KEY=." ".env" 2>/dev/null; then
  if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "No Claude API key found."
    echo "Double-click: 2. Set Claude API Key"
    echo ""
    echo "Continuing anyway in 3 seconds..."
    sleep 3
  fi
fi

exec python3 desktop_app.py
