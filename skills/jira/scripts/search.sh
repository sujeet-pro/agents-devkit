#!/usr/bin/env bash
set -euo pipefail

# Usage: bash search.sh <jql-query> [--max-results N] [--start-at N] [--fields field1,field2]

die() { echo "Error: $*" >&2; exit 1; }

usage() {
  cat >&2 <<'USAGE'
Usage: bash search.sh <jql-query> [--max-results N] [--start-at N] [--fields field1,field2]

Arguments:
  <jql-query>       JQL query string (required, positional)
  --max-results N   Maximum results to return (default: 50)
  --start-at N      Starting index for pagination (default: 0)
  --fields LIST     Comma-separated field names (default: summary,status,assignee,priority,issuetype)

Examples:
  bash search.sh "project = PROJ AND status = 'In Progress'"
  bash search.sh "assignee = currentUser()" --max-results 10
  bash search.sh "sprint in openSprints()" --fields "summary,status,assignee"
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

[[ $# -ge 1 ]] || usage

jql="$1"; shift

max_results=50
start_at=0
fields="summary,status,assignee,priority,issuetype"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-results) max_results="$2"; shift 2 ;;
    --start-at) start_at="$2"; shift 2 ;;
    --fields) fields="$2"; shift 2 ;;
    *) die "Unknown flag: $1" ;;
  esac
done

fields_json=$(echo "$fields" | tr ',' '\n' | jq -R . | jq -s .)

payload=$(jq -n \
  --arg jql "$jql" \
  --argjson maxResults "$max_results" \
  --argjson startAt "$start_at" \
  --argjson fields "$fields_json" \
  '{jql: $jql, maxResults: $maxResults, startAt: $startAt, fields: $fields}')

jira_api POST "${API}/search" -d "$payload"
