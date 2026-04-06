#!/usr/bin/env bash
set -euo pipefail

# Usage: bash projects.sh <action> [args...]
# Actions: list, get, versions, create-version, components, create-component, statuses

die() { echo "Error: $*" >&2; exit 1; }

usage() {
  cat >&2 <<'USAGE'
Usage: bash projects.sh <action> [args...]

Actions:
  list                                              List all projects
  get              --key KEY                        Get project details
  versions         --key KEY                        List project versions
  create-version   --project-id ID --name NAME [--release-date DATE] [--released BOOL]
  components       --key KEY                        List project components
  create-component --project KEY --name NAME [--lead ACCOUNT_ID]
  statuses         --key KEY                        List project statuses
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

ACTION="${1:-}"; shift 2>/dev/null || true
[[ -n "$ACTION" ]] || usage

case "$ACTION" in
  list)
    jira_api GET "${API}/project?expand=lead"
    ;;

  get)
    key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "get requires --key"
    jira_api GET "${API}/project/${key}"
    ;;

  versions)
    key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "versions requires --key"
    jira_api GET "${API}/project/${key}/versions"
    ;;

  create-version)
    project_id="" name="" release_date="" released=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project-id) project_id="$2"; shift 2 ;;
        --name) name="$2"; shift 2 ;;
        --release-date) release_date="$2"; shift 2 ;;
        --released) released="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$project_id" ]] || die "create-version requires --project-id"
    [[ -n "$name" ]] || die "create-version requires --name"

    payload=$(jq -n \
      --argjson pid "$project_id" \
      --arg name "$name" \
      '{projectId: $pid, name: $name}')

    if [[ -n "$release_date" ]]; then
      payload=$(echo "$payload" | jq --arg d "$release_date" '.releaseDate = $d')
    fi
    if [[ -n "$released" ]]; then
      payload=$(echo "$payload" | jq --argjson r "$released" '.released = $r')
    fi

    jira_api POST "${API}/version" -d "$payload"
    ;;

  components)
    key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "components requires --key"
    jira_api GET "${API}/project/${key}/components"
    ;;

  create-component)
    project="" name="" lead=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="$2"; shift 2 ;;
        --name) name="$2"; shift 2 ;;
        --lead) lead="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$project" ]] || die "create-component requires --project"
    [[ -n "$name" ]] || die "create-component requires --name"

    payload=$(jq -n \
      --arg project "$project" \
      --arg name "$name" \
      '{project: $project, name: $name}')

    if [[ -n "$lead" ]]; then
      payload=$(echo "$payload" | jq --arg l "$lead" '.leadAccountId = $l')
    fi

    jira_api POST "${API}/component" -d "$payload"
    ;;

  statuses)
    key=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --key) key="$2"; shift 2 ;;
        *) die "Unknown flag: $1" ;;
      esac
    done
    [[ -n "$key" ]] || die "statuses requires --key"
    jira_api GET "${API}/project/${key}/statuses"
    ;;

  *) die "Unknown action: $ACTION. Run without arguments for usage." ;;
esac
