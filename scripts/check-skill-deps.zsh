#!/usr/bin/env zsh
set -euo pipefail

skill="${1:-}"
shift || true

if [[ -z "$skill" ]]; then
  cat <<'EOF'
Usage: zsh scripts/check-skill-deps.zsh <skill-name> [key=value ...]

Examples:
  zsh scripts/check-skill-deps.zsh review-pr pr=https://github.com/org/repo/pull/42 publish=both
  zsh scripts/check-skill-deps.zsh review-doc source=https://docs.google.com/document/d/123/edit
  zsh scripts/check-skill-deps.zsh diagrams format=png
EOF
  exit 1
fi

provider_arg=""
source_arg=""
target_arg=""
pr_arg=""
format_arg=""
output_arg=""
publish_arg=""
server_arg=""

for arg in "$@"; do
  if [[ "$arg" == *=* ]]; then
    key="${arg%%=*}"
    value="${arg#*=}"
    case "$key" in
      provider)
        provider_arg="$value"
        ;;
      source)
        source_arg="$value"
        ;;
      target)
        target_arg="$value"
        ;;
      pr)
        pr_arg="$value"
        ;;
      format)
        format_arg="$value"
        ;;
      output)
        output_arg="$value"
        ;;
      publish)
        publish_arg="$value"
        ;;
      server)
        server_arg="$value"
        ;;
    esac
  fi
done

errors=0
warnings=0

print_status() {
  local icon="$1"
  local message="$2"
  printf '  %s %s\n' "$icon" "$message"
}

ok() {
  print_status "✓" "$1"
}

info() {
  print_status "ℹ" "$1"
}

warn() {
  local message="$1"
  warnings=$((warnings + 1))
  print_status "○" "$message"
}

fail() {
  local message="$1"
  local install_hint="${2:-}"
  errors=$((errors + 1))
  print_status "✗" "$message"
  if [[ -n "$install_hint" ]]; then
    print_status " " "Install: $install_hint"
  fi
}

need_cmd() {
  local name="$1"
  local install_hint="${2:-}"
  if command -v "$name" >/dev/null 2>&1; then
    ok "$name"
  else
    fail "$name (missing)" "$install_hint"
  fi
}

need_optional_cmd() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    ok "$name"
  else
    warn "$name (optional, not installed)"
  fi
}

global_npm_root() {
  npm root -g 2>/dev/null || true
}

has_global_npm_package() {
  local pkg="$1"
  if ! command -v npm >/dev/null 2>&1; then
    return 1
  fi
  npm list -g --depth=0 "$pkg" >/dev/null 2>&1
}

need_global_npm_package() {
  local pkg="$1"
  local install_hint="$2"
  if has_global_npm_package "$pkg"; then
    ok "global npm package $pkg"
  else
    fail "global npm package $pkg (missing)" "$install_hint"
  fi
}

need_mcp() {
  local name="$1"
  local install_hint="$2"
  local cfg="$HOME/.claude.json"
  if [[ -f "$cfg" ]] && jq -e ".mcpServers[\"$name\"]" "$cfg" >/dev/null 2>&1; then
    ok "MCP $name configured"
  else
    fail "MCP $name not configured" "$install_hint"
  fi
}

maybe_need_mcp() {
  local name="$1"
  local install_hint="$2"
  local cfg="$HOME/.claude.json"
  if [[ -f "$cfg" ]] && jq -e ".mcpServers[\"$name\"]" "$cfg" >/dev/null 2>&1; then
    ok "MCP $name configured"
  else
    warn "MCP $name not configured"
    if [[ -n "$install_hint" ]]; then
      print_status " " "Setup: $install_hint"
    fi
  fi
}

diagramkit_package_dir() {
  local root
  root="$(global_npm_root)"
  if [[ -n "$root" ]]; then
    printf '%s/diagramkit\n' "$root"
  fi
}

need_diagramkit_playwright() {
  local pkg_dir
  pkg_dir="$(diagramkit_package_dir)"

  if [[ -z "$pkg_dir" || ! -d "$pkg_dir" ]]; then
    fail "Playwright Chromium could not be checked because global diagramkit is missing" "npm install -g diagramkit"
    return
  fi

  if node - "$pkg_dir" >/dev/null 2>&1 <<'NODE'
const path = require('node:path')

;(async () => {
  const pkgDir = process.argv[2]
  const { chromium } = require(path.join(pkgDir, 'node_modules/playwright'))
  const browser = await chromium.launch()
  await browser.close()
})().catch((error) => {
  console.error(error && error.message ? error.message : String(error))
  process.exit(1)
})
NODE
  then
    ok "Playwright Chromium ready for diagramkit"
  else
    fail "Playwright Chromium not ready for diagramkit" "diagramkit warmup"
    print_status " " "Alternative: npx playwright install chromium"
  fi
}

detect_provider() {
  local raw="$1"
  local lower="${raw:l}"

  if [[ -z "$lower" ]]; then
    return
  fi

  case "$lower" in
    *github.com/*|github)
      echo "github"
      ;;
    *bitbucket.org/*|bitbucket)
      echo "bitbucket"
      ;;
    *atlassian.net/wiki/*|*confluence*|confluence)
      echo "atlassian-confluence"
      ;;
    *docs.google.com/*|*drive.google.com/*|google-doc|google-drive|google)
      echo "google-drive"
      ;;
  esac

  return 0
}

detect_pr_provider_from_git() {
  if ! command -v git >/dev/null 2>&1; then
    return
  fi

  local remote
  remote="$(git remote get-url origin 2>/dev/null || true)"
  detect_provider "$remote"
}

check_selected_mcp() {
  local provider="$1"
  case "$provider" in
    github)
      need_mcp github "Configure the GitHub MCP in ~/.claude.json as documented in settings/mcp-setup.md"
      ;;
    bitbucket)
      need_mcp bitbucket "Configure the Bitbucket MCP in ~/.claude.json as documented in settings/mcp-setup.md"
      ;;
    atlassian-confluence)
      need_mcp atlassian-confluence "Configure the Confluence MCP in ~/.claude.json as documented in settings/mcp-setup.md"
      ;;
    google-drive)
      need_mcp google-drive "Configure the Google Drive MCP in ~/.claude.json as documented in settings/mcp-setup.md"
      ;;
    "")
      warn "No source-specific MCP could be inferred from the provided input"
      ;;
  esac
}

is_raster_format() {
  local value="${1:l}"
  [[ "$value" == "png" || "$value" == "jpeg" || "$value" == "jpg" || "$value" == "webp" ]]
}

resolve_provider() {
  local candidate=""

  for candidate_input in \
    "$provider_arg" \
    "$source_arg" \
    "$target_arg" \
    "$pr_arg" \
    "$publish_arg" \
    "$format_arg" \
    "$server_arg"; do
    if [[ -n "$candidate_input" ]]; then
      candidate="$(detect_provider "$candidate_input")"
      if [[ -n "$candidate" ]]; then
        echo "$candidate"
        return 0
      fi
    fi
  done

  if [[ "$skill" == "review-pr" || "$skill" == "review-code-pr" || "$skill" == "pr-review" || "$skill" == "review-pr-followup" || "$skill" == "pr-review-followup" || "$skill" == "pr-describe" ]]; then
    candidate="$(detect_pr_provider_from_git)"
    if [[ -n "$candidate" ]]; then
      echo "$candidate"
    fi
  fi

  return 0
}

echo "Checking AKIT dependencies for: $skill"
if (( $# > 0 )); then
  echo "Context:"
  for arg in "$@"; do
    echo "  - $arg"
  done
fi

provider="$(resolve_provider)"
format_value="${format_arg:-${output_arg:-}}"
publish_value="${publish_arg:-}"

case "$skill" in
  review-pr|review-code-pr|pr-review|review-pr-followup|pr-review-followup|pr-describe)
    need_cmd git
    need_cmd rg
    need_cmd fd
    need_cmd jq
    check_selected_mcp "$provider"
    ;;
  pr-fix|pr-fix-comments|pr-fix-comment)
    need_cmd git
    need_cmd rg
    need_cmd fd
    need_cmd jq
    check_selected_mcp "$provider"
    # Verify we are in a git repo
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      fail "Not inside a git repository" "Run this skill from within a cloned repository"
    else
      ok "Inside a git repository"
    fi
    # Verify clean working tree
    if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
      fail "Working tree is not clean" "Commit or stash your changes first"
    else
      ok "Working tree is clean"
    fi
    ;;
  pr-finalize|pr-finish)
    need_cmd git
    need_cmd rg
    need_cmd fd
    need_cmd jq
    check_selected_mcp "$provider"
    # Verify we are in a git repo
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      fail "Not inside a git repository" "Run this skill from within a cloned repository"
    else
      ok "Inside a git repository"
    fi
    # Verify not on main/master
    local current_branch
    current_branch="$(git branch --show-current 2>/dev/null || true)"
    if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
      fail "Currently on $current_branch — switch to a feature branch first"
    else
      ok "On branch: $current_branch"
    fi
    # Verify clean working tree
    if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
      fail "Working tree is not clean" "Commit or stash your changes first"
    else
      ok "Working tree is clean"
    fi
    ;;
  review)
    need_cmd rg
    need_cmd fd
    need_cmd jq
    check_selected_mcp "$provider"
    ;;
  review-doc|doc-review)
    need_cmd rg
    need_cmd fd
    need_cmd jq
    check_selected_mcp "$provider"
    ;;
  write-doc|doc-write|write-project-docs|project-docs|publish-confluence|confluence-publish|write-markdown|markdown|write-article|article|write-blog|blog)
    need_cmd rg
    need_cmd fd
    need_cmd jq
    if [[ -n "$provider" ]]; then
      check_selected_mcp "$provider"
    else
      case "${format_value:l}" in
        confluence)
          need_mcp atlassian-confluence "Configure the Confluence MCP in ~/.claude.json as documented in settings/mcp-setup.md"
          ;;
        google-doc)
          need_mcp google-drive "Configure the Google Drive MCP in ~/.claude.json as documented in settings/mcp-setup.md"
        ;;
      esac
    fi
    ;;
  review-local|review-code-local|self-review|review-codebase|codebase-review|research|research-quick|search|research-deep|deep-research|audit-security|security-audit|audit-performance|performance-audit)
    need_cmd git
    need_cmd rg
    need_cmd fd
    need_cmd jq
    ;;
  write-adr|adr|write-onboarding|onboarding|write-runbook|runbook|write-api-docs|api-docs|write-tech-radar|tech-radar)
    need_cmd git
    need_cmd rg
    need_cmd fd
    need_cmd jq
    ;;
  audit-dependency|dependency-audit)
    need_cmd git
    need_cmd rg
    need_cmd fd
    need_cmd jq
    need_cmd node
    need_cmd npm
    ;;
  write-migration-guide|migration-guide)
    need_cmd git
    need_cmd rg
    need_cmd fd
    need_cmd jq
    ;;
  write-changelog|changelog)
    need_cmd git
    need_cmd rg
    need_cmd jq
    ;;
  manage-update|update)
    need_cmd git
    need_cmd jq
    need_cmd rsync
    ;;
  manage-improve|improve)
    need_cmd git
    need_cmd rg
    need_cmd fd
    need_cmd jq
    need_cmd rsync
    ;;
  agent-team|team-dispatch)
    need_cmd rg
    need_cmd jq
    info "Optional provider CLIs:"
    need_optional_cmd claude
    need_optional_cmd codex
    need_optional_cmd gemini
    ;;
  agent-multi|multi)
    need_cmd rg
    need_cmd jq
    info "Optional provider CLIs:"
    need_optional_cmd claude
    need_optional_cmd codex
    need_optional_cmd gemini
    need_optional_cmd cursor-agent
    need_optional_cmd cursor-cli
    ;;
  diagram-graphviz)
    need_cmd node
    need_cmd rg
    need_cmd dot
    ;;
  diagrams|diagram|diagram-mermaid|diagram-excalidraw|diagram-drawio|diagramkit|diagram-render|image-convert|diagram-raster|diagram-convert|image-transform|diagram-pipeline|diagram-troubleshoot)
    need_cmd node
    need_cmd npm
    need_cmd npx
    need_cmd rg
    need_global_npm_package diagramkit "npm install -g diagramkit"
    need_diagramkit_playwright
    if is_raster_format "$format_value"; then
      need_global_npm_package sharp "npm install -g sharp"
    fi
    ;;
  manage-validate|validate-mcp)
    need_cmd jq
    local_server="${server_arg:-}"
    if [[ -n "$local_server" && "$local_server" != "all" ]]; then
      check_selected_mcp "$(detect_provider "$local_server")"
    else
      maybe_need_mcp github "See settings/mcp-setup.md"
      maybe_need_mcp bitbucket "See settings/mcp-setup.md"
      maybe_need_mcp atlassian-confluence "See settings/mcp-setup.md"
      maybe_need_mcp google-drive "See settings/mcp-setup.md"
    fi
    ;;
  *)
    need_cmd rg
    need_cmd fd
    need_cmd jq
    ;;
esac

if [[ "$publish_value:l" == "source" || "$publish_value:l" == "both" ]]; then
  if [[ -z "$provider" && -n "$source_arg" ]]; then
    warn "Publish requested but no source-native MCP could be inferred from the source"
  fi
fi

echo ""
if (( errors > 0 )); then
  echo "Dependency check failed with $errors error(s)."
  echo "Fix the missing items above before running the skill."
  exit 1
fi

if (( warnings > 0 )); then
  echo "Dependency check passed with $warnings warning(s)."
else
  echo "Dependency check passed."
fi
