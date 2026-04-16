#!/bin/bash
set -euo pipefail

# ADK Symlink Uninstaller
# Removes all adk-* symlinks that point into this repo from runtime directories.
#
# Usage:
#   ./scripts/uninstall.sh [--agents <list>] [--global] [--target <path>] [--dry-run]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

AGENTS=""
GLOBAL=false
DRY_RUN=false
TARGET=""

skills_dir_for_agent() {
    local agent="$1"
    local prefix="$2"
    case "$agent" in
        claude) printf '%s\n' "$prefix/.claude/skills" ;;
        cursor) printf '%s\n' "$prefix/.cursor/skills" ;;
        codex) printf '%s\n' "$prefix/.codex/skills" ;;
        agents) printf '%s\n' "$prefix/.agents/skills" ;;
        antigravity) printf '%s\n' "$prefix/.antigravity/skills" ;;
        junie) printf '%s\n' "$prefix/.junie/skills" ;;
        *) return 1 ;;
    esac
}

agents_dir_for_agent() {
    local agent="$1"
    local prefix="$2"
    case "$agent" in
        claude) printf '%s\n' "$prefix/.claude/agents" ;;
        cursor) printf '%s\n' "$prefix/.cursor/agents" ;;
        codex) printf '%s\n' "$prefix/.codex/agents" ;;
        *) return 1 ;;
    esac
}

hook_target_path_for_agent() {
    local agent="$1"
    local prefix="$2"
    case "$agent" in
        claude) printf '%s\n' "$prefix/.claude/settings.json" ;;
        cursor) printf '%s\n' "$prefix/.cursor/hooks.json" ;;
        codex) printf '%s\n' "$prefix/.codex/hooks.json" ;;
        *) return 1 ;;
    esac
}

log() { echo "[uninstall] $*"; }

removed=0

remove_adk_links() {
    local dir="$1"
    [ -d "$dir" ] || return 0

    for link in "$dir"/adk-*; do
        [ -L "$link" ] || continue
        local target
        target="$(readlink "$link")"

        # Only remove symlinks that point into this repo
        case "$target" in
            "$REPO_DIR"*)
                if [ "$DRY_RUN" = true ]; then
                    log "[dry-run] remove: $link"
                else
                    rm "$link"
                    log "removed: $link"
                fi
                ((removed++)) || true
                ;;
            *)
                log "skip: $link (points outside this repo)"
                ;;
        esac
    done
}

remove_repo_symlink() {
    local target_path="$1"
    [ -L "$target_path" ] || return 0

    local target
    target="$(readlink "$target_path")"
    case "$target" in
        "$REPO_DIR"*)
            if [ "$DRY_RUN" = true ]; then
                log "[dry-run] remove: $target_path"
            else
                rm "$target_path"
                log "removed: $target_path"
            fi
            ((removed++)) || true
            ;;
        *)
            log "skip: $target_path (points outside this repo)"
            ;;
    esac
}

uninstall_agent() {
    local agent="$1"
    local skills_dir agents_dir hooks_path
    skills_dir="$(skills_dir_for_agent "$agent" "$PREFIX" 2>/dev/null || true)"
    agents_dir="$(agents_dir_for_agent "$agent" "$PREFIX" 2>/dev/null || true)"
    hooks_path="$(hook_target_path_for_agent "$agent" "$PREFIX" 2>/dev/null || true)"
    for dir in "$skills_dir" "$agents_dir"; do
        [ -n "$dir" ] && remove_adk_links "$dir"
    done
    [ -n "$hooks_path" ] && remove_repo_symlink "$hooks_path"
}

uninstall_custom_target() {
    local target="$1"
    for subdir in skills agents-claude agents-cursor agents-codex; do
        remove_adk_links "$target/$subdir"
    done
    remove_repo_symlink "$target/hooks/settings.json"
    remove_repo_symlink "$target/hooks-cursor/hooks.json"
    remove_repo_symlink "$target/hooks-codex/hooks.json"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --agents) AGENTS="$2"; shift 2 ;;
        --global) GLOBAL=true; shift ;;
        --target) TARGET="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --help)
            head -8 "$0" | tail -6
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

PREFIX="$(pwd)"
[ "$GLOBAL" = true ] && PREFIX="$HOME"

if [ -n "$TARGET" ]; then
    uninstall_custom_target "$TARGET"
elif [ -n "$AGENTS" ]; then
    for agent in ${AGENTS//,/ }; do
        uninstall_agent "$agent"
    done
else
    for agent in claude cursor codex agents antigravity junie; do
        uninstall_agent "$agent"
    done
fi

log "done: $removed symlinks removed"
