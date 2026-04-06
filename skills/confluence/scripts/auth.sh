#!/usr/bin/env bash
set -euo pipefail

die() { echo "Error: $*" >&2; exit 1; }

[[ -n "${CONFLUENCE_URL:-}" ]] || die "CONFLUENCE_URL not set. Add to ~/.zshenv: export CONFLUENCE_URL=\"https://your-domain.atlassian.net\""
[[ -n "${CONFLUENCE_USERNAME:-}" ]] || die "CONFLUENCE_USERNAME not set. Add to ~/.zshenv: export CONFLUENCE_USERNAME=\"your-email@example.com\""
[[ -n "${CONFLUENCE_API_TOKEN:-}" ]] || die "CONFLUENCE_API_TOKEN not set. Add to ~/.zshenv: export CONFLUENCE_API_TOKEN=\"your-api-token\""

CONFLUENCE_URL="${CONFLUENCE_URL%/}"
AUTH="-u ${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}"

response=$(curl -s -w "\n%{http_code}" ${AUTH} \
  -X GET -H "Accept: application/json" \
  "${CONFLUENCE_URL}/wiki/api/v2/spaces?limit=1")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" -ge 400 ]]; then
  echo "Authentication failed (HTTP ${http_code})" >&2
  echo "$body" >&2
  echo "" >&2
  echo "Verify your credentials in ~/.zshenv:" >&2
  echo "  export CONFLUENCE_URL=\"https://your-domain.atlassian.net\"" >&2
  echo "  export CONFLUENCE_USERNAME=\"your-email@example.com\"" >&2
  echo "  export CONFLUENCE_API_TOKEN=\"your-api-token\"" >&2
  echo "" >&2
  echo "Generate a token at: https://id.atlassian.com/manage-profile/security/api-tokens" >&2
  echo "Then run: source ~/.zshenv" >&2
  exit 1
fi

echo "{\"authenticated\":true,\"url\":\"${CONFLUENCE_URL}\",\"user\":\"${CONFLUENCE_USERNAME}\"}"
