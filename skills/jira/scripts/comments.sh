#!/usr/bin/env bash
set -euo pipefail

# Usage: bash comments.sh <action> --key <issue-key> [args...]
# Actions: list, get, add, update, delete

die() { echo "Error: $*" >&2; exit 1; }

usage() {
  cat >&2 <<'USAGE'
Usage: bash comments.sh <action> --key <issue-key> [args...]

Actions:
  list     --key KEY
  get      --key KEY --comment-id ID
  add      --key KEY --body TEXT
  update   --key KEY --comment-id ID --body TEXT
  delete   --key KEY --comment-id ID
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

text_to_adf() {
  local text="$1"
  local paragraphs=""
  local first=true
  while IFS= read -r line || [[ -n "$line" ]]; do
    local escaped
    escaped=$(jq -Rrs '.' <<< "$line" | sed 's/^"//;s/"$//')
    if [[ "$first" == "true" ]]; then
      first=false
    else
      paragraphs+=","
    fi
    paragraphs+="{\"type\":\"paragraph\",\"content\":[{\"type\":\"text\",\"text\":\"${escaped}\"}]}"
  done <<< "$text"
  echo "{\"type\":\"doc\",\"version\":1,\"content\":[${paragraphs}]}"
}

ACTION="${1:-}"; shift 2>/dev/null || true
[[ -n "$ACTION" ]] || usage

case "$ACTION" in
  list)
    key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "list requires --key"
    jira_api GET "${API}/issue/${key}/comment"
    ;;

  get)
    key="" comment_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --comment-id) comment_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "get requires --key"
    [[ -n "$comment_id" ]] || die "get requires --comment-id"
    jira_api GET "${API}/issue/${key}/comment/${comment_id}"
    ;;

  add)
    key="" body=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --body) body="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "add requires --key"
    [[ -n "$body" ]] || die "add requires --body"
    adf=$(text_to_adf "$body")
    payload=$(jq -n --argjson b "$adf" '{body: $b}')
    jira_api POST "${API}/issue/${key}/comment" -d "$payload"
    ;;

  update)
    key="" comment_id="" body=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --comment-id) comment_id="$2"; shift 2 ;;
        --body) body="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "update requires --key"
    [[ -n "$comment_id" ]] || die "update requires --comment-id"
    [[ -n "$body" ]] || die "update requires --body"
    adf=$(text_to_adf "$body")
    payload=$(jq -n --argjson b "$adf" '{body: $b}')
    jira_api PUT "${API}/issue/${key}/comment/${comment_id}" -d "$payload"
    ;;

  delete)
    key="" comment_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --comment-id) comment_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "delete requires --key"
    [[ -n "$comment_id" ]] || die "delete requires --comment-id"
    result=$(jira_api DELETE "${API}/issue/${key}/comment/${comment_id}")
    if [[ -z "$result" ]]; then
      echo '{"status":"deleted"}'
    else
      echo "$result"
    fi
    ;;

  *) die "Unknown action: $ACTION. Run without arguments for usage." ;;
esac
