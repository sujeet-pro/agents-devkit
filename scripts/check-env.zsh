#!/usr/bin/env zsh
set -euo pipefail

BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

errors=0
warnings=0

check_env() {
    local name="$1"
    local required="$2"  # "required" or "optional"
    local description="$3"

    if [ -n "${(P)name:-}" ]; then
        # Show first 4 and last 4 chars, mask the rest
        local val="${(P)name}"
        local len=${#val}
        if [ $len -gt 12 ]; then
            local masked="${val:0:4}...${val: -4}"
        elif [ $len -gt 4 ]; then
            local masked="${val:0:2}..."
        else
            local masked="***"
        fi
        printf "  ${GREEN}✓${NC} %-30s %s (${CYAN}%s${NC})\n" "$name" "$description" "$masked"
    elif [ "$required" = "required" ]; then
        printf "  ${RED}✗${NC} %-30s %s ${RED}— NOT SET${NC}\n" "$name" "$description"
        ((errors++))
    else
        printf "  ${YELLOW}○${NC} %-30s %s ${YELLOW}— not set (optional)${NC}\n" "$name" "$description"
        ((warnings++))
    fi
}

echo -e "\n${BOLD}Checking environment variables for claude-devkit...${NC}\n"

echo -e "${BOLD}Bitbucket MCP${NC} (for Bitbucket PR reviews):"
check_env "BITBUCKET_TOKEN" "optional" "Bitbucket API Token"

echo ""
echo -e "${BOLD}Atlassian Confluence MCP${NC} (for Confluence operations):"
check_env "CONFLUENCE_URL" "optional" "e.g. https://yoursite.atlassian.net/wiki"
check_env "CONFLUENCE_USERNAME" "optional" "Atlassian account email"
check_env "CONFLUENCE_API_TOKEN" "optional" "Atlassian API token"

echo ""
echo -e "${BOLD}Google Drive MCP${NC} (for Google Docs/Sheets/Slides/Drive):"
check_env "GOOGLE_MCP_CLIENT_ID" "optional" "Google OAuth Client ID"
check_env "GOOGLE_MCP_CLIENT_SECRET" "optional" "Google OAuth Client Secret"
check_env "GOOGLE_DRIVE_OAUTH_CREDENTIALS" "optional" "Path to gcp-oauth.keys.json (auto-generated)"

# Check if credentials file exists when path is set
if [ -n "${GOOGLE_DRIVE_OAUTH_CREDENTIALS:-}" ] && [ ! -f "${GOOGLE_DRIVE_OAUTH_CREDENTIALS}" ]; then
    printf "  ${YELLOW}!${NC} %-30s %s\n" "" "File not found — run: scripts/setup-google-drive.zsh"
fi

# Suggest setup if client ID is set but credentials file is missing
if [ -n "${GOOGLE_MCP_CLIENT_ID:-}" ] && [ -z "${GOOGLE_DRIVE_OAUTH_CREDENTIALS:-}" ]; then
    printf "  ${YELLOW}!${NC} %-30s %s\n" "" "Run: scripts/setup-google-drive.zsh to generate credentials"
fi

echo ""
echo -e "${BOLD}OAuth-based MCP Servers${NC} (no env vars needed — browser login):"
echo -e "  ${CYAN}ℹ${NC}  Google Drive MCP      — run scripts/setup-google-drive.zsh for first-time OAuth setup"
echo -e "  ${CYAN}ℹ${NC}  Slack MCP             — Claude.ai built-in integration (login via Claude Desktop)"
echo -e "  ${CYAN}ℹ${NC}  Gmail MCP             — Claude.ai built-in integration (login via Claude Desktop)"
echo -e "  ${CYAN}ℹ${NC}  Google Calendar MCP   — Claude.ai built-in integration (login via Claude Desktop)"

echo ""
if [ $errors -gt 0 ]; then
    echo -e "${RED}${BOLD}✗ $errors variable(s) not set.${NC}"
    echo -e ""
    echo -e "  Add missing variables to ${BOLD}~/.zshenv${NC}:"
    echo -e "    export VAR_NAME=\"your-value\""
    echo -e ""
    echo -e "  Then reload: ${BOLD}source ~/.zshenv${NC}"
    echo -e ""
    echo -e "  See dot-files template: ${BOLD}~/personal/dot-files/configs/shell/.zshenv.example${NC}"
elif [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}${BOLD}○ $warnings optional variable(s) not set.${NC} Some MCP integrations will be unavailable."
else
    echo -e "${GREEN}${BOLD}✓ All environment variables configured.${NC}"
fi
