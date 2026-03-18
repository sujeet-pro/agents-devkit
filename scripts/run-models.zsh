#!/usr/bin/env zsh
set -euo pipefail

# Run a prompt against multiple AI CLI tools in parallel.
# Outputs go to individual files in the specified directory.
# Returns JSON summary of results.
#
# Usage: run-models.zsh --prompt-file <file> --output-dir <dir> --models <json> [--timeout <secs>]

PROMPT_FILE=""
OUTPUT_DIR=""
MODELS_JSON=""
TIMEOUT="300"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt-file) PROMPT_FILE="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --models) MODELS_JSON="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$PROMPT_FILE" || -z "$OUTPUT_DIR" || -z "$MODELS_JSON" ]]; then
  echo "Usage: run-models.zsh --prompt-file <file> --output-dir <dir> --models <json>" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
PROMPT="$(cat "$PROMPT_FILE")"
PIDS=()
MODEL_NAMES=()

count=$(jq 'length' <<< "$MODELS_JSON")

for i in $(seq 0 $((count - 1))); do
  name=$(jq -r ".[$i].name" <<< "$MODELS_JSON")
  cmd=$(jq -r ".[$i].cmd" <<< "$MODELS_JSON")
  flags=$(jq -r ".[$i].flags // \"\"" <<< "$MODELS_JSON")
  input_mode=$(jq -r ".[$i].input_mode // \"arg\"" <<< "$MODELS_JSON")

  output_file="$OUTPUT_DIR/${name}.md"
  status_file="$OUTPUT_DIR/${name}.status"

  MODEL_NAMES+=("$name")

  (
    start_time=$(date +%s)
    exit_code=0

    case "$cmd" in
      claude)
        # shellcheck disable=SC2086
        timeout "$TIMEOUT" claude $flags "$PROMPT" > "$output_file" 2>/dev/null || exit_code=$?
        ;;
      codex)
        # shellcheck disable=SC2086
        timeout "$TIMEOUT" codex $flags --prompt "$PROMPT" > "$output_file" 2>/dev/null || exit_code=$?
        ;;
      gemini)
        if [[ "$input_mode" == "stdin" ]]; then
          echo "$PROMPT" | timeout "$TIMEOUT" gemini $flags > "$output_file" 2>/dev/null || exit_code=$?
        else
          # shellcheck disable=SC2086
          timeout "$TIMEOUT" gemini $flags "$PROMPT" > "$output_file" 2>/dev/null || exit_code=$?
        fi
        ;;
      cursor-cli)
        # shellcheck disable=SC2086
        timeout "$TIMEOUT" cursor-cli $flags --prompt "$PROMPT" > "$output_file" 2>/dev/null || exit_code=$?
        ;;
      *)
        echo "Unknown CLI: $cmd" > "$output_file"
        exit_code=127
        ;;
    esac

    end_time=$(date +%s)
    duration=$((end_time - start_time))

    jq -n \
      --arg name "$name" \
      --argjson exit "$exit_code" \
      --argjson duration "$duration" \
      '{
        "name": $name,
        "exit_code": $exit,
        "duration_seconds": $duration,
        "success": ($exit == 0),
        "timed_out": ($exit == 124)
      }' > "$status_file"
  ) &

  PIDS+=($!)
done

# Wait for all processes
for pid in "${PIDS[@]}"; do
  wait "$pid" 2>/dev/null || true
done

# Build summary
results='[]'
for name in "${MODEL_NAMES[@]}"; do
  status_file="$OUTPUT_DIR/${name}.status"
  output_file="$OUTPUT_DIR/${name}.md"

  if [[ -f "$status_file" ]]; then
    status=$(cat "$status_file")
  else
    status=$(jq -n --arg name "$name" '{"name":$name,"exit_code":1,"duration_seconds":0,"success":false,"timed_out":false}')
  fi

  has_output="false"
  if [[ -f "$output_file" && -s "$output_file" ]]; then
    has_output="true"
  fi

  results=$(jq --argjson s "$status" --argjson ho "$has_output" '. + [$s + {"has_output": $ho}]' <<< "$results")
done

jq '.' <<< "$results"
