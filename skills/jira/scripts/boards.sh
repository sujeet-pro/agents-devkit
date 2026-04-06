#!/usr/bin/env bash
set -euo pipefail

# Usage: bash boards.sh <action> [args...]
# Actions: list, get, config, sprints, sprint-issues, move-to-sprint,
#          backlog, move-to-backlog, rank

die() { echo "Error: $*" >&2; exit 1; }

usage() {
  cat >&2 <<'USAGE'
Usage: bash boards.sh <action> [args...]

Actions:
  list             [--project KEY]
  get              --board-id ID
  config           --board-id ID
  sprints          --board-id ID [--state active,future,closed]
  sprint-issues    --sprint-id ID
  move-to-sprint   --sprint-id ID --issues KEY1,KEY2
  backlog          --board-id ID
  move-to-backlog  --issues KEY1,KEY2
  rank             --issues KEY1,KEY2 --rank-before KEY
USAGE
  exit 1
}

[[ -n "${JIRA_URL:-}" ]] || die "JIRA_URL not set. Add to ~/.zshenv"
[[ -n "${JIRA_USERNAME:-}" ]] || die "JIRA_USERNAME not set. Add to ~/.zshenv"
[[ -n "${JIRA_API_TOKEN:-}" ]] || die "JIRA_API_TOKEN not set. Add to ~/.zshenv"

JIRA_URL="${JIRA_URL%/}"
AUTH="-u ${JIRA_USERNAME}:${JIRA_API_TOKEN}"
API="${JIRA_URL}/rest/api/3"
AGILE="${JIRA_URL}/rest/agile/1.0"

jira_api() {
  local method="$1" endpoint="$2"; shift 2
  local response http_code body
  response=$(curl -s -w "\n%{http_code}" ${AUTH} \
    -X "$method" -H "Content-Type: application/json" -H "Accept: application/json" \
    "${endpoint}" "$@")
  http_code=$(echo "$response" | tail -1)
  body=$(echo "$response" | sed '$d')
  if [[ "$http_code" -ge 400 ]]; then
    echo "$body" >&2
    return 1
  fi
  echo "$body"
}

parse_issues_csv() {
  echo "$1" | tr ',' '\n' | jq -R . | jq -s .
}

ACTION="${1:-}"; shift 2>/dev/null || true
[[ -n "$ACTION" ]] || usage

case "$ACTION" in
  list)
    project=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    url="${AGILE}/board"
    [[ -n "$project" ]] && url+="?projectKeyOrId=${project}"
    jira_api GET "$url"
    ;;

  get)
    board_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --board-id) board_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$board_id" ]] || die "get requires --board-id"
    jira_api GET "${AGILE}/board/${board_id}"
    ;;

  config)
    board_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --board-id) board_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$board_id" ]] || die "config requires --board-id"
    jira_api GET "${AGILE}/board/${board_id}/configuration"
    ;;

  sprints)
    board_id="" state=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --board-id) board_id="$2"; shift 2 ;;
        --state) state="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$board_id" ]] || die "sprints requires --board-id"
    url="${AGILE}/board/${board_id}/sprint"
    [[ -n "$state" ]] && url+="?state=${state}"
    jira_api GET "$url"
    ;;

  sprint-issues)
    sprint_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --sprint-id) sprint_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$sprint_id" ]] || die "sprint-issues requires --sprint-id"
    jira_api GET "${AGILE}/sprint/${sprint_id}/issue"
    ;;

  move-to-sprint)
    sprint_id="" issues=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --sprint-id) sprint_id="$2"; shift 2 ;;
        --issues) issues="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$sprint_id" ]] || die "move-to-sprint requires --sprint-id"
    [[ -n "$issues" ]] || die "move-to-sprint requires --issues"
    issues_json=$(parse_issues_csv "$issues")
    payload=$(jq -n --argjson i "$issues_json" '{issues: $i}')
    result=$(jira_api POST "${AGILE}/sprint/${sprint_id}/issue" -d "$payload")
    if [[ -z "$result" ]]; then
      echo '{"status":"moved_to_sprint"}'
    else
      echo "$result"
    fi
    ;;

  backlog)
    board_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --board-id) board_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$board_id" ]] || die "backlog requires --board-id"
    jira_api GET "${AGILE}/board/${board_id}/backlog"
    ;;

  move-to-backlog)
    issues=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --issues) issues="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$issues" ]] || die "move-to-backlog requires --issues"
    issues_json=$(parse_issues_csv "$issues")
    payload=$(jq -n --argjson i "$issues_json" '{issues: $i}')
    result=$(jira_api POST "${AGILE}/backlog/issue" -d "$payload")
    if [[ -z "$result" ]]; then
      echo '{"status":"moved_to_backlog"}'
    else
      echo "$result"
    fi
    ;;

  rank)
    issues="" rank_before=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --issues) issues="$2"; shift 2 ;;
        --rank-before) rank_before="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$issues" ]] || die "rank requires --issues"
    [[ -n "$rank_before" ]] || die "rank requires --rank-before"
    issues_json=$(parse_issues_csv "$issues")
    payload=$(jq -n \
      --argjson i "$issues_json" \
      --arg rb "$rank_before" \
      '{issues: $i, rankBeforeIssue: $rb}')
    result=$(jira_api PUT "${AGILE}/issue/rank" -d "$payload")
    if [[ -z "$result" ]]; then
      echo '{"status":"ranked"}'
    else
      echo "$result"
    fi
    ;;

  *) die "Unknown action: $ACTION. Run without arguments for usage." ;;
esac
