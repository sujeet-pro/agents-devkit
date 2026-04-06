#!/usr/bin/env bash
set -euo pipefail

die() { echo "Error: $*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: auth.sh

Validates Bitbucket credentials and tests API access.
Requires BITBUCKET_USERNAME and BITBUCKET_TOKEN in environment.

Output: JSON with authenticated status, username, and display_name.
EOF
  exit 0
}

[[ "${1:-}" == "--help" ]] && usage

[[ -n "${BITBUCKET_USERNAME:-}" ]] || die "BITBUCKET_USERNAME not set. Add to ~/.zshenv: export BITBUCKET_USERNAME=\"your-username\""
[[ -n "${BITBUCKET_TOKEN:-}" ]] || die "BITBUCKET_TOKEN not set. Add to ~/.zshenv: export BITBUCKET_TOKEN=\"your-app-password\""

BASE="https://api.bitbucket.org/2.0"
AUTH="-u ${BITBUCKET_USERNAME}:${BITBUCKET_TOKEN}"

response=$(curl -s -w "\n%{http_code}" ${AUTH} \
  -H "Accept: application/json" \
  "${BASE}/user")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" -ge 400 ]]; then
  echo "$body" >&2
  die "Authentication failed (HTTP ${http_code}). Check BITBUCKET_USERNAME and BITBUCKET_TOKEN."
fi

username=$(echo "$body" | jq -r '.username // empty')
display_name=$(echo "$body" | jq -r '.display_name // empty')

jq -n \
  --argjson authenticated true \
  --arg username "$username" \
  --arg display_name "$display_name" \
  '{authenticated: $authenticated, username: $username, display_name: $display_name}'
