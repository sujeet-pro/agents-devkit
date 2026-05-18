#!/usr/bin/env bash
# sync-to-personal.sh — mirror this repo (v3) into the personal clone.
#
# Usage:
#   ./scripts/sync-to-personal.sh                            # dry-run summary (default)
#   ./scripts/sync-to-personal.sh --apply                    # actually do the sync
#   ./scripts/sync-to-personal.sh --apply --dest <path>      # custom destination
#   ./scripts/sync-to-personal.sh --apply --commit "<msg>"   # also git-add + git-commit in dest
#   ./scripts/sync-to-personal.sh --apply --commit "<msg>" --push   # also git-push (asks first)
#
# Excludes:
#   .git/, .temp/, .claude/, node_modules/, gh-pages/ (and __pycache__, .DS_Store, build artifacts)
#
# Safety:
#   - Refuses to run if dest isn't a git repo.
#   - Warns (does not block) if dest has uncommitted changes — those will appear bundled with the sync diff.
#   - Never modifies dest/.git/ directly.
#   - --push asks once before pushing; never force-pushes.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${HOME}/personal/agents-devkit"
APPLY=0
COMMIT_MSG=""
PUSH=0

usage() {
  sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# //; s/^#//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)   APPLY=1 ;;
    --dest)    shift; DEST="$1" ;;
    --commit)  shift; COMMIT_MSG="$1" ;;
    --push)    PUSH=1 ;;
    -h|--help) usage; exit 0 ;;
    *)         echo "unknown arg: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

# Validate
if [ ! -d "$SRC" ]; then
  echo "ERROR: source not found: $SRC" >&2
  exit 1
fi
if [ ! -d "$DEST" ]; then
  echo "ERROR: destination not found: $DEST"  >&2
  echo "       clone the repo first:" >&2
  echo "       git clone <repo-url> $DEST" >&2
  exit 1
fi
if [ ! -d "$DEST/.git" ]; then
  echo "ERROR: $DEST is not a git repo (no .git/ dir)" >&2
  exit 1
fi
# Disallow accidentally writing back into the source
SRC_REAL="$(cd "$SRC" && pwd -P)"
DEST_REAL="$(cd "$DEST" && pwd -P)"
if [ "$SRC_REAL" = "$DEST_REAL" ]; then
  echo "ERROR: source and destination resolve to the same path: $SRC_REAL" >&2
  exit 1
fi

EXCLUDES=(
  --exclude='.git/'
  --exclude='.temp/'
  --exclude='.claude/'
  --exclude='node_modules/'
  --exclude='gh-pages/'
  --exclude='install-scratch/'
  --exclude='.DS_Store'
  --exclude='__pycache__/'
  --exclude='*.pyc'
  --exclude='*.pyo'
  --exclude='.venv/'
  --exclude='.mypy_cache/'
  --exclude='.ruff_cache/'
  --exclude='dist/'
  --exclude='build/'
  --exclude='coverage/'
  --exclude='.pagesmith/'
  --exclude='*.log'
)

# Preflight info
echo "src : $SRC_REAL"
echo "dest: $DEST_REAL"
echo

# Warn if destination has uncommitted changes
( cd "$DEST" && {
    dirty="$(git status --porcelain | wc -l | tr -d ' ')"
    if [ "$dirty" -gt 0 ]; then
      echo "WARN: dest has $dirty uncommitted file change(s). They will appear bundled with the sync diff." >&2
      echo "      run \`cd $DEST && git status\` to inspect." >&2
      echo
    fi
  }
)

# Compute the action plan with --dry-run + itemize
plan_file="$(mktemp -t adk-sync-plan.XXXXXX)"
trap 'rm -f "$plan_file"' EXIT

rsync -a --delete --dry-run --itemize-changes "${EXCLUDES[@]}" "$SRC/" "$DEST/" > "$plan_file" 2>&1 || true

# Summarize the plan. rsync --itemize tokens: `>f+++…` = new file received,
# `>f.st…` etc. = modified, `*deleting path` = deletion, `cd+++…` = new directory.
all_files=$(grep -cE '^>f'           "$plan_file" || true)
added=$(grep -cE '^>f\++ '           "$plan_file" || true)
modified=$(( all_files - added ))
deleted_total=$(grep -cE '^\*deleting ' "$plan_file" || true)
dir_added=$(grep -cE '^cd\++ '       "$plan_file" || true)
dir_deleted=$(grep -cE '^\*deleting .*/$' "$plan_file" || true)
file_deleted=$(( deleted_total - dir_deleted ))

echo "plan summary:"
echo "  files added    : $added"
echo "  files modified : $modified"
echo "  files deleted  : $file_deleted"
echo "  dirs added     : $dir_added"
echo "  dirs deleted   : $dir_deleted"
echo

# Sample of the diff (first 30 entries). Use awk; avoid `/` inside regex char classes
# so this works on macOS BSD awk + Linux GNU awk alike.
# Temporarily relax pipefail because awk | head triggers SIGPIPE on awk when head exits early.
echo "sample (first 30 changes):"
set +o pipefail
awk '{
  if (substr($0, 1, 10) == "*deleting ") {
    path = substr($0, 11)
    if (length(path) > 0 && substr(path, length(path)) == "/") {
      printf "  DELDIR %s\n", path
    } else {
      printf "  DELETE %s\n", path
    }
    next
  }
  if (match($0, /^>f\++ /)) {
    sub(/^[^ ]+ /, "")
    printf "  ADD    %s\n", $0
    next
  }
  if (substr($0, 1, 2) == ">f") {
    sub(/^[^ ]+ /, "")
    printf "  MOD    %s\n", $0
    next
  }
  if (substr($0, 1, 2) == "cd") {
    sub(/^[^ ]+ /, "")
    printf "  ADDDIR %s\n", $0
    next
  }
}' "$plan_file" | head -30
set -o pipefail
echo "  ..."
echo

if (( APPLY == 0 )); then
  echo "=== DRY RUN (no changes written) ==="
  echo "re-run with --apply to execute."
  exit 0
fi

# Apply
echo "=== APPLY ==="
# `--info=progress2` is rsync 3+; macOS ships 2.6.9. Use --stats for a final summary
# that works on both. Pipe stats through tail to keep output compact.
rsync -a --delete --stats "${EXCLUDES[@]}" "$SRC/" "$DEST/" | tail -20
echo

echo "=== git status in $DEST_REAL ==="
( cd "$DEST" && git status --short | head -30 )
echo "..."
echo "(full diff: cd $DEST && git diff --stat)"
echo

if [ -n "$COMMIT_MSG" ]; then
  echo "=== commit ==="
  ( cd "$DEST"
    git add -A
    git commit -m "$COMMIT_MSG" || echo "(nothing to commit)"
  )
  echo
fi

if (( PUSH == 1 )); then
  branch="$( cd "$DEST" && git rev-parse --abbrev-ref HEAD )"
  echo "about to push branch '$branch' to remote. press ENTER to confirm, Ctrl-C to abort."
  read -r _
  ( cd "$DEST" && git push origin "$branch" )
fi

echo "done."
