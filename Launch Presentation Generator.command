#!/bin/zsh
# Double-click this file in the project folder to open the app.
set -e
cd "$(dirname "$0")"

if [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"
fi

exec python3 desktop_app.py
