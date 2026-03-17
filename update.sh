#!/usr/bin/env bash
set -euo pipefail

# claude-devkit updater
# Updates the devkit and re-installs with the same mode.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVKIT_DIR="${CLAUDE_DEVKIT_DIR:-$SCRIPT_DIR}"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
MANIFEST_FILE="$CLAUDE_DIR/.devkit-manifest"

echo "========================================"
echo "  claude-devkit updater"
echo "========================================"
echo ""

# ---------------------------------------------------------------------------
# Detect current install mode from manifest
# ---------------------------------------------------------------------------
MODE="remote"

if [[ -f "$MANIFEST_FILE" ]]; then
  manifest_mode="$(grep '^# mode=' "$MANIFEST_FILE" | head -1 | sed 's/^# mode=//')"
  if [[ -n "$manifest_mode" ]]; then
    MODE="$manifest_mode"
  fi
  echo "Detected install mode from manifest: $MODE"
else
  echo "No manifest found — assuming remote mode."
fi

# Allow override via argument
for arg in "$@"; do
  case "$arg" in
    --mode=*)
      MODE="${arg#--mode=}"
      echo "Mode overridden to: $MODE"
      ;;
    --help|-h)
      echo "Usage: update.sh [--mode=remote|dev]"
      echo ""
      echo "Updates the devkit to the latest version and re-installs."
      echo "Mode is auto-detected from the manifest unless overridden."
      exit 0
      ;;
  esac
done

echo ""

# ---------------------------------------------------------------------------
# Update source
# ---------------------------------------------------------------------------
if [[ "$MODE" == "dev" ]]; then
  echo "Dev mode — pulling latest changes in $DEVKIT_DIR ..."
  echo ""

  if [[ -d "$DEVKIT_DIR/.git" ]]; then
    cd "$DEVKIT_DIR"
    git pull --ff-only
    echo ""
    echo "Source updated. Symlinks are already pointing to the repo, so"
    echo "all changes are immediately available."
  else
    echo "Warning: $DEVKIT_DIR is not a git repository."
    echo "Cannot auto-update in dev mode without a git repo."
    echo "Please update the source manually and re-run install.sh --mode=dev"
    exit 1
  fi

  echo ""
  echo "========================================"
  echo "  Update complete (dev mode)"
  echo "========================================"

elif [[ "$MODE" == "remote" ]]; then
  echo "Remote mode — updating source and re-installing ..."
  echo ""

  if [[ -d "$DEVKIT_DIR/.git" ]]; then
    echo "Git repo detected at $DEVKIT_DIR — pulling latest ..."
    cd "$DEVKIT_DIR"
    git pull --ff-only
    echo ""
  else
    echo "Warning: $DEVKIT_DIR is not a git repository."
    echo "If you downloaded this as an archive, please download the latest"
    echo "version and re-run install.sh."
    exit 1
  fi

  echo "Re-running installer with --mode=remote ..."
  echo ""
  bash "$DEVKIT_DIR/install.sh" --mode=remote

  echo ""
  echo "========================================"
  echo "  Update complete (remote mode)"
  echo "========================================"

else
  echo "Error: unknown mode '$MODE'"
  exit 1
fi
