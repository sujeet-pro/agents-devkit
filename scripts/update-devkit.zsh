#!/usr/bin/env zsh
set -euo pipefail

# DevKit updater
# Updates the DevKit installation from GitHub (default) or a local filesystem path.
#
# Usage:
#   zsh scripts/update-devkit.zsh                     # pull from GitHub
#   zsh scripts/update-devkit.zsh --fs /path/to/repo  # copy from local path
#   zsh scripts/update-devkit.zsh --dry-run            # preview only

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEVKIT_DIR="$(dirname "$SCRIPT_DIR")"

SOURCE="github"
FS_PATH=""
DRY_RUN=false

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --fs)
      SOURCE="fs"
      if [[ -n "${2:-}" ]]; then
        FS_PATH="$2"
        shift
      else
        echo "Error: --fs requires a path argument"
        exit 1
      fi
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --help|-h)
      cat <<'EOF'
Usage: update-devkit.zsh [--fs <path>] [--dry-run]

Update the DevKit installation with the latest skills, agents, and guidelines.

Options:
  --fs <path>    Copy from a local filesystem path instead of git pull
  --dry-run      Preview changes without applying
  --help         Show this help message

Examples:
  zsh scripts/update-devkit.zsh                              # GitHub update
  zsh scripts/update-devkit.zsh --fs ~/dev/agents-devkit     # Local filesystem
  zsh scripts/update-devkit.zsh --dry-run                    # Preview only
EOF
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Run with --help for usage."
      exit 1
      ;;
  esac
  shift
done

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
for cmd in git jq rsync; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: $cmd is required but not installed"
    exit 1
  fi
done

echo "========================================"
echo "  DevKit Updater"
echo "========================================"
echo ""
echo "Source:    $SOURCE"
echo "DevKit:   $DEVKIT_DIR"
echo "Dry run:  $DRY_RUN"
echo ""

# ---------------------------------------------------------------------------
# GitHub update
# ---------------------------------------------------------------------------
if [[ "$SOURCE" == "github" ]]; then
  echo "--- Git Pull ---"

  if [[ "$DRY_RUN" == "true" ]]; then
    cd "$DEVKIT_DIR"
    git fetch --quiet
    changes="$(git log HEAD..origin/main --oneline 2>/dev/null || echo '(no remote tracking branch)')"
    if [[ -z "$changes" ]]; then
      echo "  Already up to date."
    else
      echo "  Pending changes:"
      echo "$changes" | sed 's/^/    /'
    fi
  else
    cd "$DEVKIT_DIR"
    if ! git pull --ff-only 2>/dev/null; then
      echo "  Warning: fast-forward pull failed. You may have local modifications."
      echo "  Consider: git stash && git pull --ff-only && git stash pop"
      exit 1
    fi
    echo "  Done."
  fi
  echo ""
fi

# ---------------------------------------------------------------------------
# Filesystem update
# ---------------------------------------------------------------------------
if [[ "$SOURCE" == "fs" ]]; then
  echo "--- Filesystem Copy ---"

  if [[ -z "$FS_PATH" ]]; then
    echo "Error: --fs requires a path argument"
    exit 1
  fi

  if [[ ! -d "$FS_PATH" ]]; then
    echo "Error: path does not exist: $FS_PATH"
    exit 1
  fi

  if [[ ! -d "$FS_PATH/skills" || ! -d "$FS_PATH/agents" ]]; then
    echo "Error: path does not look like a DevKit repo (missing skills/ or agents/)"
    exit 1
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  Would copy from: $FS_PATH"
    rsync -an --exclude='.git' --exclude='node_modules' --exclude='.temp' --exclude='lib/node_modules' "$FS_PATH/" "$DEVKIT_DIR/" | head -50
    echo "  (dry-run, no changes applied)"
  else
    rsync -a --exclude='.git' --exclude='node_modules' --exclude='.temp' --exclude='lib/node_modules' "$FS_PATH/" "$DEVKIT_DIR/"
    echo "  Copied from $FS_PATH"
  fi
  echo ""
fi

# ---------------------------------------------------------------------------
# Sync upstream sources
# ---------------------------------------------------------------------------
if [[ "$DRY_RUN" == "false" ]]; then
  echo "--- Sync Upstream Sources ---"
  if [[ -f "$DEVKIT_DIR/scripts/sync-sources.zsh" ]]; then
    zsh "$DEVKIT_DIR/scripts/sync-sources.zsh" || echo "  Warning: sync-sources had errors (non-fatal)"
  else
    echo "  scripts/sync-sources.zsh not found — skipping"
  fi
  echo ""

  echo "--- Node.js Dependencies ---"
  if [[ -f "$DEVKIT_DIR/scripts/setup-node.zsh" ]]; then
    zsh "$DEVKIT_DIR/scripts/setup-node.zsh" || echo "  Warning: setup-node had errors (non-fatal)"
  else
    echo "  scripts/setup-node.zsh not found — skipping"
  fi
  echo ""

  echo "--- Re-install ---"
  zsh "$DEVKIT_DIR/install.zsh" --skip-checks
  echo ""
fi

echo "========================================"
echo "  Update complete"
echo "========================================"
