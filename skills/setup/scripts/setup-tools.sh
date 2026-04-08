#!/usr/bin/env bash
# setup-tools.sh — Idempotent CLI tool setup, validation, and update script
# Usage: bash setup-tools.sh [--check-only] [--tool <name>] [--skip-update]
#
# For each tool:
#   1. Check if installed → install via brew if missing
#   2. Check for updates → update via brew if available (unless --skip-update)
#
# Supports: git, python3, node, npm, dot (graphviz), uvx (uv), docker, gh

set -euo pipefail

CHECK_ONLY=false
TARGET_TOOL=""
SKIP_UPDATE=false

# ─── Argument parsing ───────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-only) CHECK_ONLY=true; shift ;;
    --tool) TARGET_TOOL="$2"; shift 2 ;;
    --skip-update) SKIP_UPDATE=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# ─── Helpers ────────────────────────────────────────────────────────
ERRORS=0
INSTALLED=0
UPDATED=0

status_icon() {
  if [[ "$1" == "ok" ]]; then echo "✓"; elif [[ "$1" == "warn" ]]; then echo "○"; else echo "✗"; fi
}

ensure_brew() {
  if ! command -v brew &>/dev/null; then
    echo ""
    echo "Homebrew is not installed. It is required to install CLI tools."
    echo "Install it with:"
    echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    exit 1
  fi
}

# Generic: check, install, update a brew formula
setup_brew_tool() {
  local name="$1"        # display name
  local cmd="$2"         # command to check
  local formula="$3"     # brew formula name
  local version_flag="${4:---version}"  # flag to get version
  local is_cask="${5:-false}"           # brew --cask?

  echo ""
  echo "── ${name} ──"

  if command -v "$cmd" &>/dev/null; then
    local ver
    ver=$($cmd $version_flag 2>&1 | head -1)
    echo "  $(status_icon ok) Installed: $ver"

    # Check for updates
    if ! $SKIP_UPDATE; then
      if $CHECK_ONLY; then
        echo "  $(status_icon warn) Run without --check-only to check for updates"
      else
        echo "  Checking for updates..."
        if [[ "$is_cask" == "true" ]]; then
          if brew upgrade --cask "$formula" 2>/dev/null; then
            local new_ver
            new_ver=$($cmd $version_flag 2>&1 | head -1)
            if [[ "$ver" != "$new_ver" ]]; then
              echo "  $(status_icon ok) Updated: $new_ver"
              UPDATED=$((UPDATED + 1))
            else
              echo "  $(status_icon ok) Already latest"
            fi
          else
            echo "  $(status_icon ok) Already latest"
          fi
        else
          if brew upgrade "$formula" 2>/dev/null; then
            local new_ver
            new_ver=$($cmd $version_flag 2>&1 | head -1)
            if [[ "$ver" != "$new_ver" ]]; then
              echo "  $(status_icon ok) Updated: $new_ver"
              UPDATED=$((UPDATED + 1))
            else
              echo "  $(status_icon ok) Already latest"
            fi
          else
            echo "  $(status_icon ok) Already latest"
          fi
        fi
      fi
    fi
  else
    echo "  $(status_icon warn) Not installed"
    if $CHECK_ONLY; then
      echo "  Install with: brew install ${formula}"
      ERRORS=$((ERRORS + 1))
      return
    fi

    ensure_brew
    echo "  Installing ${formula}..."
    if [[ "$is_cask" == "true" ]]; then
      brew install --cask "$formula" && echo "  $(status_icon ok) Installed" && INSTALLED=$((INSTALLED + 1)) || { echo "  $(status_icon warn) Installation failed"; ERRORS=$((ERRORS + 1)); }
    else
      brew install "$formula" && echo "  $(status_icon ok) Installed" && INSTALLED=$((INSTALLED + 1)) || { echo "  $(status_icon warn) Installation failed"; ERRORS=$((ERRORS + 1)); }
    fi
  fi
}

# Special handler for uv/uvx (not a brew formula by default)
setup_uv() {
  echo ""
  echo "── uv / uvx ──"

  if command -v uvx &>/dev/null; then
    local ver
    ver=$(uvx --version 2>&1 | head -1)
    echo "  $(status_icon ok) Installed: $ver"

    if ! $SKIP_UPDATE && ! $CHECK_ONLY; then
      echo "  Updating uv..."
      curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null && echo "  $(status_icon ok) Updated" || echo "  $(status_icon ok) Already latest"
    fi
  else
    echo "  $(status_icon warn) Not installed"
    if $CHECK_ONLY; then
      echo "  Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
      ERRORS=$((ERRORS + 1))
      return
    fi
    echo "  Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null && echo "  $(status_icon ok) Installed" && INSTALLED=$((INSTALLED + 1)) || { echo "  $(status_icon warn) Installation failed"; ERRORS=$((ERRORS + 1)); }
  fi
}

# Special handler for npm update
setup_npm() {
  echo ""
  echo "── npm ──"

  if command -v npm &>/dev/null; then
    local ver
    ver=$(npm --version 2>&1 | head -1)
    echo "  $(status_icon ok) Installed: v${ver}"

    if ! $SKIP_UPDATE && ! $CHECK_ONLY; then
      echo "  Checking for updates..."
      npm install -g npm@latest 2>/dev/null && echo "  $(status_icon ok) Updated to $(npm --version)" || echo "  $(status_icon ok) Already latest"
    fi
  else
    echo "  $(status_icon warn) Not installed (install node first — npm is bundled)"
    ERRORS=$((ERRORS + 1))
  fi
}

# Generic: install/update a global npm package
setup_npm_package() {
  local name="$1"
  local cmd="$2"
  local pkg="$3"

  echo ""
  echo "── ${name} ──"

  if command -v "$cmd" &>/dev/null; then
    local ver
    ver=$($cmd --version 2>&1 | head -1)
    echo "  $(status_icon ok) Installed: $ver"

    if ! $SKIP_UPDATE && ! $CHECK_ONLY; then
      echo "  Checking for updates..."
      npm install -g "$pkg" 2>/dev/null && echo "  $(status_icon ok) Updated" || echo "  $(status_icon ok) Already latest"
    fi
  else
    echo "  $(status_icon warn) Not installed"
    if ! command -v npm &>/dev/null; then
      echo "  $(status_icon warn) npm not found — install node first"
      ERRORS=$((ERRORS + 1))
      return
    fi
    if $CHECK_ONLY; then
      echo "  Install with: npm install -g ${pkg}"
      ERRORS=$((ERRORS + 1))
      return
    fi
    echo "  Installing ${pkg}..."
    npm install -g "$pkg" && echo "  $(status_icon ok) Installed" && INSTALLED=$((INSTALLED + 1)) || { echo "  $(status_icon warn) Installation failed"; ERRORS=$((ERRORS + 1)); }
  fi
}

# ─── Tool setup functions ──────────────────────────────────────────
run_git()         { setup_brew_tool "git"        "git"     "git"      "--version"; }
run_python3()     { setup_brew_tool "Python 3"   "python3" "python"   "--version"; }
run_node()        { setup_brew_tool "Node.js"    "node"    "node"     "--version"; }
run_npm()         { setup_npm; }
run_graphviz()    { setup_brew_tool "Graphviz"   "dot"     "graphviz" "-V"; }
run_docker()      { setup_brew_tool "Docker"     "docker"  "docker"   "--version" "true"; }
run_gh()          { setup_brew_tool "GitHub CLI" "gh"      "gh"       "--version"; }
run_uv()          { setup_uv; }
run_jq()          { setup_brew_tool "jq"         "jq"      "jq"       "--version"; }
run_curl()        { setup_brew_tool "curl"       "curl"    "curl"     "--version"; }
run_diagramkit()  { setup_npm_package "diagramkit" "diagramkit" "diagramkit"; }
run_pagesmith()   { setup_npm_package "pagesmith"  "pagesmith"  "@pagesmith/docs"; }

setup_gh_auth() {
  echo ""
  echo "── GitHub CLI Auth ──"
  if ! command -v gh &>/dev/null; then
    echo "  $(status_icon warn) gh not installed — skipping auth check"
    return
  fi
  if gh auth status &>/dev/null; then
    echo "  $(status_icon ok) Authenticated"
  else
    echo "  $(status_icon warn) Not authenticated"
    echo "  Run: gh auth login"
    echo "  Then follow the prompts to sign in with your GitHub account."
    ERRORS=$((ERRORS + 1))
  fi
}

# ─── Main ───────────────────────────────────────────────────────────

echo "DevKit CLI Tool Setup"
echo "====================="
if $CHECK_ONLY; then
  echo "Mode: check-only (no changes)"
elif $SKIP_UPDATE; then
  echo "Mode: install only (skip updates)"
else
  echo "Mode: install & update"
fi

if [[ -n "$TARGET_TOOL" ]]; then
  case "$TARGET_TOOL" in
    git) run_git ;;
    python|python3) run_python3 ;;
    node) run_node ;;
    npm) run_npm ;;
    dot|graphviz) run_graphviz ;;
    docker) run_docker ;;
    gh) run_gh; setup_gh_auth ;;
    uv|uvx) run_uv ;;
    jq) run_jq ;;
    curl) run_curl ;;
    diagramkit) run_diagramkit ;;
    pagesmith) run_pagesmith ;;
    *) echo "Unknown tool: $TARGET_TOOL"; exit 1 ;;
  esac
else
  run_git
  run_python3
  run_node
  run_npm
  run_jq
  run_curl
  run_graphviz
  run_uv
  run_docker
  run_gh
  setup_gh_auth
  run_diagramkit
  run_pagesmith
fi

echo ""
echo "────────────────"
echo "Summary: ${INSTALLED} installed, ${UPDATED} updated, ${ERRORS} error(s)"
if [[ $ERRORS -gt 0 ]]; then
  echo "Some tools could not be installed. Check the output above."
  exit 1
fi
echo "Done."
