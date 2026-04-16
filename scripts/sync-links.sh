#!/bin/bash
set -euo pipefail

# ADK Symlink Sync
# Prunes stale symlinks and creates missing ones for all detected runtimes.
#
# Usage:
#   ./scripts/sync-links.sh [--agents <list>] [--global] [--dry-run] [--target <path>]
#
# Behavior:
#   1. Scans agent directories for existing adk-* symlinks
#   2. If a symlink points to a skill/agent no longer in this repo, removes it
#   3. If a skill/agent exists in this repo but has no symlink, creates it
#   4. Reports what changed

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GLOBAL=false
DRY_RUN=false
TARGET=""
AGENTS=""

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

agent_source_dir_for_agent() {
    local agent="$1"
    case "$agent" in
        claude) printf '%s\n' "$REPO_DIR/agents-claude" ;;
        cursor) printf '%s\n' "$REPO_DIR/agents-cursor" ;;
        codex) printf '%s\n' "$REPO_DIR/agents-codex" ;;
        *) return 1 ;;
    esac
}

agent_pattern_for_agent() {
    local agent="$1"
    case "$agent" in
        codex) printf '%s\n' "adk-*.toml" ;;
        claude|cursor) printf '%s\n' "adk-*.md" ;;
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

hook_source_path_for_agent() {
    local agent="$1"
    case "$agent" in
        claude) printf '%s\n' "$REPO_DIR/hooks/settings.json" ;;
        cursor) printf '%s\n' "$REPO_DIR/hooks/hooks-cursor/hooks.json" ;;
        codex) printf '%s\n' "$REPO_DIR/hooks/hooks-codex/hooks.json" ;;
        *) return 1 ;;
    esac
}

log() { echo "[sync] $*"; }

added=0
removed=0
skipped=0

prune_stale() {
    local dir="$1"
    [ -d "$dir" ] || return 0

    for link in "$dir"/adk-*; do
        [ -L "$link" ] || continue
        local target
        target="$(readlink "$link")"

        # Check if the target still exists
        if [ ! -e "$target" ]; then
            if [ "$DRY_RUN" = true ]; then
                log "[dry-run] prune: $link (target $target gone)"
            else
                rm "$link"
                log "pruned: $link"
            fi
            ((removed++)) || true
        fi
    done
}

add_missing() {
    local source_dir="$1"
    local target_dir="$2"
    local pattern="$3"

    [ -d "$source_dir" ] || return 0
    [ -d "$target_dir" ] || return 0

    for item in "$source_dir"/$pattern; do
        [ -e "$item" ] || continue
        local name
        name="$(basename "$item")"

        if [ ! -e "$target_dir/$name" ]; then
            if [ "$DRY_RUN" = true ]; then
                log "[dry-run] add: $target_dir/$name -> $item"
            else
                ln -s "$item" "$target_dir/$name"
                log "added: $target_dir/$name"
            fi
            ((added++)) || true
        else
            ((skipped++)) || true
        fi
    done
}

sync_single_file() {
    local source="$1"
    local target="$2"

    [ -f "$source" ] || return 0

    if [ -L "$target" ]; then
        local existing
        existing="$(readlink "$target")"
        if [ "$existing" = "$source" ]; then
            ((skipped++)) || true
            return 0
        fi
        case "$existing" in
            "$REPO_DIR"*)
                if [ "$DRY_RUN" = true ]; then
                    log "[dry-run] update: $target -> $source (was $existing)"
                else
                    rm "$target"
                    mkdir -p "$(dirname "$target")"
                    ln -s "$source" "$target"
                    log "updated: $target"
                fi
                ((added++)) || true
                ;;
            *)
                ((skipped++)) || true
                ;;
        esac
    elif [ -e "$target" ]; then
        ((skipped++)) || true
    else
        if [ "$DRY_RUN" = true ]; then
            log "[dry-run] add: $target -> $source"
        else
            mkdir -p "$(dirname "$target")"
            ln -s "$source" "$target"
            log "added: $target"
        fi
        ((added++)) || true
    fi
}

prune_stale_file() {
    local source="$1"
    local target="$2"

    if [ -L "$target" ] && [ ! -e "$source" ]; then
        if [ "$DRY_RUN" = true ]; then
            log "[dry-run] prune: $target (source $source gone)"
        else
            rm "$target"
            log "pruned: $target"
        fi
        ((removed++)) || true
    fi
}

sync_agent_projections() {
    local agent="$1"
    local target_dir="$2"
    local source_dir pattern
    source_dir="$(agent_source_dir_for_agent "$agent" 2>/dev/null || true)"
    pattern="$(agent_pattern_for_agent "$agent" 2>/dev/null || true)"

    if [ -z "$target_dir" ] || [ ! -d "$target_dir" ] || [ ! -d "$source_dir" ]; then
        return 0
    fi

    prune_stale "$target_dir"
    add_missing "$source_dir" "$target_dir" "$pattern"
}

sync_hook_projection() {
    local agent="$1"
    local source target
    source="$(hook_source_path_for_agent "$agent" 2>/dev/null || true)"
    target="$(hook_target_path_for_agent "$agent" "$PREFIX" 2>/dev/null || true)"

    [ -n "$target" ] || return 0
    prune_stale_file "$source" "$target"
    sync_single_file "$source" "$target"
}

sync_agent() {
    local agent="$1"
    local skills_dir agents_dir
    skills_dir="$(skills_dir_for_agent "$agent" "$PREFIX" 2>/dev/null || true)"
    agents_dir="$(agents_dir_for_agent "$agent" "$PREFIX" 2>/dev/null || true)"

    if [ -n "$skills_dir" ] && [ -d "$skills_dir" ]; then
        prune_stale "$skills_dir"
        add_missing "$REPO_DIR/skills" "$skills_dir" "adk-*/"
    fi

    sync_agent_projections "$agent" "$agents_dir"
    sync_hook_projection "$agent"
}

sync_custom_target() {
    local target="$1"
    for subdir in skills agents-claude agents-cursor agents-codex; do
        if [ ! -d "$target/$subdir" ]; then
            continue
        fi

        prune_stale "$target/$subdir"
        if [ "$subdir" = "skills" ]; then
            add_missing "$REPO_DIR/$subdir" "$target/$subdir" "adk-*/"
        elif [ "$subdir" = "agents-claude" ]; then
            add_missing "$REPO_DIR/$subdir" "$target/$subdir" "adk-*.md"
        elif [ "$subdir" = "agents-cursor" ]; then
            add_missing "$REPO_DIR/$subdir" "$target/$subdir" "adk-*.md"
        else
            add_missing "$REPO_DIR/$subdir" "$target/$subdir" "adk-*.toml"
        fi
    done

    if [ -d "$target/hooks" ]; then
        sync_single_file "$REPO_DIR/hooks/settings.json" "$target/hooks/settings.json"
    fi
    if [ -d "$target/hooks-cursor" ]; then
        sync_single_file "$REPO_DIR/hooks/hooks-cursor/hooks.json" "$target/hooks-cursor/hooks.json"
    fi
    if [ -d "$target/hooks-codex" ]; then
        sync_single_file "$REPO_DIR/hooks/hooks-codex/hooks.json" "$target/hooks-codex/hooks.json"
    fi
}

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --agents) AGENTS="$2"; shift 2 ;;
        --global) GLOBAL=true; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        --target) TARGET="$2"; shift 2 ;;
        --help)
            head -12 "$0" | tail -10
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

PREFIX="$(pwd)"
[ "$GLOBAL" = true ] && PREFIX="$HOME"

if [ -n "$TARGET" ]; then
    sync_custom_target "$TARGET"
else
    if [ -n "$AGENTS" ]; then
        AGENT_LIST="${AGENTS//,/ }"
    else
        AGENT_LIST="claude cursor codex agents antigravity junie"
    fi
    for agent in $AGENT_LIST; do
        sync_agent "$agent"
    done
fi

log "sync complete: $added added, $removed removed, $skipped unchanged"
