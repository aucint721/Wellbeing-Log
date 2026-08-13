#!/bin/zsh
# Pull latest code from GitHub and refresh Python packages.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "========================================"
echo " Presentation Generator — Update"
echo "========================================"
echo "Folder: $ROOT"
echo ""

if [ -d ".git" ]; then
  echo "Fetching latest from GitHub..."
  git fetch origin
  git checkout main
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    git reset --hard origin/main
  else
    git pull origin main
  fi
  echo "✓ Code updated to latest main"
else
  echo "Not a git folder — skipped code update."
  echo "Tip: clone from GitHub so Update can pull new features."
fi

if [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
else
  echo "No venv yet — run \"1. Setup Presentation Generator\" first."
  echo ""
  read -k 1 "?Press any key to close..."
  exit 1
fi

echo ""
echo "Refreshing Python packages..."
pip install -r requirements.txt

"$ROOT/install_desktop_shortcuts.sh"

echo ""
echo "✓ Update complete."
echo ""
read -k 1 "?Press any key to close..."
