#!/bin/zsh
# Double-click from the project’s mac_shortcuts folder (or use the Desktop copy).
# Creates venv and installs Python packages (one-time / repair).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "========================================"
echo " Presentation Generator — Setup"
echo "========================================"
echo "Folder: $ROOT"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed."
  echo "Install from https://www.python.org/downloads/ or run:"
  echo "  xcode-select --install"
  echo ""
  read -k 1 "?Press any key to close..."
  exit 1
fi

echo "Python: $(python3 --version)"
echo ""

if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
  echo "Creating virtual environment (venv)..."
  python3 -m venv venv
fi

if [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

echo "Installing / updating packages..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Creating Desktop shortcuts..."
"$ROOT/install_desktop_shortcuts.sh"

echo ""
echo "✓ Setup complete."
echo "Next on your Desktop:"
echo "  2. Set Claude API Key"
echo "  4. Open Presentation Generator"
echo ""
read -k 1 "?Press any key to close..."
