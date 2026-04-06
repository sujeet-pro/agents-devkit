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
Usage: comments.sh <action> [args...]

Actions:
  list-footer   --page-id <pageId>
  list-inline   --page-id <pageId>
  create-footer --page-id <pageId> --body <html>
  create-inline --page-id <pageId> --body <html> --text-selection <text> [--match-index <n>]
  reply         --comment-id <commentId> --body <html>
  get           --comment-id <commentId> --type <footer|inline>
EOF
  exit 1
}

case "$ACTION" in
  list-footer)
    page_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --page-id) page_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$page_id" ]] || die "list-footer requires --page-id"
    confluence_api GET "${V2}/pages/${page_id}/footer-comments"
    ;;

  list-inline)
    page_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --page-id) page_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$page_id" ]] || die "list-inline requires --page-id"
    confluence_api GET "${V2}/pages/${page_id}/inline-comments"
    ;;

  create-footer)
    page_id="" body=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --page-id) page_id="$2"; shift 2 ;;
        --body) body="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$page_id" ]] || die "create-footer requires --page-id"
    [[ -n "$body" ]] || die "create-footer requires --body"

    payload=$(jq -n \
      --arg pageId "$page_id" \
      --arg body "$body" \
      '{
        pageId: $pageId,
        body: { representation: "storage", value: $body }
      }')

    confluence_api POST "${V2}/footer-comments" -d "$payload"
    ;;

  create-inline)
    page_id="" body="" text_selection="" match_index="0"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --page-id) page_id="$2"; shift 2 ;;
        --body) body="$2"; shift 2 ;;
        --text-selection) text_selection="$2"; shift 2 ;;
        --match-index) match_index="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$page_id" ]] || die "create-inline requires --page-id"
    [[ -n "$body" ]] || die "create-inline requires --body"
    [[ -n "$text_selection" ]] || die "create-inline requires --text-selection"

    payload=$(jq -n \
      --arg pageId "$page_id" \
      --arg body "$body" \
      --arg textSelection "$text_selection" \
      --argjson matchIndex "$match_index" \
      '{
        pageId: $pageId,
        body: { representation: "storage", value: $body },
        inlineCommentProperties: {
          textSelection: $textSelection,
          textSelectionMatchCount: 1,
          textSelectionMatchIndex: $matchIndex
        }
      }')

    confluence_api POST "${V2}/inline-comments" -d "$payload"
    ;;

  reply)
    comment_id="" body=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --comment-id) comment_id="$2"; shift 2 ;;
        --body) body="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$comment_id" ]] || die "reply requires --comment-id"
    [[ -n "$body" ]] || die "reply requires --body"

    parent=$(confluence_api GET "${V2}/footer-comments/${comment_id}?body-format=storage")
    page_id=$(echo "$parent" | jq -r '.pageId')
    [[ "$page_id" != "null" && -n "$page_id" ]] || die "Could not determine pageId from parent comment ${comment_id}"

    payload=$(jq -n \
      --arg pageId "$page_id" \
      --arg body "$body" \
      --arg parentCommentId "$comment_id" \
      '{
        pageId: $pageId,
        body: { representation: "storage", value: $body },
        parentCommentId: $parentCommentId
      }')

    confluence_api POST "${V2}/footer-comments" -d "$payload"
    ;;

  get)
    comment_id="" type=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --comment-id) comment_id="$2"; shift 2 ;;
        --type) type="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$comment_id" ]] || die "get requires --comment-id"
    [[ -n "$type" ]] || die "get requires --type (footer|inline)"

    case "$type" in
      footer) confluence_api GET "${V2}/footer-comments/${comment_id}?body-format=storage" ;;
      inline) confluence_api GET "${V2}/inline-comments/${comment_id}?body-format=storage" ;;
      *) die "type must be 'footer' or 'inline'" ;;
    esac
    ;;

  *)
    usage
    ;;
esac
