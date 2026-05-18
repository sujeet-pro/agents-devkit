#!/usr/bin/env bash
# install.sh — adk v3 installer (thin wrapper around install.py)
#
# Usage:
#   ./install.sh                      # autodetect installed agents, install for all detected
#   ./install.sh --target claude
#   ./install.sh --target claude,cursor
#   ./install.sh --target all         # try every supported agent
#   ./install.sh --uninstall          # remove by marker; leave overrides intact
#   ./install.sh --dry-run            # show what would change

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required (brew install python@3.12)" >&2
  exit 1
fi

exec python3 "$HERE/install.py" --repo-root "$HERE" "$@"
