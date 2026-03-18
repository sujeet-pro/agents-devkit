#!/usr/bin/env zsh
set -euo pipefail

# Detect available AI CLI tools and output JSON manifest of available models.
# Reads model IDs from scripts/model-config.json.
# Used by the /multi skill for multi-model orchestration.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/model-config.json"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo '{"available_models":[],"count":0,"multi_model_available":false,"error":"model-config.json not found"}' 1>&2
  exit 1
fi

models='[]'
has_claude=false

add_model() {
  local name="$1"
  models=$(jq --arg name "$name" \
    --argjson entry "$(jq --arg n "$name" '.[$n]' "$CONFIG_FILE")" \
    '. + [{"name": $name} + $entry]' <<< "$models")
}

# Claude Code CLI
if command -v claude &>/dev/null; then
  has_claude=true
  add_model "claude"
fi

# OpenAI Codex CLI
if command -v codex &>/dev/null; then
  add_model "codex"
fi

# Google Gemini CLI
if command -v gemini &>/dev/null; then
  add_model "gemini"
fi

# Cursor CLI — expands to multiple model entries
if command -v cursor-cli &>/dev/null; then
  add_model "cursor-gpt"
  add_model "cursor-gemini"
fi

count=$(jq 'length' <<< "$models")

jq -n \
  --argjson models "$models" \
  --argjson count "$count" \
  '{
    "available_models": $models,
    "count": $count,
    "multi_model_available": ($count >= 2)
  }'
