#!/usr/bin/env bash
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

    if [ -n "${!name:-}" ]; then
        # Show first 4 and last 4 chars, mask the rest
        local val="${!name}"
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

echo -e "${BOLD}Bitbucket MCP${NC} (required for PR reviews on Bitbucket):"
check_env "BITBUCKET_TOKEN" "required" "Bitbucket App Password"

echo ""
echo -e "${BOLD}Atlassian Confluence MCP${NC} (required for Confluence operations):"
check_env "CONFLUENCE_API_TOKEN" "required" "Atlassian API token"
check_env "CONFLUENCE_BASE_URL" "required" "e.g. https://yoursite.atlassian.net/wiki"
check_env "CONFLUENCE_EMAIL" "required" "Atlassian account email"

echo ""
echo -e "${BOLD}AI API Keys${NC} (optional, for multi-model features):"
check_env "ANTHROPIC_API_KEY" "optional" "Anthropic API key"
check_env "OPENAI_API_KEY" "optional" "OpenAI API key"

echo ""
echo -e "${BOLD}OAuth-based MCP Servers${NC} (no env vars needed — browser login):"
echo -e "  ${CYAN}ℹ${NC}  Google Drive MCP      — uses OAuth browser flow (first-time setup via npx)"
echo -e "  ${CYAN}ℹ${NC}  Slack MCP             — Claude.ai built-in integration (login via Claude Desktop)"
echo -e "  ${CYAN}ℹ${NC}  Gmail MCP             — Claude.ai built-in integration (login via Claude Desktop)"
echo -e "  ${CYAN}ℹ${NC}  Google Calendar MCP   — Claude.ai built-in integration (login via Claude Desktop)"

echo ""
if [ $errors -gt 0 ]; then
    echo -e "${RED}${BOLD}✗ $errors required variable(s) not set.${NC}"
    echo -e ""
    echo -e "  Add these to ${BOLD}~/.zshenv${NC}:"
    echo -e "    export BITBUCKET_TOKEN=\"your-app-password\""
    echo -e "    export CONFLUENCE_API_TOKEN=\"your-api-token\""
    echo -e "    export CONFLUENCE_BASE_URL=\"https://yoursite.atlassian.net/wiki\""
    echo -e "    export CONFLUENCE_EMAIL=\"your-email@example.com\""
    echo -e ""
    echo -e "  Then reload: ${BOLD}source ~/.zshenv${NC}"
    echo -e ""
    echo -e "  See dot-files template: ${BOLD}~/personal/dot-files/configs/shell/.zshenv.example${NC}"
    exit 1
elif [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}${BOLD}○ $warnings optional variable(s) not set.${NC} Some features may be limited."
    echo -e "${GREEN}${BOLD}✓ All required variables present.${NC}"
else
    echo -e "${GREEN}${BOLD}✓ All environment variables configured.${NC}"
fi
