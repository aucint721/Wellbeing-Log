#!/bin/zsh
# Install / refresh all Presentation Generator shortcuts on the Desktop.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
DESKTOP="$HOME/Desktop"

mkdir -p "$DESKTOP"

write_cmd() {
  local name="$1"
  local body="$2"
  local dest="$DESKTOP/$name"
  print -r -- "$body" > "$dest"
  chmod +x "$dest"
  echo "  ✓ $dest"
}

# --- 1. Setup ---
write_cmd "1. Setup Presentation Generator.command" "#!/bin/zsh
set -e
ROOT=\"$ROOT\"
cd \"\$ROOT\"
echo \"========================================\"
echo \" Presentation Generator — Setup\"
echo \"========================================\"
echo \"Folder: \$ROOT\"
echo \"\"
if ! command -v python3 >/dev/null 2>&1; then
  echo \"Python 3 is not installed.\"
  echo \"Install from https://www.python.org/downloads/ or: xcode-select --install\"
  echo \"\"
  read -k 1 \"?Press any key to close...\"
  exit 1
fi
echo \"Python: \$(python3 --version)\"
echo \"\"
if [ ! -d \"venv\" ] && [ ! -d \".venv\" ]; then
  echo \"Creating virtual environment (venv)...\"
  python3 -m venv venv
fi
if [ -f \"venv/bin/activate\" ]; then
  source \"venv/bin/activate\"
elif [ -f \".venv/bin/activate\" ]; then
  source \".venv/bin/activate\"
fi
echo \"Installing / updating packages...\"
python -m pip install --upgrade pip
pip install -r requirements.txt
\"\$ROOT/install_desktop_shortcuts.sh\"
echo \"\"
echo \"✓ Setup complete.\"
echo \"Next: 2. Set Claude API Key, then 4. Open Presentation Generator.\"
echo \"\"
read -k 1 \"?Press any key to close...\"
"

# --- 2. API key ---
write_cmd "2. Set Claude API Key.command" "#!/bin/zsh
set -e
ROOT=\"$ROOT\"
cd \"\$ROOT\"
ENV_FILE=\"\$ROOT/.env\"
echo \"========================================\"
echo \" Presentation Generator — Claude API Key\"
echo \"========================================\"
echo \"Folder: \$ROOT\"
echo \"\"
echo \"Get a key at: https://console.anthropic.com/\"
echo \"\"
echo \"Easiest way on Mac:\"
echo \"  1) Copy the key (Cmd+C)\"
echo \"  2) Come back here and press Enter\"
echo \"  (Reads from clipboard — no Terminal paste needed.)\"
echo \"\"
if [ -f \"\$ENV_FILE\" ] && grep -q \"ANTHROPIC_API_KEY=\" \"\$ENV_FILE\" 2>/dev/null; then
  echo \"A key is already saved in .env\"
  echo -n \"Replace it? [y/N] \"
  read ans
  if [[ ! \"\$ans\" =~ ^[Yy]\$ ]]; then
    echo \"Keeping existing key.\"
    echo \"\"
    echo -n \"Press Enter to close...\"
    read
    exit 0
  fi
  echo \"\"
fi
KEY=\"\"
if command -v pbpaste >/dev/null 2>&1; then
  echo -n \"Press Enter to use the key currently on your clipboard...\"
  read
  KEY=\"\$(pbpaste | tr -d '\\r\\n' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*\$//')\"
fi
if [ -z \"\$KEY\" ]; then
  echo \"\"
  echo \"Clipboard was empty. Paste the key below (Cmd+V), then press Enter.\"
  echo \"(You will be able to see what you paste.)\"
  echo -n \"ANTHROPIC_API_KEY: \"
  read KEY
  KEY=\"\$(print -r -- \"\$KEY\" | tr -d '\\r\\n' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*\$//')\"
fi
if [ -z \"\$KEY\" ]; then
  echo \"No key found — nothing saved.\"
  echo \"\"
  echo -n \"Press Enter to close...\"
  read
  exit 1
fi
if [[ ! \"\$KEY\" == sk-ant-* ]]; then
  echo \"\"
  echo \"Warning: keys usually start with sk-ant-\"
  echo -n \"Save this value anyway? [y/N] \"
  read ans
  if [[ ! \"\$ans\" =~ ^[Yy]\$ ]]; then
    echo \"Cancelled.\"
    echo \"\"
    echo -n \"Press Enter to close...\"
    read
    exit 1
  fi
fi
TMP=\"\$(mktemp)\"
if [ -f \"\$ENV_FILE\" ]; then
  grep -v '^ANTHROPIC_API_KEY=' \"\$ENV_FILE\" > \"\$TMP\" || true
fi
printf 'ANTHROPIC_API_KEY=%s\\n' \"\$KEY\" >> \"\$TMP\"
mv \"\$TMP\" \"\$ENV_FILE\"
chmod 600 \"\$ENV_FILE\"
LAST4=\"\${KEY[-4,-1]}\"
echo \"\"
echo \"✓ Saved to \$ENV_FILE\"
echo \"  (ends with …\$LAST4)\"
echo \"\"
echo -n \"Press Enter to close...\"
read
"

# --- 3. Update ---
write_cmd "3. Update Presentation Generator.command" "#!/bin/zsh
set -e
ROOT=\"$ROOT\"
cd \"\$ROOT\"
echo \"========================================\"
echo \" Presentation Generator — Update\"
echo \"========================================\"
echo \"Folder: \$ROOT\"
echo \"\"
if [ -d \".git\" ]; then
  echo \"Fetching latest from GitHub...\"
  git fetch origin
  git checkout main
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    git reset --hard origin/main
  else
    git pull origin main
  fi
  echo \"✓ Code updated to latest main\"
else
  echo \"Not a git folder — skipped code update.\"
fi
if [ -f \"venv/bin/activate\" ]; then
  source \"venv/bin/activate\"
elif [ -f \".venv/bin/activate\" ]; then
  source \".venv/bin/activate\"
else
  echo \"No venv yet — run 1. Setup Presentation Generator first.\"
  echo \"\"
  read -k 1 \"?Press any key to close...\"
  exit 1
fi
echo \"\"
echo \"Refreshing Python packages...\"
pip install -r requirements.txt
\"\$ROOT/install_desktop_shortcuts.sh\"
echo \"\"
echo \"✓ Update complete.\"
echo \"\"
read -k 1 \"?Press any key to close...\"
"

# --- 4. Open ---
write_cmd "4. Open Presentation Generator.command" "#!/bin/zsh
set -e
ROOT=\"$ROOT\"
cd \"\$ROOT\"
if [ -f \"venv/bin/activate\" ]; then
  source \"venv/bin/activate\"
elif [ -f \".venv/bin/activate\" ]; then
  source \".venv/bin/activate\"
else
  echo \"Setup is not done yet.\"
  echo \"Double-click: 1. Setup Presentation Generator\"
  echo \"\"
  read -k 1 \"?Press any key to close...\"
  exit 1
fi
if [ ! -f \".env\" ] || ! grep -q \"ANTHROPIC_API_KEY=.\" \".env\" 2>/dev/null; then
  if [ -z \"\$ANTHROPIC_API_KEY\" ]; then
    echo \"No Claude API key found.\"
    echo \"Double-click: 2. Set Claude API Key\"
    echo \"\"
    echo \"Continuing anyway in 3 seconds...\"
    sleep 3
  fi
fi
exec python3 desktop_app.py
"

# Also keep the older single-name launcher for convenience
write_cmd "Presentation Generator.command" "#!/bin/zsh
set -e
ROOT=\"$ROOT\"
cd \"\$ROOT\"
if [ -f \"venv/bin/activate\" ]; then
  source \"venv/bin/activate\"
elif [ -f \".venv/bin/activate\" ]; then
  source \".venv/bin/activate\"
fi
exec python3 desktop_app.py
"

# Make in-repo helpers executable
chmod +x "$ROOT"/mac_shortcuts/*.command 2>/dev/null || true
chmod +x "$ROOT/Launch Presentation Generator.command" 2>/dev/null || true
chmod +x "$ROOT/desktop_app.py" 2>/dev/null || true
chmod +x "$ROOT/install_desktop_shortcuts.sh" 2>/dev/null || true

echo ""
echo "Desktop shortcuts ready in:"
echo "  $DESKTOP"
echo ""
echo "Use in order the first time:"
echo "  1. Setup Presentation Generator"
echo "  2. Set Claude API Key"
echo "  4. Open Presentation Generator"
echo ""
echo "Later: 3. Update Presentation Generator"
echo "If macOS blocks a shortcut: right-click → Open → Open."
echo ""
