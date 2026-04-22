#!/usr/bin/env bash
# validate-markdown.sh — run `pagesmith-core validate` on a markdown source or
# directory, auto-installing @pagesmith/core globally (with a y/N prompt) when
# the CLI is not already on PATH.
#
# Usage:
#   validate-markdown.sh <file-or-dir> [extra pagesmith-core validate flags...]
#
# Examples:
#   validate-markdown.sh content/
#   validate-markdown.sh content/posts/hello.md
#   validate-markdown.sh content/ --strict --json
#   AUTO_YES=1 validate-markdown.sh content/
#
# Env vars:
#   PAGESMITH_CORE_VERSION  Pinned @pagesmith/core version. Default: 0.9.9
#   AUTO_YES                When set to 1, skip the interactive install prompt.
#
# Exit codes:
#   0 — every validated file is clean
#   1 — validation surfaced one or more failures
#   2 — install was declined or failed
#   3 — usage / invalid arguments

set -euo pipefail

PAGESMITH_CORE_VERSION="${PAGESMITH_CORE_VERSION:-0.9.9}"
AUTO_YES="${AUTO_YES:-0}"

err()  { printf 'ERROR: %s\n' "$*" >&2; }
info() { printf '%s\n' "$*" >&2; }

if [[ $# -lt 1 ]]; then
  err "usage: $0 <file-or-dir> [extra pagesmith-core validate flags...]"
  exit 3
fi

TARGET="$1"; shift
if [[ ! -e "$TARGET" ]]; then
  err "target does not exist: $TARGET"
  exit 3
fi

ensure_pagesmith_core() {
  if command -v pagesmith-core >/dev/null 2>&1; then
    local installed_version
    installed_version="$(pagesmith-core --version 2>/dev/null | head -n1 | tr -d 'v ' || echo unknown)"
    info "[markdown] using pagesmith-core v${installed_version} ($(command -v pagesmith-core))"
    if [[ "$installed_version" != "$PAGESMITH_CORE_VERSION" && "$installed_version" != "unknown" ]]; then
      info "[markdown] WARNING: installed v${installed_version}, this skill is pinned to v${PAGESMITH_CORE_VERSION}."
      info "[markdown] Re-install pinned version with: npm install -g @pagesmith/core@${PAGESMITH_CORE_VERSION}"
    fi
    return 0
  fi

  info "[markdown] @pagesmith/core (pagesmith-core) is not installed globally."
  info "[markdown] This skill needs: npm install -g @pagesmith/core@${PAGESMITH_CORE_VERSION}"

  local reply
  if [[ "$AUTO_YES" == "1" ]]; then
    reply="y"
  else
    if [[ ! -t 0 ]]; then
      err "non-interactive shell and AUTO_YES != 1 — refuse to install @pagesmith/core silently."
      err "either re-run with AUTO_YES=1, or install manually: npm install -g @pagesmith/core@${PAGESMITH_CORE_VERSION}"
      exit 2
    fi
    printf '[markdown] install @pagesmith/core@%s globally now? [y/N] ' "$PAGESMITH_CORE_VERSION" >&2
    read -r reply
  fi

  case "$reply" in
    y|Y|yes|YES)
      info "[markdown] installing @pagesmith/core@${PAGESMITH_CORE_VERSION}…"
      if ! npm install -g "@pagesmith/core@${PAGESMITH_CORE_VERSION}"; then
        err "global install failed."
        exit 2
      fi
      ;;
    *)
      err "user declined install. exiting."
      exit 2
      ;;
  esac
}

ensure_pagesmith_core

# Force non-interactive output unless the caller already set it; --json still
# wins when present in extra args.
export PAGESMITH_NON_INTERACTIVE="${PAGESMITH_NON_INTERACTIVE:-1}"

info "[markdown] validate: pagesmith-core validate \"$TARGET\" $*"
if pagesmith-core validate "$TARGET" "$@"; then
  info "[markdown] OK — $TARGET is clean."
  exit 0
else
  rc=$?
  err "pagesmith-core validate failed (exit $rc). See output above."
  exit 1
fi
