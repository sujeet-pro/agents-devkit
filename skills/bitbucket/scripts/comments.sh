#!/usr/bin/env bash
set -euo pipefail

die() { echo "Error: $*" >&2; exit 1; }

[[ -n "${BITBUCKET_USERNAME:-}" ]] || die "BITBUCKET_USERNAME not set. Add to ~/.zshenv: export BITBUCKET_USERNAME=\"your-username\""
[[ -n "${BITBUCKET_TOKEN:-}" ]] || die "BITBUCKET_TOKEN not set. Add to ~/.zshenv: export BITBUCKET_TOKEN=\"your-app-password\""

BASE="https://api.bitbucket.org/2.0"
AUTH="-u ${BITBUCKET_USERNAME}:${BITBUCKET_TOKEN}"

bb_api() {
  local method="$1" endpoint="$2"; shift 2
  local response http_code body
  response=$(curl -s -w "\n%{http_code}" ${AUTH} \
    -X "$method" -H "Content-Type: application/json" -H "Accept: application/json" \
    "${BASE}${endpoint}" "$@")
  http_code=$(echo "$response" | tail -1)
  body=$(echo "$response" | sed '$d')
  if [[ "$http_code" -ge 400 ]]; then
    echo "$body" >&2
    return 1
  fi
  echo "$body"
}

usage() {
  cat <<'EOF'
Usage: comments.sh <action> <workspace> <repo> <pr-id> [options...]

Actions:
  list         <ws> <repo> <pr-id>                              List all comments
  get          <ws> <repo> <pr-id> --comment-id <id>            Get single comment
  create       <ws> <repo> <pr-id> --body "..." [--file path --line N]  Post comment
  reply        <ws> <repo> <pr-id> --parent-id <id> --body "..." Reply to comment
  update       <ws> <repo> <pr-id> --comment-id <id> --body "..." Update comment
  delete       <ws> <repo> <pr-id> --comment-id <id>            Delete comment
  list-tasks   <ws> <repo> <pr-id>                              List tasks
  create-task  <ws> <repo> <pr-id> --body "..." [--comment-id N] Create task
  resolve-task <ws> <repo> <pr-id> --task-id <id> --state RESOLVED|OPEN
EOF
  exit 0
}

[[ $# -ge 1 ]] || usage

action="$1"; shift

[[ "$action" == "--help" ]] && usage

[[ $# -ge 3 ]] || die "Requires at least: <workspace> <repo> <pr-id>"
workspace="$1"; shift
repo="$1"; shift
pr_id="$1"; shift

pr_path="/repositories/${workspace}/${repo}/pullrequests/${pr_id}"

case "$action" in
  list)
    bb_api GET "${pr_path}/comments"
    ;;

  get)
    comment_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --comment-id) comment_id="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$comment_id" ]] || die "get requires --comment-id"
    bb_api GET "${pr_path}/comments/${comment_id}"
    ;;

  create)
    body="" file="" line=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --body) body="$2"; shift 2 ;;
        --file) file="$2"; shift 2 ;;
        --line) line="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$body" ]] || die "create requires --body"
    if [[ -n "$file" && -n "$line" ]]; then
      payload=$(jq -n \
        --arg body "$body" \
        --arg file "$file" \
        --argjson line "$line" \
        '{content: {raw: $body}, inline: {path: $file, to: $line}}')
    else
      payload=$(jq -n --arg body "$body" '{content: {raw: $body}}')
    fi
    bb_api POST "${pr_path}/comments" -d "$payload"
    ;;

  reply)
    parent_id="" body=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --parent-id) parent_id="$2"; shift 2 ;;
        --body) body="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$parent_id" ]] || die "reply requires --parent-id"
    [[ -n "$body" ]] || die "reply requires --body"
    payload=$(jq -n \
      --arg body "$body" \
      --argjson pid "$parent_id" \
      '{content: {raw: $body}, parent: {id: $pid}}')
    bb_api POST "${pr_path}/comments" -d "$payload"
    ;;

  update)
    comment_id="" body=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --comment-id) comment_id="$2"; shift 2 ;;
        --body) body="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$comment_id" ]] || die "update requires --comment-id"
    [[ -n "$body" ]] || die "update requires --body"
    payload=$(jq -n --arg body "$body" '{content: {raw: $body}}')
    bb_api PUT "${pr_path}/comments/${comment_id}" -d "$payload"
    ;;

  delete)
    comment_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --comment-id) comment_id="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$comment_id" ]] || die "delete requires --comment-id"
    bb_api DELETE "${pr_path}/comments/${comment_id}"
    ;;

  list-tasks)
    bb_api GET "${pr_path}/tasks"
    ;;

  create-task)
    body="" comment_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --body) body="$2"; shift 2 ;;
        --comment-id) comment_id="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$body" ]] || die "create-task requires --body"
    if [[ -n "$comment_id" ]]; then
      payload=$(jq -n \
        --arg body "$body" \
        --argjson cid "$comment_id" \
        '{content: {raw: $body}, comment: {id: $cid}}')
    else
      payload=$(jq -n --arg body "$body" '{content: {raw: $body}}')
    fi
    bb_api POST "${pr_path}/tasks" -d "$payload"
    ;;

  resolve-task)
    task_id="" state=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --task-id) task_id="$2"; shift 2 ;;
        --state) state="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$task_id" ]] || die "resolve-task requires --task-id"
    [[ -n "$state" ]] || die "resolve-task requires --state (RESOLVED|OPEN)"
    payload=$(jq -n --arg s "$state" '{state: $s}')
    bb_api PUT "${pr_path}/tasks/${task_id}" -d "$payload"
    ;;

  *)
    die "Unknown action: $action. Run with --help for usage."
    ;;
esac
