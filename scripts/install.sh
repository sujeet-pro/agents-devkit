#!/bin/bash
set -euo pipefail

# ADK Symlink Installer
# Creates symlinks from runtime directories to this repo's skills, agents, and hooks.
#
# Usage:
#   ./scripts/install.sh [--agents <list>] [--target <path>] [--global] [--dry-run]
#
# Options:
#   --agents <list>   Comma-separated agent list: claude,cursor,codex,agents,antigravity,junie
#                     Default: auto-detect installed agents
#   --target <path>   Custom target directory for symlinks (e.g., ~/.future-agents)
#   --global          Install to global (home) directories instead of project-local
#   --dry-run         Show what would be done without making changes
#   --help            Show this help

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

AGENTS=""
TARGET=""
GLOBAL=false
DRY_RUN=false

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

usage() {
    head -14 "$0" | tail -12
    exit 0
}

log() {
    echo "[adk] $*"
}

log_dry() {
    if [ "$DRY_RUN" = true ]; then
        echo "[dry-run] $*"
    else
        echo "[adk] $*"
    fi
}

create_symlink() {
    local source="$1"
    local target="$2"
    local name
    name="$(basename "$source")"

    if [ -L "$target/$name" ]; then
        local existing
        existing="$(readlink "$target/$name")"
        if [ "$existing" = "$source" ]; then
            return 0
        fi
        log_dry "update: $target/$name -> $source (was $existing)"
        if [ "$DRY_RUN" = false ]; then
            rm "$target/$name"
            ln -s "$source" "$target/$name"
        fi
    elif [ -e "$target/$name" ]; then
        log "skip: $target/$name exists and is not a symlink"
        return 0
    else
        log_dry "link: $target/$name -> $source"
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$target"
            ln -s "$source" "$target/$name"
        fi
    fi
}

create_symlink_to_path() {
    local source="$1"
    local target_path="$2"

    if [ -L "$target_path" ]; then
        local existing
        existing="$(readlink "$target_path")"
        if [ "$existing" = "$source" ]; then
            return 0
        fi
        case "$existing" in
            "$REPO_DIR"*)
                log_dry "update: $target_path -> $source (was $existing)"
                if [ "$DRY_RUN" = false ]; then
                    rm "$target_path"
                    mkdir -p "$(dirname "$target_path")"
                    ln -s "$source" "$target_path"
                fi
                ;;
            *)
                log "skip: $target_path already points outside this repo"
                ;;
        esac
    elif [ -e "$target_path" ]; then
        log "skip: $target_path exists and is not a symlink"
        return 0
    else
        log_dry "link: $target_path -> $source"
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$(dirname "$target_path")"
            ln -s "$source" "$target_path"
        fi
    fi
}

install_agent_projections() {
    local agent="$1"
    local target_dir="$2"
    local source_dir pattern
    source_dir="$(agent_source_dir_for_agent "$agent" 2>/dev/null || true)"
    pattern="$(agent_pattern_for_agent "$agent" 2>/dev/null || true)"

    if [ -z "$target_dir" ] || [ ! -d "$source_dir" ]; then
        return 0
    fi

    for agent_file in "$source_dir"/$pattern; do
        [ -f "$agent_file" ] || continue
        create_symlink "$agent_file" "$target_dir"
    done
}

install_hook_projection() {
    local agent="$1"
    local target_path="$2"
    local source_path
    source_path="$(hook_source_path_for_agent "$agent" 2>/dev/null || true)"

    if [ -z "$target_path" ] || [ ! -f "$source_path" ]; then
        return 0
    fi

    create_symlink_to_path "$source_path" "$target_path"
}

detect_agents() {
    local detected=()
    local prefix="$1"

    for agent in claude cursor codex agents antigravity junie; do
        local dir
        dir="$(skills_dir_for_agent "$agent" "$prefix" 2>/dev/null || true)"
        local parent
        parent="$(dirname "$dir" 2>/dev/null || true)"
        if [ -d "$parent" ] || [ -d "$dir" ]; then
            detected+=("$agent")
        fi
    done

    if [ ${#detected[@]} -eq 0 ]; then
        detected=(claude cursor codex)
        log "no agents detected, defaulting to: ${detected[*]}"
    else
        log "detected agents: ${detected[*]}"
    fi

    echo "${detected[*]}"
}

install_for_agent() {
    local agent="$1"
    local skills_dir agents_dir hooks_path
    skills_dir="$(skills_dir_for_agent "$agent" "$PREFIX" 2>/dev/null || true)"
    agents_dir="$(agents_dir_for_agent "$agent" "$PREFIX" 2>/dev/null || true)"
    hooks_path="$(hook_target_path_for_agent "$agent" "$PREFIX" 2>/dev/null || true)"

    if [ -z "$skills_dir" ] && [ -n "$TARGET" ]; then
        skills_dir="$TARGET/skills"
    fi

    if [ -z "$skills_dir" ]; then
        log "skip: unknown agent '$agent'"
        return 0
    fi

    log_dry "installing for $agent..."

    # Symlink skills
    if [ -d "$REPO_DIR/skills" ]; then
        for skill_dir in "$REPO_DIR"/skills/adk-*/; do
            [ -d "$skill_dir" ] || continue
            create_symlink "$skill_dir" "$skills_dir"
        done
    fi

    # Symlink runtime-specific custom agents
    install_agent_projections "$agent" "$agents_dir"

    # Symlink runtime-specific hooks
    install_hook_projection "$agent" "$hooks_path"

}

install_custom_target() {
    local target="$1"
    log_dry "installing to custom target: $target"

    mkdir -p \
        "$target/skills" \
        "$target/agents-claude" \
        "$target/agents-cursor" \
        "$target/agents-codex" \
        "$target/hooks" \
        "$target/hooks-cursor" \
        "$target/hooks-codex" 2>/dev/null || true

    for skill_dir in "$REPO_DIR"/skills/adk-*/; do
        [ -d "$skill_dir" ] || continue
        create_symlink "$skill_dir" "$target/skills"
    done

    for agent_file in "$REPO_DIR"/agents-claude/adk-*.md; do
        [ -f "$agent_file" ] || continue
        create_symlink "$agent_file" "$target/agents-claude"
    done

    for agent_file in "$REPO_DIR"/agents-cursor/adk-*.md; do
        [ -f "$agent_file" ] || continue
        create_symlink "$agent_file" "$target/agents-cursor"
    done

    for agent_file in "$REPO_DIR"/agents-codex/adk-*.toml; do
        [ -f "$agent_file" ] || continue
        create_symlink "$agent_file" "$target/agents-codex"
    done

    [ -f "$REPO_DIR/hooks/settings.json" ] && create_symlink "$REPO_DIR/hooks/settings.json" "$target/hooks"
    [ -f "$REPO_DIR/hooks/hooks-cursor/hooks.json" ] && create_symlink "$REPO_DIR/hooks/hooks-cursor/hooks.json" "$target/hooks-cursor"
    [ -f "$REPO_DIR/hooks/hooks-codex/hooks.json" ] && create_symlink "$REPO_DIR/hooks/hooks-codex/hooks.json" "$target/hooks-codex"
}

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --agents)
            AGENTS="$2"
            shift 2
            ;;
        --target)
            TARGET="$2"
            shift 2
            ;;
        --global)
            GLOBAL=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Determine install prefix
if [ "$GLOBAL" = true ]; then
    PREFIX="$HOME"
else
    PREFIX="$(pwd)"
fi

# Handle custom target
if [ -n "$TARGET" ]; then
    install_custom_target "$TARGET"
    log "done. Run './scripts/sync-links.sh' after repo changes to keep symlinks current."
    exit 0
fi

# Determine agent list
if [ -z "$AGENTS" ]; then
    AGENT_LIST=$(detect_agents "$PREFIX")
else
    AGENT_LIST="${AGENTS//,/ }"
fi

# Install for each agent
for agent in $AGENT_LIST; do
    install_for_agent "$agent"
done

log "done. Run './scripts/sync-links.sh' after repo changes to keep symlinks current."
