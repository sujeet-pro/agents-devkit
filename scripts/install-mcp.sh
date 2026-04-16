#!/bin/bash
set -euo pipefail

# ADK MCP Config Installer
# Merges MCP server configurations into agent config files.
#
# Usage:
#   ./scripts/install-mcp.sh --agent <agent> [--servers <list>] [--dry-run]
#
# Options:
#   --agent <agent>     Target agent: claude-code, cursor, claude-desktop, codex
#                       Can be comma-separated for multiple agents
#   --servers <list>    Comma-separated server names (default: all in mcp-config/servers/)
#   --dry-run           Show what would be done without making changes
#   --help              Show this help

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MCP_DIR="$REPO_DIR/mcp-config/servers"

AGENT_ARG=""
SERVERS=""
DRY_RUN=false

log() { echo "[mcp] $*"; }

post_install_note() {
    local server_name="$1"
    case "$server_name" in
        brainstorming)
            log "note: set BRAINSTORMING_MCP_ROOT to the local mcp-brainstorming checkout before using this server"
            ;;
    esac
}

get_config_path() {
    local agent="$1"
    case "$agent" in
        claude-code)
            echo "$HOME/.claude/mcp.json"
            ;;
        cursor)
            echo "$(pwd)/.cursor/mcp.json"
            ;;
        claude-desktop)
            if [ "$(uname)" = "Darwin" ]; then
                echo "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
            else
                echo "$HOME/.config/claude-desktop/config.json"
            fi
            ;;
        codex)
            echo "$HOME/.codex/mcp.json"
            ;;
        *)
            echo ""
            ;;
    esac
}

get_servers_key() {
    local agent="$1"
    case "$agent" in
        claude-desktop)
            echo "mcpServers"
            ;;
        *)
            echo "mcpServers"
            ;;
    esac
}

merge_server() {
    local config_path="$1"
    local server_name="$2"
    local server_file="$MCP_DIR/$server_name.json"
    local servers_key="$3"

    if [ ! -f "$server_file" ]; then
        log "warn: server config not found: $server_file"
        return 0
    fi

    # Check if config file exists, create if not
    if [ ! -f "$config_path" ]; then
        if [ "$DRY_RUN" = true ]; then
            log "[dry-run] create: $config_path with server $server_name"
            return 0
        fi
        mkdir -p "$(dirname "$config_path")"
        echo "{\"$servers_key\":{}}" > "$config_path"
        log "created: $config_path"
    fi

    # Check if server already exists in config
    if python3 -c "
import json, sys
with open('$config_path') as f:
    cfg = json.load(f)
servers = cfg.get('$servers_key', {})
sys.exit(0 if '$server_name' in servers else 1)
" 2>/dev/null; then
        log "skip: $server_name already in $config_path"
        post_install_note "$server_name"
        return 0
    fi

    if [ "$DRY_RUN" = true ]; then
        log "[dry-run] add: $server_name -> $config_path"
        post_install_note "$server_name"
        return 0
    fi

    # Merge server into config using python3 for reliable JSON manipulation
    python3 -c "
import json
with open('$config_path') as f:
    cfg = json.load(f)
with open('$server_file') as f:
    server = json.load(f)

# Remove non-standard fields
server.pop('description', None)

if '$servers_key' not in cfg:
    cfg['$servers_key'] = {}
cfg['$servers_key']['$server_name'] = server

with open('$config_path', 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')
"
    log "added: $server_name -> $config_path"
    post_install_note "$server_name"
}

install_for_agent() {
    local agent="$1"
    local config_path
    config_path="$(get_config_path "$agent")"
    local servers_key
    servers_key="$(get_servers_key "$agent")"

    if [ -z "$config_path" ]; then
        log "error: unknown agent '$agent'"
        return 1
    fi

    log "installing MCP servers for $agent ($config_path)..."

    local server_list
    if [ -n "$SERVERS" ]; then
        server_list="${SERVERS//,/ }"
    else
        server_list=""
        for f in "$MCP_DIR"/*.json; do
            [ -f "$f" ] || continue
            server_list="$server_list $(basename "$f" .json)"
        done
    fi

    for server in $server_list; do
        merge_server "$config_path" "$server" "$servers_key"
    done
}

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --agent) AGENT_ARG="$2"; shift 2 ;;
        --servers) SERVERS="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --help)
            head -14 "$0" | tail -12
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [ -z "$AGENT_ARG" ]; then
    echo "Error: --agent is required"
    echo "Usage: ./scripts/install-mcp.sh --agent claude-code,cursor"
    exit 1
fi

for agent in ${AGENT_ARG//,/ }; do
    install_for_agent "$agent"
done

log "done."
