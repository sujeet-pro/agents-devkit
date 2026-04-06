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
Usage: repo.sh <action> <workspace> <repo> [options...]

Actions:
  get       <ws> <repo>                              Get repo metadata
  file      <ws> <repo> --path <path> [--ref main]   Get file contents
  branches  <ws> <repo>                              List branches
  commits   <ws> <repo> [--branch <name>]            List commits
  diff      <ws> <repo> --spec <spec>                Compare refs (e.g., main..feature)
EOF
  exit 0
}

[[ $# -ge 1 ]] || usage

action="$1"; shift

[[ "$action" == "--help" ]] && usage

[[ $# -ge 2 ]] || die "Requires at least: <workspace> <repo>"
workspace="$1"; shift
repo="$1"; shift

repo_path="/repositories/${workspace}/${repo}"

case "$action" in
  get)
    bb_api GET "${repo_path}"
    ;;

  file)
    path="" ref="main"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --path) path="$2"; shift 2 ;;
        --ref) ref="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$path" ]] || die "file requires --path"
    bb_raw "${repo_path}/src/${ref}/${path}"
    ;;

  branches)
    bb_api GET "${repo_path}/refs/branches"
    ;;

  commits)
    branch=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --branch) branch="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    if [[ -n "$branch" ]]; then
      bb_api GET "${repo_path}/commits/${branch}"
    else
      bb_api GET "${repo_path}/commits"
    fi
    ;;

  diff)
    spec=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --spec) spec="$2"; shift 2 ;;
        *) die "Unknown option: $1" ;;
      esac
    done
    [[ -n "$spec" ]] || die "diff requires --spec (e.g., main..feature-branch)"
    bb_raw "${repo_path}/diff/${spec}"
    ;;

  *)
    die "Unknown action: $action. Run with --help for usage."
    ;;
esac
