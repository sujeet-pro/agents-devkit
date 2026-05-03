#!/usr/bin/env bash
# parse-mode.sh — flag parser sourced by adk skills to normalize --auto / -i / --fix.
#
# Usage (from inside another skill):
#   source "${CLAUDE_PLUGIN_ROOT}/skills/mode-contract/scripts/parse-mode.sh"
#   parse_mode "$@"
#
# After parse_mode returns, the following env vars are set:
#   ADK_MODE   — "auto" (default) | "interactive"
#   ADK_FIX    — 0 (default) | 1
#   ADK_REMAINING — array of args that weren't consumed (use with "${ADK_REMAINING[@]}")
#
# Exit non-zero on contradiction (--auto -i).

parse_mode() {
  ADK_MODE="auto"
  ADK_FIX=0
  ADK_REMAINING=()
  local saw_auto=0
  local saw_interactive=0

  while (( "$#" )); do
    case "$1" in
      --auto)
        saw_auto=1
        ADK_MODE="auto"
        shift
        ;;
      -i|--interactive)
        saw_interactive=1
        ADK_MODE="interactive"
        shift
        ;;
      --fix)
        ADK_FIX=1
        shift
        ;;
      --)
        shift
        ADK_REMAINING+=("$@")
        break
        ;;
      *)
        ADK_REMAINING+=("$1")
        shift
        ;;
    esac
  done

  if (( saw_auto == 1 && saw_interactive == 1 )); then
    echo "ERROR: --auto and -i / --interactive are mutually exclusive" >&2
    return 2
  fi

  export ADK_MODE ADK_FIX
  return 0
}

# If sourced and called directly (debug), demo the parse:
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  parse_mode "$@"
  echo "ADK_MODE=$ADK_MODE"
  echo "ADK_FIX=$ADK_FIX"
  echo "ADK_REMAINING=${ADK_REMAINING[*]:-}"
fi
