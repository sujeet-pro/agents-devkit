#!/usr/bin/env bash
set -euo pipefail

# Usage: bash issues.sh <action> [args...]
# Actions: get, create, update, delete, transitions, transition, assign, link,
#          watchers, add-watcher, worklog, add-worklog

die() { echo "Error: $*" >&2; exit 1; }

usage() {
  cat >&2 <<'USAGE'
Usage: bash issues.sh <action> [args...]

Actions:
  get             --key KEY [--expand FIELDS]
  create          --project KEY --type NAME --summary TEXT [--description TEXT] [--priority NAME] [--assignee ACCOUNT_ID] [--labels L1,L2]
  update          --key KEY [--summary TEXT] [--description TEXT] [--priority NAME] [--assignee ACCOUNT_ID] [--labels L1,L2]
  delete          --key KEY
  transitions     --key KEY
  transition      --key KEY --transition-id ID [--comment TEXT] [--resolution NAME]
  assign          --key KEY --account-id ID
  link            --from KEY --to KEY --type NAME
  watchers        --key KEY
  add-watcher     --key KEY --account-id ID
  worklog         --key KEY
  add-worklog     --key KEY --time-spent DURATION [--comment TEXT]
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

text_to_adf() {
  local text="$1"
  local paragraphs=""
  local first=true
  while IFS= read -r line || [[ -n "$line" ]]; do
    local escaped
    escaped=$(jq -Rrs '.' <<< "$line" | sed 's/^"//;s/"$//')
    if [[ "$first" == "true" ]]; then
      first=false
    else
      paragraphs+=","
    fi
    paragraphs+="{\"type\":\"paragraph\",\"content\":[{\"type\":\"text\",\"text\":\"${escaped}\"}]}"
  done <<< "$text"
  echo "{\"type\":\"doc\",\"version\":1,\"content\":[${paragraphs}]}"
}

ACTION="${1:-}"; shift 2>/dev/null || true
[[ -n "$ACTION" ]] || usage

case "$ACTION" in
  get)
    key="" expand=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --expand) expand="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "get requires --key"
    url="${API}/issue/${key}"
    [[ -n "$expand" ]] && url+="?expand=${expand}"
    jira_api GET "$url"
    ;;

  create)
    project="" type="" summary="" description="" priority="" assignee="" labels=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="$2"; shift 2 ;;
        --type) type="$2"; shift 2 ;;
        --summary) summary="$2"; shift 2 ;;
        --description) description="$2"; shift 2 ;;
        --priority) priority="$2"; shift 2 ;;
        --assignee) assignee="$2"; shift 2 ;;
        --labels) labels="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$project" ]] || die "create requires --project"
    [[ -n "$type" ]] || die "create requires --type"
    [[ -n "$summary" ]] || die "create requires --summary"

    fields=$(jq -n \
      --arg project "$project" \
      --arg type "$type" \
      --arg summary "$summary" \
      '{project: {key: $project}, summary: $summary, issuetype: {name: $type}}')

    if [[ -n "$description" ]]; then
      adf=$(text_to_adf "$description")
      fields=$(echo "$fields" | jq --argjson desc "$adf" '.description = $desc')
    fi
    if [[ -n "$priority" ]]; then
      fields=$(echo "$fields" | jq --arg p "$priority" '.priority = {name: $p}')
    fi
    if [[ -n "$assignee" ]]; then
      fields=$(echo "$fields" | jq --arg a "$assignee" '.assignee = {accountId: $a}')
    fi
    if [[ -n "$labels" ]]; then
      labels_json=$(echo "$labels" | tr ',' '\n' | jq -R . | jq -s .)
      fields=$(echo "$fields" | jq --argjson l "$labels_json" '.labels = $l')
    fi

    payload=$(jq -n --argjson f "$fields" '{fields: $f}')
    jira_api POST "${API}/issue" -d "$payload"
    ;;

  update)
    key="" summary="" description="" priority="" assignee="" labels=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --summary) summary="$2"; shift 2 ;;
        --description) description="$2"; shift 2 ;;
        --priority) priority="$2"; shift 2 ;;
        --assignee) assignee="$2"; shift 2 ;;
        --labels) labels="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "update requires --key"

    fields="{}"
    if [[ -n "$summary" ]]; then
      fields=$(echo "$fields" | jq --arg s "$summary" '.summary = $s')
    fi
    if [[ -n "$description" ]]; then
      adf=$(text_to_adf "$description")
      fields=$(echo "$fields" | jq --argjson desc "$adf" '.description = $desc')
    fi
    if [[ -n "$priority" ]]; then
      fields=$(echo "$fields" | jq --arg p "$priority" '.priority = {name: $p}')
    fi
    if [[ -n "$assignee" ]]; then
      fields=$(echo "$fields" | jq --arg a "$assignee" '.assignee = {accountId: $a}')
    fi
    if [[ -n "$labels" ]]; then
      labels_json=$(echo "$labels" | tr ',' '\n' | jq -R . | jq -s .)
      fields=$(echo "$fields" | jq --argjson l "$labels_json" '.labels = $l')
    fi

    payload=$(jq -n --argjson f "$fields" '{fields: $f}')
    result=$(jira_api PUT "${API}/issue/${key}" -d "$payload")
    if [[ -z "$result" ]]; then
      echo '{"status":"updated"}'
    else
      echo "$result"
    fi
    ;;

  delete)
    key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "delete requires --key"
    result=$(jira_api DELETE "${API}/issue/${key}")
    if [[ -z "$result" ]]; then
      echo '{"status":"deleted"}'
    else
      echo "$result"
    fi
    ;;

  transitions)
    key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "transitions requires --key"
    jira_api GET "${API}/issue/${key}/transitions"
    ;;

  transition)
    key="" transition_id="" comment="" resolution=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --transition-id) transition_id="$2"; shift 2 ;;
        --comment) comment="$2"; shift 2 ;;
        --resolution) resolution="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "transition requires --key"
    [[ -n "$transition_id" ]] || die "transition requires --transition-id"

    payload=$(jq -n --arg tid "$transition_id" '{transition: {id: $tid}}')

    if [[ -n "$resolution" ]]; then
      payload=$(echo "$payload" | jq --arg r "$resolution" '.fields = {resolution: {name: $r}}')
    fi
    if [[ -n "$comment" ]]; then
      adf=$(text_to_adf "$comment")
      payload=$(echo "$payload" | jq --argjson c "$adf" '.update = {comment: [{add: {body: $c}}]}')
    fi

    result=$(jira_api POST "${API}/issue/${key}/transitions" -d "$payload")
    if [[ -z "$result" ]]; then
      echo '{"status":"transitioned"}'
    else
      echo "$result"
    fi
    ;;

  assign)
    key="" account_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --account-id) account_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "assign requires --key"
    [[ -n "$account_id" ]] || die "assign requires --account-id"
    payload=$(jq -n --arg a "$account_id" '{accountId: $a}')
    result=$(jira_api PUT "${API}/issue/${key}/assignee" -d "$payload")
    if [[ -z "$result" ]]; then
      echo '{"status":"assigned"}'
    else
      echo "$result"
    fi
    ;;

  link)
    from="" to="" link_type=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --from) from="$2"; shift 2 ;;
        --to) to="$2"; shift 2 ;;
        --type) link_type="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$from" ]] || die "link requires --from"
    [[ -n "$to" ]] || die "link requires --to"
    [[ -n "$link_type" ]] || die "link requires --type"
    payload=$(jq -n \
      --arg lt "$link_type" \
      --arg inward "$from" \
      --arg outward "$to" \
      '{type: {name: $lt}, inwardIssue: {key: $inward}, outwardIssue: {key: $outward}}')
    result=$(jira_api POST "${API}/issueLink" -d "$payload")
    if [[ -z "$result" ]]; then
      echo '{"status":"linked"}'
    else
      echo "$result"
    fi
    ;;

  watchers)
    key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "watchers requires --key"
    jira_api GET "${API}/issue/${key}/watchers"
    ;;

  add-watcher)
    key="" account_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --account-id) account_id="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "add-watcher requires --key"
    [[ -n "$account_id" ]] || die "add-watcher requires --account-id"
    result=$(jira_api POST "${API}/issue/${key}/watchers" -d "\"${account_id}\"")
    if [[ -z "$result" ]]; then
      echo '{"status":"watcher_added"}'
    else
      echo "$result"
    fi
    ;;

  worklog)
    key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "worklog requires --key"
    jira_api GET "${API}/issue/${key}/worklog"
    ;;

  add-worklog)
    key="" time_spent="" comment=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        --time-spent) time_spent="$2"; shift 2 ;;
        --comment) comment="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "add-worklog requires --key"
    [[ -n "$time_spent" ]] || die "add-worklog requires --time-spent"

    payload=$(jq -n --arg ts "$time_spent" '{timeSpent: $ts}')
    if [[ -n "$comment" ]]; then
      adf=$(text_to_adf "$comment")
      payload=$(echo "$payload" | jq --argjson c "$adf" '.comment = $c')
    fi

    jira_api POST "${API}/issue/${key}/worklog" -d "$payload"
    ;;

  *) die "Unknown action: $ACTION. Run without arguments for usage." ;;
esac
