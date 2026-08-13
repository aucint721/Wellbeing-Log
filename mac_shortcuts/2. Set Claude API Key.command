#!/bin/zsh
# Prompt for Anthropic API key and save to project .env
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ENV_FILE="$ROOT/.env"

echo "========================================"
echo " Presentation Generator — Claude API Key"
echo "========================================"
echo "Folder: $ROOT"
echo ""
echo "Get a key at: https://console.anthropic.com/"
echo "(Stored only in this Mac's .env file — not uploaded anywhere by this script.)"
echo ""

if [ -f "$ENV_FILE" ] && grep -q "ANTHROPIC_API_KEY=" "$ENV_FILE" 2>/dev/null; then
  echo "A key is already saved in .env"
  echo -n "Replace it? [y/N] "
  read ans
  if [[ ! "$ans" =~ ^[Yy]$ ]]; then
    echo "Keeping existing key."
    echo ""
    read -k 1 "?Press any key to close..."
    exit 0
  fi
fi

echo -n "Paste ANTHROPIC_API_KEY: "
read -s KEY
echo ""

if [ -z "$KEY" ]; then
  echo "No key entered — nothing saved."
  echo ""
  read -k 1 "?Press any key to close..."
  exit 1
fi

TMP="$(mktemp)"
if [ -f "$ENV_FILE" ]; then
  grep -v '^ANTHROPIC_API_KEY=' "$ENV_FILE" > "$TMP" || true
fi
echo "ANTHROPIC_API_KEY=$KEY" >> "$TMP"
mv "$TMP" "$ENV_FILE"
chmod 600 "$ENV_FILE"

echo ""
echo "✓ Saved to $ENV_FILE"
echo "You can now open the Presentation Generator."
echo ""
read -k 1 "?Press any key to close..."
