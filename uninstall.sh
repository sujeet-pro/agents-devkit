#!/usr/bin/env bash
set -euo pipefail

# claude-devkit uninstaller
# Removes items installed by install.sh, using the manifest for tracking.

CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
MANIFEST_FILE="$CLAUDE_DIR/.devkit-manifest"

# ---------------------------------------------------------------------------
# Check for manifest
# ---------------------------------------------------------------------------
if [[ ! -f "$MANIFEST_FILE" ]]; then
  echo "No devkit manifest found at $MANIFEST_FILE"
  echo "Nothing to uninstall — either the devkit was never installed or the manifest was removed."
  exit 0
fi

# ---------------------------------------------------------------------------
# Read manifest
# ---------------------------------------------------------------------------
ITEMS=()
while IFS= read -r line; do
  # Skip comments and blank lines
  [[ "$line" =~ ^#.*$ ]] && continue
  [[ -z "$line" ]] && continue
  ITEMS+=("$line")
done < "$MANIFEST_FILE"

if [[ ${#ITEMS[@]} -eq 0 ]]; then
  echo "Manifest is empty — nothing to uninstall."
  rm "$MANIFEST_FILE"
  exit 0
fi

# ---------------------------------------------------------------------------
# Confirm
# ---------------------------------------------------------------------------
echo "========================================"
echo "  claude-devkit uninstaller"
echo "========================================"
echo ""
echo "The following ${#ITEMS[@]} item(s) will be removed:"
echo ""
for item in "${ITEMS[@]}"; do
  if [[ -L "$item" ]]; then
    echo "  [symlink] $item"
  elif [[ -d "$item" ]]; then
    echo "  [dir]     $item"
  elif [[ -f "$item" ]]; then
    echo "  [file]    $item"
  else
    echo "  [missing] $item"
  fi
done
echo ""

# Support non-interactive mode via --yes flag
AUTO_CONFIRM=false
for arg in "$@"; do
  case "$arg" in
    --yes|-y)
      AUTO_CONFIRM=true
      ;;
  esac
done

if [[ "$AUTO_CONFIRM" != "true" ]]; then
  read -rp "Proceed with uninstall? [y/N] " confirm
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
  fi
fi

# ---------------------------------------------------------------------------
# Remove items
# ---------------------------------------------------------------------------
removed=0
skipped=0

for item in "${ITEMS[@]}"; do
  if [[ -L "$item" ]]; then
    rm "$item"
    echo "  Removed symlink: $item"
    removed=$((removed + 1))
  elif [[ -d "$item" ]]; then
    rm -rf "$item"
    echo "  Removed directory: $item"
    removed=$((removed + 1))
  elif [[ -f "$item" ]]; then
    rm "$item"
    echo "  Removed file: $item"
    removed=$((removed + 1))
  else
    echo "  Skipped (not found): $item"
    skipped=$((skipped + 1))
  fi
done

# ---------------------------------------------------------------------------
# Clean up empty directories
# ---------------------------------------------------------------------------
for dir in "$CLAUDE_DIR/skills" "$CLAUDE_DIR/agents" "$CLAUDE_DIR/guidelines" "$CLAUDE_DIR/profiles"; do
  if [[ -d "$dir" ]] && [[ -z "$(ls -A "$dir" 2>/dev/null)" ]]; then
    rmdir "$dir"
    echo "  Removed empty directory: $dir"
  fi
done

# ---------------------------------------------------------------------------
# Remove manifest
# ---------------------------------------------------------------------------
rm "$MANIFEST_FILE"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "========================================"
echo "  Uninstall complete"
echo "========================================"
echo ""
echo "Removed: $removed item(s)"
echo "Skipped: $skipped item(s) (not found)"
echo "Manifest removed."
