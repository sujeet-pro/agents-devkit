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

bb_raw() {
  local endpoint="$1"
  local response http_code body
  response=$(curl -s -w "\n%{http_code}" ${AUTH} \
    "${BASE}${endpoint}")
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
Usage: pr.sh <action> <workspace> <repo> [pr-id] [options...]

Actions:
  get         <ws> <repo> <pr-id>                    Get PR details
  list        <ws> <repo> [--state OPEN|MERGED|DECLINED|SUPERSEDED]
  diff        <ws> <repo> <pr-id>                    Get full text diff
  diffstat    <ws> <repo> <pr-id>                    Get file change summary
  create      <ws> <repo> --title "..." --source-branch "..." [--dest-branch main] [--description "..."]
  update      <ws> <repo> <pr-id> [--title "..."] [--description "..."]
  merge       <ws> <repo> <pr-id> [--strategy merge_commit|squash|fast_forward] [--close-source true|false]
  decline     <ws> <repo> <pr-id>                    Decline a PR
  approve     <ws> <repo> <pr-id>                    Approve a PR
  unapprove   <ws> <repo> <pr-id>                    Remove approval
  commits     <ws> <repo> <pr-id>                    List PR commits
  statuses    <ws> <repo> <pr-id>                    Get build statuses
  activity    <ws> <repo> <pr-id>                    Get activity feed
EOF
  exit 0
}

[[ $# -ge 1 ]] || usage

action="$1"; shift

[[ "$action" == "--help" ]] && usage

[[ $# -ge 2 ]] || die "Requires at least: <workspace> <repo>"
workspace="$1"; shift
repo="$1"; shift

case "$action" in
  get)
    [[ $# -ge 1 ]] || die "get requires <pr-id>"
    pr_id="$1"
    bb_api GET "/repositories/${workspace}/${repo}/pullrequests/${pr_id}"
    ;;

  list)
    state="OPEN"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --state) state="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    bb_api GET "/repositories/${workspace}/${repo}/pullrequests?state=${state}"
    ;;

  diff)
    [[ $# -ge 1 ]] || die "diff requires <pr-id>"
    pr_id="$1"
    bb_raw "/repositories/${workspace}/${repo}/pullrequests/${pr_id}/diff"
    ;;

  diffstat)
    [[ $# -ge 1 ]] || die "diffstat requires <pr-id>"
    pr_id="$1"
    bb_api GET "/repositories/${workspace}/${repo}/pullrequests/${pr_id}/diffstat"
    ;;

  create)
    title="" source_branch="" dest_branch="main" description=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --title) title="$2"; shift 2 ;;
        --source-branch) source_branch="$2"; shift 2 ;;
        --dest-branch) dest_branch="$2"; shift 2 ;;
        --description) description="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$title" ]] || die "create requires --title"
    [[ -n "$source_branch" ]] || die "create requires --source-branch"
    payload=$(jq -n \
      --arg title "$title" \
      --arg src "$source_branch" \
      --arg dst "$dest_branch" \
      --arg desc "$description" \
      '{
        title: $title,
        source: {branch: {name: $src}},
        destination: {branch: {name: $dst}},
        description: $desc
      }')
    bb_api POST "/repositories/${workspace}/${repo}/pullrequests" -d "$payload"
    ;;

  update)
    [[ $# -ge 1 ]] || die "update requires <pr-id>"
    pr_id="$1"; shift
    title="" description="" has_title=false has_desc=false
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --title) title="$2"; has_title=true; shift 2 ;;
        --description) description="$2"; has_desc=true; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    payload="{}"
    if $has_title; then
      payload=$(echo "$payload" | jq --arg t "$title" '. + {title: $t}')
    fi
    if $has_desc; then
      payload=$(echo "$payload" | jq --arg d "$description" '. + {description: $d}')
    fi
    bb_api PUT "/repositories/${workspace}/${repo}/pullrequests/${pr_id}" -d "$payload"
    ;;

  merge)
    [[ $# -ge 1 ]] || die "merge requires <pr-id>"
    pr_id="$1"; shift
    strategy="merge_commit" close_source="true"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --strategy) strategy="$2"; shift 2 ;;
        --close-source) close_source="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    payload=$(jq -n \
      --arg s "$strategy" \
      --argjson c "$close_source" \
      '{merge_strategy: $s, close_source_branch: $c}')
    bb_api POST "/repositories/${workspace}/${repo}/pullrequests/${pr_id}/merge" -d "$payload"
    ;;

  decline)
    [[ $# -ge 1 ]] || die "decline requires <pr-id>"
    pr_id="$1"
    bb_api POST "/repositories/${workspace}/${repo}/pullrequests/${pr_id}/decline"
    ;;

  approve)
    [[ $# -ge 1 ]] || die "approve requires <pr-id>"
    pr_id="$1"
    bb_api POST "/repositories/${workspace}/${repo}/pullrequests/${pr_id}/approve"
    ;;

  unapprove)
    [[ $# -ge 1 ]] || die "unapprove requires <pr-id>"
    pr_id="$1"
    bb_api DELETE "/repositories/${workspace}/${repo}/pullrequests/${pr_id}/approve"
    ;;

  commits)
    [[ $# -ge 1 ]] || die "commits requires <pr-id>"
    pr_id="$1"
    bb_api GET "/repositories/${workspace}/${repo}/pullrequests/${pr_id}/commits"
    ;;

  statuses)
    [[ $# -ge 1 ]] || die "statuses requires <pr-id>"
    pr_id="$1"
    bb_api GET "/repositories/${workspace}/${repo}/pullrequests/${pr_id}/statuses"
    ;;

  activity)
    [[ $# -ge 1 ]] || die "activity requires <pr-id>"
    pr_id="$1"
    bb_api GET "/repositories/${workspace}/${repo}/pullrequests/${pr_id}/activity"
    ;;

  *)
    die "Unknown action: $action. Run with --help for usage."
    ;;
esac
