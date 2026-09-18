#!/bin/zsh
# Double-click this file in the project folder to open the PRAL checker.
set -e
cd "$(dirname "$0")"

if [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "This Mac has no python3 (there is usually no \`python\` command either)."
  echo "Double-click: 1. Setup Presentation Generator"
  echo "Or run: xcode-select --install"
  echo ""
  read -k 1 "?Press any key to close..."
  exit 1
fi

exec python3 desktop_pral.py
