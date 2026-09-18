#!/bin/zsh
# Open the PRAL food-acidity checker.
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

exec python3 desktop_pral.py
