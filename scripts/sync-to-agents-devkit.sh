#!/usr/bin/env bash
set -euo pipefail

# Sync this repo's current working-tree files into agents-devkit as a normal git diff,
# preserving /Users/sujeet/personal/agents-devkit/.git and committing the result.
#
# Command:
#   ./scripts/sync-to-agents-devkit.sh
#
# Optional:
#   # Override the default commit message, which is copied from this repo's latest commit.
#   COMMIT_MESSAGE="chore: sync claude-marketplace snapshot" ./scripts/sync-to-agents-devkit.sh
#   NO_COMMIT=1 ./scripts/sync-to-agents-devkit.sh
#   DRY_RUN=1 ./scripts/sync-to-agents-devkit.sh
#   NO_PUSH=1 ./scripts/sync-to-agents-devkit.sh

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TARGET_ROOT_INPUT="${1:-/Users/sujeet/personal/agents-devkit}"

default_commit_message() {
  if git -C "$SOURCE_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$SOURCE_ROOT" log -1 --format=%B
  else
    printf "%s\n" "chore: sync claude-marketplace snapshot"
  fi
}

COMMIT_MESSAGE="${COMMIT_MESSAGE:-$(default_commit_message)}"

if ! command -v rsync >/dev/null 2>&1; then
  echo "ERROR: rsync is required." >&2
  exit 1
fi

if [[ ! -d "$TARGET_ROOT_INPUT" ]]; then
  echo "ERROR: target directory does not exist: $TARGET_ROOT_INPUT" >&2
  exit 1
fi

TARGET_ROOT="$(cd "$TARGET_ROOT_INPUT" && pwd -P)"

if [[ ! -d "$TARGET_ROOT/.git" ]]; then
  echo "ERROR: target is not a git repository: $TARGET_ROOT" >&2
  exit 1
fi

if [[ "$SOURCE_ROOT" == "$TARGET_ROOT" ]]; then
  echo "ERROR: source and target are the same directory." >&2
  exit 1
fi

if [[ -n "$(git -C "$TARGET_ROOT" status --porcelain)" && "${ALLOW_DIRTY_TARGET:-0}" != "1" ]]; then
  echo "ERROR: target has uncommitted changes. Commit/stash them first, or rerun with ALLOW_DIRTY_TARGET=1." >&2
  git -C "$TARGET_ROOT" status --short >&2
  exit 1
fi

rsync_args=(
  -a
  --delete
  --itemize-changes
  --exclude=.git/
  --exclude=node_modules/
  --exclude=gh-pages/
  --exclude=.temp/
  --exclude=.cache/
  --exclude=dist/
  --exclude=build/
  --exclude=coverage/
  --exclude=.DS_Store
  --exclude=.env
  --exclude=.env.*
  --exclude=.idea/
  --exclude=.vscode/
  --exclude=*.log
)

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  rsync_args+=(--dry-run)
fi

echo "Syncing current files:"
echo "  from: $SOURCE_ROOT/"
echo "  to:   $TARGET_ROOT/"
rsync "${rsync_args[@]}" "$SOURCE_ROOT/" "$TARGET_ROOT/"

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  echo "Dry run complete. No files were changed."
  exit 0
fi

git -C "$TARGET_ROOT" add -A

if git -C "$TARGET_ROOT" diff --cached --quiet; then
  echo "No changes to commit in $TARGET_ROOT."
  exit 0
fi

echo "Staged sync diff in $TARGET_ROOT:"
git -C "$TARGET_ROOT" status --short

if [[ "${NO_COMMIT:-0}" == "1" ]]; then
  echo "NO_COMMIT=1 set; leaving changes staged in $TARGET_ROOT."
  exit 0
fi

git -C "$TARGET_ROOT" commit -m "$COMMIT_MESSAGE"

if [[ "${NO_PUSH:-0}" == "1" ]]; then
  echo "NO_PUSH=1 set; commit created but not pushed."
  exit 0
fi

git -C "$TARGET_ROOT" push origin HEAD
