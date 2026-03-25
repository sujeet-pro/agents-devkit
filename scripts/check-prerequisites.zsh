#!/usr/bin/env zsh
set -euo pipefail

# Required CLI tools for AKIT contributor workflows

BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

errors=0
warnings=0

check_tool() {
    local name="$1"
    local cmd="$2"
    local required="$3"  # "required" or "optional"
    local install_hint="$4"

    if command -v "$cmd" &>/dev/null; then
        local version
        case "$cmd" in
            cursor-agent|cursor-cli)
                version="installed"
                ;;
            *)
                version=$("$cmd" --version 2>/dev/null | head -1 || echo "installed")
                ;;
        esac
        printf "  ${GREEN}✓${NC} %-20s %s\n" "$name" "$version"
    elif [ "$required" = "required" ]; then
        printf "  ${RED}✗${NC} %-20s ${RED}MISSING${NC} — %s\n" "$name" "$install_hint"
        errors=$((errors + 1))
    else
        printf "  ${YELLOW}○${NC} %-20s ${YELLOW}OPTIONAL${NC} — %s\n" "$name" "$install_hint"
        warnings=$((warnings + 1))
    fi
}

echo -e "\n${BOLD}Checking prerequisites for AKIT...${NC}\n"

echo -e "${BOLD}Core CLI Tools${NC} (install via dot-files / Homebrew):"
check_tool "fd (file finder)" "fd" "required" "brew install fd"
check_tool "ripgrep (rg)" "rg" "required" "brew install ripgrep"
check_tool "bat" "bat" "required" "brew install bat"
check_tool "git" "git" "required" "brew install git"
check_tool "eza" "eza" "optional" "brew install eza"
check_tool "jq" "jq" "required" "brew install jq"
check_tool "fzf" "fzf" "optional" "brew install fzf"
check_tool "gh (GitHub CLI)" "gh" "optional" "brew install gh"
check_tool "tree" "tree" "optional" "brew install tree"
check_tool "shellcheck" "shellcheck" "optional" "brew install shellcheck"
check_tool "docker" "docker" "optional" "brew install --cask docker"

echo ""
echo -e "${BOLD}Runtime Managers${NC} (install via dot-files / mise):"
check_tool "node" "node" "required" "mise install node"
check_tool "python" "python3" "required" "mise install python"
check_tool "npx" "npx" "required" "comes with node"
check_tool "uvx" "uvx" "required" "mise install uv"

echo ""
echo -e "${BOLD}Diagram Tools${NC}:"
check_tool "mermaid-cli (mmdc)" "mmdc" "optional" "npm install -g @mermaid-js/mermaid-cli"
check_tool "excalidraw-cli" "excalidraw" "optional" "npm install -g excalidraw-cli"
check_tool "diagramkit" "diagramkit" "optional" "npm install -g diagramkit"

echo ""
echo -e "${BOLD}Provider CLIs${NC} (optional for multi-mode):"
check_tool "claude (Claude Code)" "claude" "optional" "brew install claude-code"
check_tool "codex" "codex" "optional" "Install Codex CLI"
check_tool "gemini" "gemini" "optional" "Install Gemini CLI"
check_tool "cursor-agent" "cursor-agent" "optional" "Install Cursor agent CLI"
check_tool "cursor-cli" "cursor-cli" "optional" "Install Cursor CLI"

echo ""
if [ $errors -gt 0 ]; then
    echo -e "${RED}${BOLD}✗ $errors required tool(s) missing.${NC} Install them before proceeding."
    echo -e "  Install the missing tools, then re-run this check."
    exit 1
elif [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}${BOLD}○ $warnings optional tool(s) missing.${NC} Some features may be limited."
    echo -e "${GREEN}${BOLD}✓ All required tools present.${NC}"
else
    echo -e "${GREEN}${BOLD}✓ All tools present.${NC}"
fi
