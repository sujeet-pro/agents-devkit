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
Usage: pages.sh <action> [args...]

Actions:
  get          --id <pageId>
  get-by-title --title <title> --space-id <spaceId>
  search       --query <query> [--space-id <spaceId>] [--limit <n>]
  create       --space-id <spaceId> --title <title> --body <html> [--parent-id <parentId>]
  update       --id <pageId> --title <title> --body <html> [--version <n>]
  delete       --id <pageId>
  children     --id <pageId>
  labels       --id <pageId>
  add-label    --id <pageId> --label <name>
EOF
  exit 1
}

case "$ACTION" in
  get)
    id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --id) id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$id" ]] || die "get requires --id"
    confluence_api GET "${V2}/pages/${id}?body-format=storage"
    ;;

  get-by-title)
    title="" space_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --title) title="$2"; shift 2 ;;
        --space-id) space_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$title" ]] || die "get-by-title requires --title"
    [[ -n "$space_id" ]] || die "get-by-title requires --space-id"
    encoded_title=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$title'))")
    confluence_api GET "${V2}/pages?title=${encoded_title}&space-id=${space_id}&body-format=storage"
    ;;

  search)
    query="" space_id="" limit="25"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --query) query="$2"; shift 2 ;;
        --space-id) space_id="$2"; shift 2 ;;
        --limit) limit="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$query" ]] || die "search requires --query"
    encoded_query=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$query'))")
    url="${V2}/pages?title=${encoded_query}&limit=${limit}"
    [[ -z "$space_id" ]] || url="${url}&space-id=${space_id}"
    confluence_api GET "$url"
    ;;

  create)
    space_id="" title="" body="" parent_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --space-id) space_id="$2"; shift 2 ;;
        --title) title="$2"; shift 2 ;;
        --body) body="$2"; shift 2 ;;
        --parent-id) parent_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$space_id" ]] || die "create requires --space-id"
    [[ -n "$title" ]] || die "create requires --title"
    [[ -n "$body" ]] || die "create requires --body"

    payload=$(jq -n \
      --arg spaceId "$space_id" \
      --arg title "$title" \
      --arg body "$body" \
      --arg parentId "$parent_id" \
      '{
        spaceId: $spaceId,
        status: "current",
        title: $title,
        body: { representation: "storage", value: $body }
      } + (if $parentId != "" then { parentId: $parentId } else {} end)')

    confluence_api POST "${V2}/pages" -d "$payload"
    ;;

  update)
    id="" title="" body="" version=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --id) id="$2"; shift 2 ;;
        --title) title="$2"; shift 2 ;;
        --body) body="$2"; shift 2 ;;
        --version) version="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$id" ]] || die "update requires --id"
    [[ -n "$title" ]] || die "update requires --title"
    [[ -n "$body" ]] || die "update requires --body"

    if [[ -z "$version" ]]; then
      current=$(confluence_api GET "${V2}/pages/${id}?body-format=storage")
      current_version=$(echo "$current" | jq -r '.version.number')
      version=$((current_version + 1))
    fi

    payload=$(jq -n \
      --arg id "$id" \
      --arg title "$title" \
      --arg body "$body" \
      --argjson version "$version" \
      '{
        id: $id,
        status: "current",
        title: $title,
        body: { representation: "storage", value: $body },
        version: { number: $version, message: "Updated via API" }
      }')

    confluence_api PUT "${V2}/pages/${id}" -d "$payload"
    ;;

  delete)
    id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --id) id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$id" ]] || die "delete requires --id"
    confluence_api DELETE "${V2}/pages/${id}"
    echo '{"deleted":true}'
    ;;

  children)
    id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --id) id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$id" ]] || die "children requires --id"
    confluence_api GET "${V2}/pages/${id}/children"
    ;;

  labels)
    id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --id) id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$id" ]] || die "labels requires --id"
    confluence_api GET "${V2}/pages/${id}/labels"
    ;;

  add-label)
    id="" label=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --id) id="$2"; shift 2 ;;
        --label) label="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$id" ]] || die "add-label requires --id"
    [[ -n "$label" ]] || die "add-label requires --label"

    payload=$(jq -n --arg label "$label" '[{prefix: "global", name: $label}]')
    confluence_api POST "${V2}/pages/${id}/labels" -d "$payload"
    ;;

  *)
    usage
    ;;
esac
