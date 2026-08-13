#!/bin/zsh
# Save Anthropic API key to project .env (clipboard-friendly on Mac).
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
echo ""
echo "Easiest way on Mac:"
echo "  1) Copy the key (Cmd+C)"
echo "  2) Come back here and press Enter"
echo "  (This reads from your clipboard — no Terminal paste needed.)"
echo ""

if [ -f "$ENV_FILE" ] && grep -q "ANTHROPIC_API_KEY=" "$ENV_FILE" 2>/dev/null; then
  echo "A key is already saved in .env"
  echo -n "Replace it? [y/N] "
  read ans
  if [[ ! "$ans" =~ ^[Yy]$ ]]; then
    echo "Keeping existing key."
    echo ""
    echo -n "Press Enter to close..."
    read
    exit 0
  fi
  echo ""
fi

KEY=""
if command -v pbpaste >/dev/null 2>&1; then
  echo -n "Press Enter to use the key currently on your clipboard..."
  read
  KEY="$(pbpaste | tr -d '\r\n' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
fi

if [ -z "$KEY" ]; then
  echo ""
  echo "Clipboard was empty (or paste unavailable)."
  echo "Paste the key below (Cmd+V), then press Enter."
  echo "(You will be able to see what you paste.)"
  echo -n "ANTHROPIC_API_KEY: "
  read KEY
  KEY="$(print -r -- "$KEY" | tr -d '\r\n' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
fi

if [ -z "$KEY" ]; then
  echo "No key found — nothing saved."
  echo ""
  echo -n "Press Enter to close..."
  read
  exit 1
fi

# Basic sanity check
if [[ ! "$KEY" == sk-ant-* ]]; then
  echo ""
  echo "Warning: keys usually start with sk-ant-"
  echo -n "Save this value anyway? [y/N] "
  read ans
  if [[ ! "$ans" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    echo ""
    echo -n "Press Enter to close..."
    read
    exit 1
  fi
fi

TMP="$(mktemp)"
if [ -f "$ENV_FILE" ]; then
  grep -v '^ANTHROPIC_API_KEY=' "$ENV_FILE" > "$TMP" || true
fi
# Avoid echoing the full key into shell history via print; write via printf
printf 'ANTHROPIC_API_KEY=%s\n' "$KEY" >> "$TMP"
mv "$TMP" "$ENV_FILE"
chmod 600 "$ENV_FILE"

LAST4="${KEY[-4,-1]}"
echo ""
echo "✓ Saved to $ENV_FILE"
echo "  (ends with …$LAST4)"
echo "You can now open the Presentation Generator."
echo ""
echo -n "Press Enter to close..."
read
