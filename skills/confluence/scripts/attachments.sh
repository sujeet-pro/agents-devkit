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

confluence_upload() {
  local method="$1" endpoint="$2"; shift 2
  local response http_code body
  response=$(curl -s -w "\n%{http_code}" ${AUTH} \
    -X "$method" -H "X-Atlassian-Token: nocheck" \
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
Usage: attachments.sh <action> [args...]

Actions:
  list     --page-id <pageId>
  upload   --page-id <pageId> --file <filePath> [--comment <description>]
  update   --page-id <pageId> --attachment-id <attId> --file <filePath>
  download --page-id <pageId> --attachment-id <attId> --output <outputPath>
EOF
  exit 1
}

case "$ACTION" in
  list)
    page_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --page-id) page_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$page_id" ]] || die "list requires --page-id"
    confluence_api GET "${V1}/content/${page_id}/child/attachment"
    ;;

  upload)
    page_id="" file="" comment=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --page-id) page_id="$2"; shift 2 ;;
        --file) file="$2"; shift 2 ;;
        --comment) comment="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$page_id" ]] || die "upload requires --page-id"
    [[ -n "$file" ]] || die "upload requires --file"
    [[ -f "$file" ]] || die "File not found: $file"

    upload_args=(-F "file=@${file}")
    [[ -z "$comment" ]] || upload_args+=(-F "comment=${comment}")

    confluence_upload POST "${V1}/content/${page_id}/child/attachment" "${upload_args[@]}"
    ;;

  update)
    page_id="" attachment_id="" file=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --page-id) page_id="$2"; shift 2 ;;
        --attachment-id) attachment_id="$2"; shift 2 ;;
        --file) file="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$page_id" ]] || die "update requires --page-id"
    [[ -n "$attachment_id" ]] || die "update requires --attachment-id"
    [[ -n "$file" ]] || die "update requires --file"
    [[ -f "$file" ]] || die "File not found: $file"

    confluence_upload POST "${V1}/content/${page_id}/child/attachment/${attachment_id}/data" \
      -F "file=@${file}"
    ;;

  download)
    page_id="" attachment_id="" output=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --page-id) page_id="$2"; shift 2 ;;
        --attachment-id) attachment_id="$2"; shift 2 ;;
        --output) output="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$page_id" ]] || die "download requires --page-id"
    [[ -n "$attachment_id" ]] || die "download requires --attachment-id"
    [[ -n "$output" ]] || die "download requires --output"

    attachments=$(confluence_api GET "${V1}/content/${page_id}/child/attachment")
    download_path=$(echo "$attachments" | jq -r --arg id "$attachment_id" \
      '.results[] | select(.id == $id or .id == ("att" + $id)) | ._links.download' | head -1)

    [[ -n "$download_path" && "$download_path" != "null" ]] || die "Attachment ${attachment_id} not found on page ${page_id}"

    curl -s ${AUTH} -o "$output" "${CONFLUENCE_URL}${download_path}"
    echo "{\"downloaded\":true,\"output\":\"${output}\"}"
    ;;

  *)
    usage
    ;;
esac
