#!/usr/bin/env bash
set -euo pipefail

die() { echo "Error: $*" >&2; exit 1; }

[[ -n "${JIRA_URL:-}" ]] || die "JIRA_URL not set. Add to ~/.zshenv"
[[ -n "${JIRA_USERNAME:-}" ]] || die "JIRA_USERNAME not set. Add to ~/.zshenv"
[[ -n "${JIRA_API_TOKEN:-}" ]] || die "JIRA_API_TOKEN not set. Add to ~/.zshenv"

JIRA_URL="${JIRA_URL%/}"
AUTH="-u ${JIRA_USERNAME}:${JIRA_API_TOKEN}"
API="${JIRA_URL}/rest/api/3"

response=$(curl -s -w "\n%{http_code}" ${AUTH} \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  "${API}/myself")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" -ge 400 ]]; then
  echo "Authentication failed (HTTP $http_code)" >&2
  echo "$body" >&2
  exit 1
fi

account_id=$(echo "$body" | jq -r '.accountId // empty')
display_name=$(echo "$body" | jq -r '.displayName // empty')
email=$(echo "$body" | jq -r '.emailAddress // empty')

jq -n \
  --arg authenticated "true" \
  --arg accountId "$account_id" \
  --arg displayName "$display_name" \
  --arg emailAddress "$email" \
  '{authenticated: true, accountId: $accountId, displayName: $displayName, emailAddress: $emailAddress}'
