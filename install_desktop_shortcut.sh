#!/bin/zsh
# Back-compat wrapper — installs the full Desktop shortcut set.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$ROOT/install_desktop_shortcuts.sh"
