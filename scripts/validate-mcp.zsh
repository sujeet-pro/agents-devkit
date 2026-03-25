#!/usr/bin/env zsh
set -euo pipefail

BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

CLAUDE_JSON="$HOME/.claude.json"
errors=0
warnings=0

echo -e "\n${BOLD}Validating MCP server configurations...${NC}\n"

if [ ! -f "$CLAUDE_JSON" ]; then
    echo -e "${RED}✗ ~/.claude.json not found.${NC} Run Claude Code at least once to generate it."
    exit 1
fi

check_mcp() {
    local name="$1"
    local required="$2"
    local auth_type="$3"

    if jq -e ".mcpServers[\"$name\"]" "$CLAUDE_JSON" &>/dev/null; then
        printf "  ${GREEN}✓${NC} %-25s configured (${CYAN}%s${NC})\n" "$name" "$auth_type"
    elif [ "$required" = "required" ]; then
        printf "  ${RED}✗${NC} %-25s ${RED}NOT CONFIGURED${NC}\n" "$name"
        errors=$((errors + 1))
    else
        printf "  ${YELLOW}○${NC} %-25s ${YELLOW}not configured (optional)${NC}\n" "$name"
        warnings=$((warnings + 1))
    fi
}

echo -e "${BOLD}AKIT MCP Servers${NC} (in ~/.claude.json):"
check_mcp "github" "optional" "GitHub PR read/write"
check_mcp "bitbucket" "optional" "Bitbucket PR read/write"
check_mcp "atlassian-confluence" "optional" "Confluence read/write"
check_mcp "google-drive" "optional" "Google Docs/Drive read/write"

echo ""
echo -e "${BOLD}MCP Configuration Reference${NC}:"
echo -e "  ${CYAN}ℹ${NC}  GitHub:     github/github-mcp-server"
echo -e "  ${CYAN}ℹ${NC}  Confluence: uvx mcp-atlassian (PyPI: mcp-atlassian)"
echo -e "  ${CYAN}ℹ${NC}  Bitbucket:  npx bitbucket-mcp@latest (npm: bitbucket-mcp)"
echo -e "  ${CYAN}ℹ${NC}  Google:     npx @piotr-agier/google-drive-mcp (OAuth tokens at ~/.config/google-drive-mcp/)"

echo ""
if [ $errors -gt 0 ]; then
    echo -e "${RED}${BOLD}✗ $errors required MCP server(s) not configured.${NC}"
    echo -e "  See: ${BOLD}settings/mcp-setup.md${NC} for setup instructions."
    exit 1
elif [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}${BOLD}○ $warnings optional MCP server(s) not configured.${NC}"
    echo -e "${GREEN}${BOLD}✓ Configure the ones needed for your workflows.${NC}"
else
    echo -e "${GREEN}${BOLD}✓ All MCP servers configured.${NC}"
fi
