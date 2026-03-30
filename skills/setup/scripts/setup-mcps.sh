#!/usr/bin/env bash
# setup-mcps.sh — Idempotent MCP server setup, validation, and update script
# Usage: bash setup-mcps.sh [--check-only] [--server <name>]
#
# For each MCP server:
#   1. Check if configured in ~/.claude.json → configure if missing
#   2. Check for package updates → update if available
#   3. Check env var tokens in ~/.zshenv → update config if tokens changed
#
# Supports: github, bitbucket, atlassian-confluence, google-drive

set -euo pipefail

CLAUDE_CONFIG="${HOME}/.claude.json"
ZSHENV="${HOME}/.zshenv"
CHECK_ONLY=false
TARGET_SERVER=""

# ─── Argument parsing ───────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-only) CHECK_ONLY=true; shift ;;
    --server) TARGET_SERVER="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# ─── Helpers ────────────────────────────────────────────────────────

# Read an env var value from ~/.zshenv
read_zshenv_var() {
  local var_name="$1"
  if [[ -f "$ZSHENV" ]]; then
    grep -E "^export ${var_name}=" "$ZSHENV" 2>/dev/null | tail -1 | sed "s/^export ${var_name}=//" | sed 's/^"//' | sed 's/"$//' | sed "s/^'//" | sed "s/'$//"
  fi
}

# Check if an MCP server exists in ~/.claude.json
server_configured() {
  local name="$1"
  python3 -c "
import json, sys
try:
    with open('${CLAUDE_CONFIG}') as f:
        data = json.load(f)
    servers = data.get('mcpServers', {})
    sys.exit(0 if '${name}' in servers else 1)
except:
    sys.exit(1)
" 2>/dev/null
}

# Get a value from the MCP server's env block
get_server_env_val() {
  local server="$1" key="$2"
  python3 -c "
import json
with open('${CLAUDE_CONFIG}') as f:
    data = json.load(f)
val = data.get('mcpServers', {}).get('${server}', {}).get('env', {}).get('${key}', '')
print(val)
" 2>/dev/null
}

# Update a single env value in the MCP server config
update_server_env_val() {
  local server="$1" key="$2" value="$3"
  python3 -c "
import json
with open('${CLAUDE_CONFIG}') as f:
    data = json.load(f)
data.setdefault('mcpServers', {}).setdefault('${server}', {}).setdefault('env', {})['${key}'] = '${value}'
with open('${CLAUDE_CONFIG}', 'w') as f:
    json.dump(data, f, indent=2)
print('  Updated ${key} in ${server}')
"
}

# Add/replace entire server config
set_server_config() {
  local server="$1" config_json="$2"
  python3 -c "
import json
with open('${CLAUDE_CONFIG}') as f:
    data = json.load(f)
data.setdefault('mcpServers', {})['${server}'] = json.loads('''${config_json}''')
with open('${CLAUDE_CONFIG}', 'w') as f:
    json.dump(data, f, indent=2)
print('  Configured ${server} in ${CLAUDE_CONFIG}')
"
}

# Ensure ~/.claude.json exists with at least {}
ensure_claude_config() {
  if [[ ! -f "$CLAUDE_CONFIG" ]]; then
    echo '{}' > "$CLAUDE_CONFIG"
    echo "Created $CLAUDE_CONFIG"
  fi
}

status_icon() {
  if [[ "$1" == "ok" ]]; then echo "✓"; elif [[ "$1" == "warn" ]]; then echo "○"; else echo "✗"; fi
}

# ─── GitHub MCP ─────────────────────────────────────────────────────
setup_github() {
  echo ""
  echo "── GitHub MCP ──"

  local pat
  pat=$(read_zshenv_var "GITHUB_PAT")

  # Check if configured
  if server_configured "github"; then
    echo "  $(status_icon ok) Server configured"

    # Check token freshness
    local current_pat
    current_pat=$(get_server_env_val "github" "GITHUB_PERSONAL_ACCESS_TOKEN")
    if [[ -n "$pat" && "$current_pat" != "$pat" ]]; then
      if $CHECK_ONLY; then
        echo "  $(status_icon warn) Token in config differs from ~/.zshenv GITHUB_PAT"
      else
        update_server_env_val "github" "GITHUB_PERSONAL_ACCESS_TOKEN" "$pat"
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
    set_server_config "github" "$config"

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
  echo ""
  echo "── Bitbucket MCP ──"

  local username token
  username=$(read_zshenv_var "BITBUCKET_USERNAME")
  token=$(read_zshenv_var "BITBUCKET_TOKEN")

  if server_configured "bitbucket"; then
    echo "  $(status_icon ok) Server configured"

    # Check token freshness
    local current_token current_username
    current_token=$(get_server_env_val "bitbucket" "BITBUCKET_TOKEN")
    current_username=$(get_server_env_val "bitbucket" "BITBUCKET_USERNAME")

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
        [[ -n "$token" ]] && update_server_env_val "bitbucket" "BITBUCKET_TOKEN" "$token"
        [[ -n "$username" ]] && update_server_env_val "bitbucket" "BITBUCKET_USERNAME" "$username"
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
    set_server_config "bitbucket" "$config"
  fi
}

# ─── Atlassian Confluence MCP ───────────────────────────────────────
setup_confluence() {
  echo ""
  echo "── Atlassian Confluence MCP ──"

  local url email api_token
  url=$(read_zshenv_var "CONFLUENCE_URL")
  email=$(read_zshenv_var "CONFLUENCE_USERNAME")
  api_token=$(read_zshenv_var "CONFLUENCE_API_TOKEN")

  if server_configured "atlassian-confluence"; then
    echo "  $(status_icon ok) Server configured"

    # Check token freshness
    local current_url current_email current_token
    current_url=$(get_server_env_val "atlassian-confluence" "CONFLUENCE_URL")
    current_email=$(get_server_env_val "atlassian-confluence" "CONFLUENCE_USERNAME")
    current_token=$(get_server_env_val "atlassian-confluence" "CONFLUENCE_API_TOKEN")

    local needs_update=false
    [[ -n "$url" && "$current_url" != "$url" ]] && needs_update=true && echo "  $(status_icon warn) CONFLUENCE_URL changed"
    [[ -n "$email" && "$current_email" != "$email" ]] && needs_update=true && echo "  $(status_icon warn) CONFLUENCE_USERNAME changed"
    [[ -n "$api_token" && "$current_token" != "$api_token" ]] && needs_update=true && echo "  $(status_icon warn) CONFLUENCE_API_TOKEN changed"

    if $needs_update; then
      if $CHECK_ONLY; then
        echo "  Run without --check-only to update"
      else
        [[ -n "$url" ]] && update_server_env_val "atlassian-confluence" "CONFLUENCE_URL" "$url"
        [[ -n "$email" ]] && update_server_env_val "atlassian-confluence" "CONFLUENCE_USERNAME" "$email"
        [[ -n "$api_token" ]] && update_server_env_val "atlassian-confluence" "CONFLUENCE_API_TOKEN" "$api_token"
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
    set_server_config "atlassian-confluence" "$config"
  fi
}

# ─── Google Drive MCP ───────────────────────────────────────────────
setup_google_drive() {
  echo ""
  echo "── Google Drive MCP ──"

  local creds_path
  creds_path=$(read_zshenv_var "GOOGLE_DRIVE_OAUTH_CREDENTIALS")
  creds_path="${creds_path:-${HOME}/.config/google-drive-mcp/gcp-oauth.keys.json}"

  if server_configured "google-drive"; then
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
    set_server_config "google-drive" "$config"
    echo "  Note: Complete the browser OAuth flow on first run"
  fi
}

# ─── Main ───────────────────────────────────────────────────────────

echo "DevKit MCP Setup"
echo "================"
echo "Config: $CLAUDE_CONFIG"
echo "Env:    $ZSHENV"
if $CHECK_ONLY; then
  echo "Mode:   check-only (no changes)"
else
  echo "Mode:   setup & update"
fi

ensure_claude_config

if [[ -n "$TARGET_SERVER" ]]; then
  case "$TARGET_SERVER" in
    github) setup_github ;;
    bitbucket) setup_bitbucket ;;
    atlassian-confluence|confluence) setup_confluence ;;
    google-drive) setup_google_drive ;;
    *) echo "Unknown server: $TARGET_SERVER"; exit 1 ;;
  esac
else
  setup_github
  setup_bitbucket
  setup_confluence
  setup_google_drive
fi

echo ""
echo "Done."
