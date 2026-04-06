#!/usr/bin/env bash
set -euo pipefail

die() { echo "Error: $*" >&2; exit 1; }

[[ -n "${CONFLUENCE_URL:-}" ]] || die "CONFLUENCE_URL not set. Add to ~/.zshenv"
[[ -n "${CONFLUENCE_USERNAME:-}" ]] || die "CONFLUENCE_USERNAME not set. Add to ~/.zshenv"
[[ -n "${CONFLUENCE_API_TOKEN:-}" ]] || die "CONFLUENCE_API_TOKEN not set. Add to ~/.zshenv"

CONFLUENCE_URL="${CONFLUENCE_URL%/}"
AUTH="-u ${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}"

confluence_api() {
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

V2="${CONFLUENCE_URL}/wiki/api/v2"
V1="${CONFLUENCE_URL}/wiki/rest/api"

ACTION="${1:-}"; shift 2>/dev/null || true

usage() {
  cat >&2 <<'EOF'
Usage: spaces.sh <action> [args...]

Actions:
  list  [--limit <n>]
  get   --id <spaceId> | --key <spaceKey>
EOF
  exit 1
}

case "$ACTION" in
  list)
    limit="25"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --limit) limit="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    confluence_api GET "${V2}/spaces?limit=${limit}"
    ;;

  get)
    id="" key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --id) id="$2"; shift 2 ;;
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done

    if [[ -n "$id" ]]; then
      confluence_api GET "${V2}/spaces/${id}"
    elif [[ -n "$key" ]]; then
      confluence_api GET "${V2}/spaces?keys=${key}"
    else
      die "get requires --id or --key"
    fi
    ;;

  *)
    usage
    ;;
esac
