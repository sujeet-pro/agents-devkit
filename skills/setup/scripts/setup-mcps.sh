#!/usr/bin/env bash
# setup-mcps.sh — Idempotent MCP server setup, validation, and update script
# Usage: bash setup-mcps.sh [--check-only] [--server <name>] [--ide <tool>]
#
# For each MCP server:
#   1. Check if configured in the target tool's config → configure if missing
#   2. Check for package updates → update if available
#   3. Check env var tokens in ~/.zshenv → update config if tokens changed
#
# Supports: github, bitbucket, atlassian-confluence, google-drive
# IDE tools: claude, cursor, windsurf, codex (auto-detected if not specified)

set -euo pipefail

ZSHENV="${HOME}/.zshenv"
CHECK_ONLY=false
TARGET_SERVER=""
TARGET_IDE=""

# ─── IDE config paths ────────────────────────────────────────────────
# Each tool stores MCP config in a different location and format.
# All use the {"mcpServers": {...}} shape except where noted.

config_path_for_ide() {
  local ide="$1"
  case "$ide" in
    claude)   echo "${HOME}/.claude.json" ;;
    cursor)   echo "${HOME}/.cursor/mcp.json" ;;
    windsurf) echo "${HOME}/.windsurf/mcp.json" ;;
    codex)    echo "${HOME}/.codex/mcp.json" ;;
    *)        echo ""; return 1 ;;
  esac
}

# ─── Argument parsing ───────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-only) CHECK_ONLY=true; shift ;;
    --server) TARGET_SERVER="$2"; shift 2 ;;
    --ide) TARGET_IDE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# ─── IDE Auto-Detection ─────────────────────────────────────────────
detect_ide() {
  # Check for Claude Code indicators
  if [[ -n "${CLAUDE_CODE:-}" ]] || [[ -n "${CLAUDE_SKILL_DIR:-}" ]]; then
    echo "claude"
    return
  fi
  # Check for Cursor indicators
  if [[ -n "${CURSOR_SESSION:-}" ]] || [[ "${TERM_PROGRAM:-}" == "cursor" ]]; then
    echo "cursor"
    return
  fi
  # Check for Windsurf indicators
  if [[ -n "${WINDSURF_SESSION:-}" ]] || [[ "${TERM_PROGRAM:-}" == "windsurf" ]]; then
    echo "windsurf"
    return
  fi
  # Check for Codex indicators
  if [[ -n "${CODEX_SESSION:-}" ]]; then
    echo "codex"
    return
  fi
  # Fallback: detect by which tools are installed
  echo ""
}

detect_available_ides() {
  local ides=()
  [[ -f "${HOME}/.claude.json" ]] || command -v claude &>/dev/null && ides+=("claude")
  [[ -d "${HOME}/.cursor" ]] || command -v cursor &>/dev/null && ides+=("cursor")
  [[ -d "${HOME}/.windsurf" ]] && ides+=("windsurf")
  [[ -d "${HOME}/.codex" ]] || command -v codex &>/dev/null && ides+=("codex")
  echo "${ides[*]}"
}

# Resolve target IDE(s)
resolve_ides() {
  if [[ "$TARGET_IDE" == "all" ]]; then
    detect_available_ides
    return
  fi
  if [[ -n "$TARGET_IDE" ]]; then
    echo "$TARGET_IDE"
    return
  fi
  # Auto-detect
  local detected
  detected=$(detect_ide)
  if [[ -n "$detected" ]]; then
    echo "$detected"
    return
  fi
  # Could not auto-detect — list available and ask
  local available
  available=$(detect_available_ides)
  if [[ -z "$available" ]]; then
    echo "claude"  # fallback default
  else
    echo "ASK:${available}"
  fi
}

# ─── Helpers ────────────────────────────────────────────────────────

# Read an env var value from ~/.zshenv
read_zshenv_var() {
  local var_name="$1"
  if [[ -f "$ZSHENV" ]]; then
    grep -E "^export ${var_name}=" "$ZSHENV" 2>/dev/null | tail -1 | sed "s/^export ${var_name}=//" | sed 's/^"//' | sed 's/"$//' | sed "s/^'//" | sed "s/'$//"
  fi
}

# Check if an MCP server exists in a config file
server_configured() {
  local name="$1" config_file="$2"
  python3 -c "
import json, sys
try:
    with open('${config_file}') as f:
        data = json.load(f)
    servers = data.get('mcpServers', {})
    sys.exit(0 if '${name}' in servers else 1)
except:
    sys.exit(1)
" 2>/dev/null
}

# Get a value from the MCP server's env block
get_server_env_val() {
  local server="$1" key="$2" config_file="$3"
  python3 -c "
import json
with open('${config_file}') as f:
    data = json.load(f)
val = data.get('mcpServers', {}).get('${server}', {}).get('env', {}).get('${key}', '')
print(val)
" 2>/dev/null
}

# Update a single env value in the MCP server config
update_server_env_val() {
  local server="$1" key="$2" value="$3" config_file="$4"
  python3 -c "
import json
with open('${config_file}') as f:
    data = json.load(f)
data.setdefault('mcpServers', {}).setdefault('${server}', {}).setdefault('env', {})['${key}'] = '${value}'
with open('${config_file}', 'w') as f:
    json.dump(data, f, indent=2)
print('  Updated ${key} in ${server}')
"
}

# Add/replace entire server config
set_server_config() {
  local server="$1" config_json="$2" config_file="$3"
  python3 -c "
import json
with open('${config_file}') as f:
    data = json.load(f)
data.setdefault('mcpServers', {})['${server}'] = json.loads('''${config_json}''')
with open('${config_file}', 'w') as f:
    json.dump(data, f, indent=2)
print('  Configured ${server} in ${config_file}')
"
}

# Ensure config file exists with proper structure
ensure_config() {
  local config_file="$1" ide="$2"
  if [[ ! -f "$config_file" ]]; then
    local dir
    dir=$(dirname "$config_file")
    mkdir -p "$dir"
    if [[ "$ide" == "claude" ]]; then
      # claude.json may have other keys — only create if missing
      echo '{"mcpServers":{}}' > "$config_file"
    else
      echo '{"mcpServers":{}}' > "$config_file"
    fi
    echo "Created $config_file"
  fi
}

status_icon() {
  if [[ "$1" == "ok" ]]; then echo "✓"; elif [[ "$1" == "warn" ]]; then echo "○"; else echo "✗"; fi
}

# ─── GitHub MCP ─────────────────────────────────────────────────────
setup_github() {
  local config_file="$1"
  echo ""
  echo "── GitHub MCP ──"

  local pat
  pat=$(read_zshenv_var "GITHUB_PAT")

  # Check if configured
  if server_configured "github" "$config_file"; then
    echo "  $(status_icon ok) Server configured"

    # Check token freshness
    local current_pat
    current_pat=$(get_server_env_val "github" "GITHUB_PERSONAL_ACCESS_TOKEN" "$config_file")
    if [[ -n "$pat" && "$current_pat" != "$pat" ]]; then
      if $CHECK_ONLY; then
        echo "  $(status_icon warn) Token in config differs from ~/.zshenv GITHUB_PAT"
      else
        update_server_env_val "github" "GITHUB_PERSONAL_ACCESS_TOKEN" "$pat" "$config_file"
      fi
    else
      echo "  $(status_icon ok) Token up to date"
    fi

    # Check for Docker image update
    if command -v docker &>/dev/null; then
      if $CHECK_ONLY; then
        echo "  $(status_icon warn) Run 'docker pull ghcr.io/github/github-mcp-server' to check for updates"
      else
        echo "  Checking for image updates..."
        docker pull ghcr.io/github/github-mcp-server 2>/dev/null && echo "  $(status_icon ok) Image up to date" || echo "  $(status_icon warn) Could not pull image (Docker may not be running)"
      fi
    fi
  else
    # Not configured — set it up
    if [[ -z "$pat" ]]; then
      echo "  $(status_icon warn) GITHUB_PAT not found in ~/.zshenv — skipping (add it and re-run)"
      return
    fi
    if $CHECK_ONLY; then
      echo "  $(status_icon warn) Not configured — run without --check-only to configure"
      return
    fi
    local config
    config=$(cat <<'ENDJSON'
{"command":"docker","args":["run","-i","--rm","-e","GITHUB_PERSONAL_ACCESS_TOKEN","ghcr.io/github/github-mcp-server"],"env":{"GITHUB_PERSONAL_ACCESS_TOKEN":"PLACEHOLDER"}}
ENDJSON
    )
    config=$(echo "$config" | sed "s/PLACEHOLDER/${pat}/")
    set_server_config "github" "$config" "$config_file"

    # Pull the Docker image
    if command -v docker &>/dev/null; then
      echo "  Pulling Docker image..."
      docker pull ghcr.io/github/github-mcp-server 2>/dev/null || echo "  $(status_icon warn) Could not pull image"
    else
      echo "  $(status_icon warn) Docker not found — install Docker to use GitHub MCP"
    fi
  fi
}

# ─── Bitbucket MCP ──────────────────────────────────────────────────
setup_bitbucket() {
  local config_file="$1"
  echo ""
  echo "── Bitbucket MCP ──"

  local username token
  username=$(read_zshenv_var "BITBUCKET_USERNAME")
  token=$(read_zshenv_var "BITBUCKET_TOKEN")

  if server_configured "bitbucket" "$config_file"; then
    echo "  $(status_icon ok) Server configured"

    # Check token freshness
    local current_token current_username
    current_token=$(get_server_env_val "bitbucket" "BITBUCKET_TOKEN" "$config_file")
    current_username=$(get_server_env_val "bitbucket" "BITBUCKET_USERNAME" "$config_file")

    local needs_update=false
    if [[ -n "$token" && "$current_token" != "$token" ]]; then
      needs_update=true
      echo "  $(status_icon warn) BITBUCKET_TOKEN changed"
    fi
    if [[ -n "$username" && "$current_username" != "$username" ]]; then
      needs_update=true
      echo "  $(status_icon warn) BITBUCKET_USERNAME changed"
    fi

    if $needs_update; then
      if $CHECK_ONLY; then
        echo "  Run without --check-only to update"
      else
        [[ -n "$token" ]] && update_server_env_val "bitbucket" "BITBUCKET_TOKEN" "$token" "$config_file"
        [[ -n "$username" ]] && update_server_env_val "bitbucket" "BITBUCKET_USERNAME" "$username" "$config_file"
      fi
    else
      echo "  $(status_icon ok) Tokens up to date"
    fi

    # npx always uses latest, so no explicit update needed
    echo "  $(status_icon ok) Package auto-updates via npx -y bitbucket-mcp@latest"
  else
    if [[ -z "$token" || -z "$username" ]]; then
      echo "  $(status_icon warn) BITBUCKET_USERNAME or BITBUCKET_TOKEN not in ~/.zshenv — skipping"
      return
    fi
    if $CHECK_ONLY; then
      echo "  $(status_icon warn) Not configured — run without --check-only to configure"
      return
    fi
    local config
    config=$(cat <<ENDJSON
{"command":"sh","args":["-c","BITBUCKET_USERNAME=\${BITBUCKET_USERNAME} BITBUCKET_PASSWORD=\${BITBUCKET_TOKEN} npx -y bitbucket-mcp@latest"],"env":{"BITBUCKET_USERNAME":"${username}","BITBUCKET_TOKEN":"${token}"}}
ENDJSON
    )
    set_server_config "bitbucket" "$config" "$config_file"
  fi
}

# ─── Atlassian Confluence MCP ───────────────────────────────────────
setup_confluence() {
  local config_file="$1"
  echo ""
  echo "── Atlassian Confluence MCP ──"

  local url email api_token
  url=$(read_zshenv_var "CONFLUENCE_URL")
  email=$(read_zshenv_var "CONFLUENCE_USERNAME")
  api_token=$(read_zshenv_var "CONFLUENCE_API_TOKEN")

  if server_configured "atlassian-confluence" "$config_file"; then
    echo "  $(status_icon ok) Server configured"

    # Check token freshness
    local current_url current_email current_token
    current_url=$(get_server_env_val "atlassian-confluence" "CONFLUENCE_URL" "$config_file")
    current_email=$(get_server_env_val "atlassian-confluence" "CONFLUENCE_USERNAME" "$config_file")
    current_token=$(get_server_env_val "atlassian-confluence" "CONFLUENCE_API_TOKEN" "$config_file")

    local needs_update=false
    [[ -n "$url" && "$current_url" != "$url" ]] && needs_update=true && echo "  $(status_icon warn) CONFLUENCE_URL changed"
    [[ -n "$email" && "$current_email" != "$email" ]] && needs_update=true && echo "  $(status_icon warn) CONFLUENCE_USERNAME changed"
    [[ -n "$api_token" && "$current_token" != "$api_token" ]] && needs_update=true && echo "  $(status_icon warn) CONFLUENCE_API_TOKEN changed"

    if $needs_update; then
      if $CHECK_ONLY; then
        echo "  Run without --check-only to update"
      else
        [[ -n "$url" ]] && update_server_env_val "atlassian-confluence" "CONFLUENCE_URL" "$url" "$config_file"
        [[ -n "$email" ]] && update_server_env_val "atlassian-confluence" "CONFLUENCE_USERNAME" "$email" "$config_file"
        [[ -n "$api_token" ]] && update_server_env_val "atlassian-confluence" "CONFLUENCE_API_TOKEN" "$api_token" "$config_file"
      fi
    else
      echo "  $(status_icon ok) Tokens up to date"
    fi

    # Check for package update
    if command -v uvx &>/dev/null; then
      if $CHECK_ONLY; then
        echo "  $(status_icon warn) Run 'uvx upgrade mcp-atlassian' to check for updates"
      else
        echo "  Checking for package updates..."
        pip install --upgrade mcp-atlassian 2>/dev/null && echo "  $(status_icon ok) Package up to date" || echo "  $(status_icon warn) Could not update mcp-atlassian"
      fi
    fi
  else
    if [[ -z "$url" || -z "$email" || -z "$api_token" ]]; then
      echo "  $(status_icon warn) CONFLUENCE_URL, CONFLUENCE_USERNAME, or CONFLUENCE_API_TOKEN not in ~/.zshenv — skipping"
      return
    fi
    if $CHECK_ONLY; then
      echo "  $(status_icon warn) Not configured — run without --check-only to configure"
      return
    fi

    # Check uvx availability
    if ! command -v uvx &>/dev/null; then
      echo "  $(status_icon warn) uvx not found — install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"
      return
    fi

    local config
    config=$(cat <<ENDJSON
{"command":"uvx","args":["mcp-atlassian","--confluence-url","${url}","--confluence-username","${email}","--confluence-token","${api_token}"],"env":{"CONFLUENCE_URL":"${url}","CONFLUENCE_USERNAME":"${email}","CONFLUENCE_API_TOKEN":"${api_token}"}}
ENDJSON
    )
    set_server_config "atlassian-confluence" "$config" "$config_file"
  fi
}

# ─── Google Drive MCP ───────────────────────────────────────────────
setup_google_drive() {
  local config_file="$1"
  echo ""
  echo "── Google Drive MCP ──"

  local creds_path
  creds_path=$(read_zshenv_var "GOOGLE_DRIVE_OAUTH_CREDENTIALS")
  creds_path="${creds_path:-${HOME}/.config/google-drive-mcp/gcp-oauth.keys.json}"

  if server_configured "google-drive" "$config_file"; then
    echo "  $(status_icon ok) Server configured"

    # Check credentials file exists
    if [[ -f "$creds_path" ]]; then
      echo "  $(status_icon ok) OAuth credentials file exists: $creds_path"
    else
      echo "  $(status_icon warn) OAuth credentials file missing: $creds_path"
      echo "  Create Google OAuth desktop credentials and save to that path"
    fi

    # npx auto-updates
    echo "  $(status_icon ok) Package auto-updates via npx -y"
  else
    if $CHECK_ONLY; then
      echo "  $(status_icon warn) Not configured — run without --check-only to configure"
      return
    fi

    if [[ ! -f "$creds_path" ]]; then
      echo "  $(status_icon warn) OAuth credentials not found at $creds_path"
      echo "  1. Create Google OAuth desktop credentials"
      echo "  2. Save to: $creds_path"
      echo "  3. Re-run this script"
      return
    fi

    local config='{"command":"npx","args":["-y","@piotr-agier/google-drive-mcp"],"env":{}}'
    set_server_config "google-drive" "$config" "$config_file"
    echo "  Note: Complete the browser OAuth flow on first run"
  fi
}

# ─── Main ───────────────────────────────────────────────────────────

echo "DevKit MCP Setup"
echo "================"
echo "Env:    $ZSHENV"
if $CHECK_ONLY; then
  echo "Mode:   check-only (no changes)"
else
  echo "Mode:   setup & update"
fi

# Resolve which IDE(s) to configure
IDE_LIST=$(resolve_ides)

# If auto-detection failed and needs user input, output a special marker
if [[ "$IDE_LIST" == ASK:* ]]; then
  available="${IDE_LIST#ASK:}"
  echo ""
  echo "PROMPT_USER:Could not auto-detect your IDE/tool. Available: ${available}"
  echo "PROMPT_USER:Pass --ide <tool> to specify (e.g. --ide claude, --ide cursor, --ide all)"
  exit 2
fi

echo "Target: $IDE_LIST"
echo ""

for ide in $IDE_LIST; do
  config_file=$(config_path_for_ide "$ide")
  if [[ -z "$config_file" ]]; then
    echo "$(status_icon warn) Unknown IDE: $ide — skipping"
    continue
  fi

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Configuring: $ide ($config_file)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if ! $CHECK_ONLY; then
    ensure_config "$config_file" "$ide"
  elif [[ ! -f "$config_file" ]]; then
    echo "  $(status_icon warn) Config file does not exist: $config_file"
    echo "  Run without --check-only to create it"
    echo ""
    continue
  fi

  if [[ -n "$TARGET_SERVER" ]]; then
    case "$TARGET_SERVER" in
      github) setup_github "$config_file" ;;
      bitbucket) setup_bitbucket "$config_file" ;;
      atlassian-confluence|confluence) setup_confluence "$config_file" ;;
      google-drive) setup_google_drive "$config_file" ;;
      *) echo "Unknown server: $TARGET_SERVER"; exit 1 ;;
    esac
  else
    setup_github "$config_file"
    setup_bitbucket "$config_file"
    setup_confluence "$config_file"
    setup_google_drive "$config_file"
  fi

  echo ""
done

echo "Done."
