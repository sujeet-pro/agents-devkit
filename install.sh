#!/usr/bin/env bash
# install.sh — adk installer (thin wrapper around install.py)
#
# Usage:
#   ./install.sh                      # autodetect installed agents, install for all detected
#   ./install.sh --target claude
#   ./install.sh --target claude,cursor
#   ./install.sh --target all         # try every supported agent
#   ./install.sh --uninstall          # remove by marker; leave overrides intact
#   ./install.sh --dry-run            # show what would change
#   ./install.sh --interactive        # textual TUI (if installed) / plain prompt fallback
#
# Normal installs enforce an ADK-only agent profile: non-ADK agent
# integrations/caches are removed, legacy ADK state is quarantined, and fresh
# ADK skills/agents/MCPs are regenerated from this repo.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required (brew install python@3.12)" >&2
  exit 1
fi

# --interactive routes through install_tui.py; everything else through install.py.
for arg in "$@"; do
  if [ "$arg" = "--interactive" ]; then
    exec python3 "$HERE/install_tui.py" --repo-root "$HERE"
  fi
done

exec python3 "$HERE/install.py" --repo-root "$HERE" "$@"
