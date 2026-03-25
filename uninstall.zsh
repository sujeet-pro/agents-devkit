#!/usr/bin/env zsh
set -euo pipefail

# agents-devkit uninstaller
# Removes symlinks created by install.zsh and managed MCP servers from ~/.claude.json.
# Does NOT touch non-symlinked items (e.g. skills installed via /plugin).

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
echo "  agents-devkit uninstaller"
echo "========================================"
echo ""
echo "The following ${#ITEMS[@]} item(s) will be removed:"
echo ""
for item in "${ITEMS[@]}"; do
  if [[ "$item" == mcp:* ]]; then
    echo "  [mcp]     ${item#mcp:} (in ~/.claude.json)"
  elif [[ -L "$item" ]]; then
    echo "  [symlink] $item"
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
# Remove symlinks
# ---------------------------------------------------------------------------
removed=0
skipped=0

for item in "${ITEMS[@]}"; do
  [[ "$item" == mcp:* ]] && continue

  if [[ -L "$item" ]]; then
    rm "$item"
    echo "  Removed symlink: $item"
    removed=$((removed + 1))
  else
    echo "  Skipped (not a symlink or not found): $item"
    skipped=$((skipped + 1))
  fi
done

# ---------------------------------------------------------------------------
# Remove managed MCP servers from ~/.claude.json
# ---------------------------------------------------------------------------
CLAUDE_JSON_TARGET="$HOME/.claude.json"
MCP_SERVERS_TO_REMOVE=()

for item in "${ITEMS[@]}"; do
  if [[ "$item" == mcp:* ]]; then
    MCP_SERVERS_TO_REMOVE+=("${item#mcp:}")
  fi
done

if [[ ${#MCP_SERVERS_TO_REMOVE[@]} -gt 0 && -f "$CLAUDE_JSON_TARGET" ]]; then
  echo ""
  echo "Removing managed MCP servers from $CLAUDE_JSON_TARGET:"

  for server_name in "${MCP_SERVERS_TO_REMOVE[@]}"; do
    if jq -e ".mcpServers.\"$server_name\"" "$CLAUDE_JSON_TARGET" &>/dev/null; then
      tmp="$(jq "del(.mcpServers.\"$server_name\")" "$CLAUDE_JSON_TARGET")"
      tmp_file="$(mktemp)"
      echo "$tmp" > "$tmp_file"
      mv "$tmp_file" "$CLAUDE_JSON_TARGET"
      echo "  Removed MCP server: $server_name"
      removed=$((removed + 1))
    else
      echo "  Skipped MCP server (not found): $server_name"
      skipped=$((skipped + 1))
    fi
  done
fi

# ---------------------------------------------------------------------------
# Clean up empty directories
# ---------------------------------------------------------------------------
for dir in "$CLAUDE_DIR/skills" "$CLAUDE_DIR/agents" "$CLAUDE_DIR/guidelines" "$CLAUDE_DIR/profiles" "$CLAUDE_DIR/scripts"; do
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
echo "Skipped: $skipped item(s)"
echo "Manifest removed."
echo ""
echo "Note: Skills installed via /plugin are not affected."
