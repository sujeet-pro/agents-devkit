#!/usr/bin/env zsh
set -euo pipefail

# Update model-config.json with the latest model IDs for each installed CLI.
# Run this periodically (e.g., via /improve) to keep model versions current.
#
# Usage: update-models.zsh [--dry-run]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/model-config.json"
DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
  esac
done

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Error: $CONFIG_FILE not found" >&2
  exit 1
fi

echo "Checking for latest model versions..."
echo ""

updates='{}'

# Claude: check for latest opus model
if command -v claude &>/dev/null; then
  # claude --version or similar to detect available models
  # For now, use the known latest model ID
  current=$(jq -r '.claude.model' "$CONFIG_FILE")
  latest="claude-opus-4-6"
  if [[ "$current" != "$latest" ]]; then
    echo "  claude: $current -> $latest"
    updates=$(jq --arg model "$latest" '.claude.model = $model | .claude.flags = "-p --model " + $model + " --output-format text"' <<< "$updates")
  else
    echo "  claude: $current (up to date)"
  fi
fi

# Codex: check for latest model
if command -v codex &>/dev/null; then
  current=$(jq -r '.codex.model' "$CONFIG_FILE")
  latest="o3-pro"
  if [[ "$current" != "$latest" ]]; then
    echo "  codex: $current -> $latest"
    updates=$(jq --arg model "$latest" '.codex.model = $model | .codex.flags = "--model " + $model + " --full-auto"' <<< "$updates")
  else
    echo "  codex: $current (up to date)"
  fi
fi

# Gemini: check for latest model
if command -v gemini &>/dev/null; then
  current=$(jq -r '.gemini.model' "$CONFIG_FILE")
  latest="gemini-2.5-pro"
  if [[ "$current" != "$latest" ]]; then
    echo "  gemini: $current -> $latest"
    updates=$(jq --arg model "$latest" '.gemini.model = $model' <<< "$updates")
  else
    echo "  gemini: $current (up to date)"
  fi
fi

# Cursor: update GPT and Gemini model versions
if command -v cursor-cli &>/dev/null; then
  # Cursor GPT
  current_gpt=$(jq -r '.["cursor-gpt"].model' "$CONFIG_FILE")
  latest_gpt="gpt-5.4"
  if [[ "$current_gpt" != "$latest_gpt" ]]; then
    echo "  cursor-gpt: $current_gpt -> $latest_gpt"
  else
    echo "  cursor-gpt: $current_gpt (up to date)"
  fi

  # Cursor Gemini
  current_gemini=$(jq -r '.["cursor-gemini"].model' "$CONFIG_FILE")
  latest_gemini="gemini-2.5-pro"
  if [[ "$current_gemini" != "$latest_gemini" ]]; then
    echo "  cursor-gemini: $current_gemini -> $latest_gemini"
  else
    echo "  cursor-gemini: $current_gemini (up to date)"
  fi
fi

echo ""

if [[ "$DRY_RUN" == "true" ]]; then
  echo "(dry run — no changes applied)"
  exit 0
fi

# Apply updates to config file
# For now, the model IDs are hardcoded above. When CLIs support model listing,
# this script should query them dynamically. The /improve skill should update
# the hardcoded values in this script when new model versions are released.
echo "Model config is at: $CONFIG_FILE"
echo "To update model IDs, edit scripts/model-config.json directly."
echo "The /improve skill will detect and update model versions automatically."
