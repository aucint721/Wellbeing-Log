#!/bin/zsh
# Double-click this file (or the Desktop copy) to launch the app.
set -e
cd "$(dirname "$0")"

# Prefer project venv if present
if [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"
fi

# Optional: load key from .env automatically via python-dotenv in desktop_app.py
# Or export it in ~/.zshrc once.

python3 desktop_app.py
