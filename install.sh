#!/usr/bin/env bash
set -euo pipefail

# claude-devkit installer
# Installs skills, agents, guidelines, and settings into ~/.claude/

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVKIT_DIR="${CLAUDE_DEVKIT_DIR:-$SCRIPT_DIR}"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
MANIFEST_FILE="$CLAUDE_DIR/.devkit-manifest"

MODE="remote"
REPO_CONFIG=""
SKIP_CHECKS=false

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --mode=*)
      MODE="${arg#--mode=}"
      ;;
    --repo-config=*)
      REPO_CONFIG="${arg#--repo-config=}"
      ;;
    --skip-checks)
      SKIP_CHECKS=true
      ;;
    --list)
      echo "claude-devkit — available skills, agents, and guidelines"
      echo ""
      echo "Skills:"
      if [[ -d "$DEVKIT_DIR/skills" ]]; then
        for skill_dir in "$DEVKIT_DIR/skills"/*/; do
          [[ -d "$skill_dir" ]] || continue
          skill_name="$(basename "$skill_dir")"
          # Extract description from SKILL.md frontmatter
          if [[ -f "$skill_dir/SKILL.md" ]]; then
            desc=$(sed -n '/^description:/s/^description: *//p' "$skill_dir/SKILL.md" | head -1 | sed 's/"//g')
            printf "  %-20s %s\n" "/$skill_name" "$desc"
          else
            printf "  %-20s %s\n" "/$skill_name" "(no description)"
          fi
        done
      fi
      echo ""
      echo "Agents:"
      if [[ -d "$DEVKIT_DIR/agents" ]]; then
        for agent_file in "$DEVKIT_DIR/agents"/*.md; do
          [[ -f "$agent_file" ]] || continue
          agent_name="$(basename "$agent_file" .md)"
          desc=$(sed -n '/^description:/s/^description: *//p' "$agent_file" | head -1 | sed 's/"//g')
          model=$(sed -n '/^model:/s/^model: *//p' "$agent_file" | head -1)
          printf "  %-25s [%s] %s\n" "$agent_name" "${model:-sonnet}" "$desc"
        done
      fi
      echo ""
      echo "Guidelines:"
      if [[ -d "$DEVKIT_DIR/guidelines" ]]; then
        for guideline_dir in "$DEVKIT_DIR/guidelines"/*/; do
          [[ -d "$guideline_dir" ]] || continue
          dir_name="$(basename "$guideline_dir")"
          count=$(find "$guideline_dir" -name "*.md" -maxdepth 1 | wc -l | tr -d ' ')
          echo "  $dir_name/ ($count guidelines)"
        done
      fi
      exit 0
      ;;
    --help|-h)
      echo "Usage: install.sh [--mode=remote|dev] [--repo-config=TYPE] [--skip-checks] [--list]"
      echo ""
      echo "Options:"
      echo "  --mode=remote   Copy files into ~/.claude/ (default)"
      echo "  --mode=dev      Create symlinks from ~/.claude/ to the devkit repo"
      echo "  --repo-config=TYPE"
      echo "                  Install a per-repo CLAUDE.md into the current directory"
      echo "                  Types: design-system, frontend-nextjs, library, backend, default"
      echo "  --skip-checks   Skip prerequisite, env var, and MCP validation checks"
      echo "  --list          List all available skills, agents, and guidelines"
      echo ""
      echo "Quick start:"
      echo "  ./install.sh --mode=dev          # Dev mode (symlinks, edit in place)"
      echo "  ./install.sh                     # Remote mode (copies files)"
      echo "  ./install.sh --list              # See what's included"
      echo ""
      echo "Environment variables:"
      echo "  CLAUDE_DEVKIT_DIR  Override auto-detected devkit directory"
      echo "  CLAUDE_DIR         Override default ~/.claude/ directory"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Run install.sh --help for usage."
      exit 1
      ;;
  esac
done

if [[ "$MODE" != "remote" && "$MODE" != "dev" ]]; then
  echo "Error: --mode must be 'remote' or 'dev'"
  exit 1
fi

# ---------------------------------------------------------------------------
# Pre-flight checks (prerequisite tools, env vars, MCP config)
# ---------------------------------------------------------------------------
if [[ "$SKIP_CHECKS" == "false" ]]; then
  check_failed=false

  if [[ -x "$SCRIPT_DIR/scripts/check-prerequisites.sh" ]]; then
    if ! "$SCRIPT_DIR/scripts/check-prerequisites.sh"; then
      check_failed=true
    fi
  else
    echo "Warning: scripts/check-prerequisites.sh not found — skipping prerequisite check"
  fi

  if [[ -x "$SCRIPT_DIR/scripts/check-env.sh" ]]; then
    if ! "$SCRIPT_DIR/scripts/check-env.sh"; then
      check_failed=true
    fi
  else
    echo "Warning: scripts/check-env.sh not found — skipping env var check"
  fi

  if [[ -x "$SCRIPT_DIR/scripts/validate-mcp.sh" ]]; then
    if ! "$SCRIPT_DIR/scripts/validate-mcp.sh"; then
      check_failed=true
    fi
  else
    echo "Warning: scripts/validate-mcp.sh not found — skipping MCP validation"
  fi

  if [[ "$check_failed" == "true" ]]; then
    echo ""
    echo "Pre-flight checks failed. Fix the issues above or re-run with --skip-checks to bypass."
    exit 1
  fi

  echo ""
else
  echo "Skipping pre-flight checks (--skip-checks)"
  echo ""
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
INSTALLED_ITEMS=()

backup_if_exists() {
  local target="$1"
  if [[ -e "$target" && ! -L "$target" ]]; then
    local backup="${target}.backup.$(date +%Y%m%d%H%M%S)"
    echo "  Backing up existing $(basename "$target") -> $(basename "$backup")"
    mv "$target" "$backup"
  elif [[ -L "$target" ]]; then
    # Remove old symlink so we can replace it
    rm "$target"
  fi
}

install_file() {
  local src="$1"
  local dest="$2"

  backup_if_exists "$dest"

  if [[ "$MODE" == "dev" ]]; then
    ln -s "$src" "$dest"
    echo "  Linked $(basename "$dest") -> $src"
  else
    cp -R "$src" "$dest"
    echo "  Copied $(basename "$src") -> $dest"
  fi

  INSTALLED_ITEMS+=("$dest")
}

# ---------------------------------------------------------------------------
# Ensure target directories exist
# ---------------------------------------------------------------------------
mkdir -p "$CLAUDE_DIR"

echo "========================================"
echo "  claude-devkit installer"
echo "========================================"
echo ""
echo "Mode:       $MODE"
echo "Devkit dir: $DEVKIT_DIR"
echo "Claude dir: $CLAUDE_DIR"
echo ""

# ---------------------------------------------------------------------------
# Install skills
# ---------------------------------------------------------------------------
SKILLS_SRC="$DEVKIT_DIR/skills"
SKILLS_DEST="$CLAUDE_DIR/skills"

if [[ -d "$SKILLS_SRC" ]]; then
  mkdir -p "$SKILLS_DEST"
  skill_count=0

  while IFS= read -r skill_dir; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    install_file "$skill_dir" "$SKILLS_DEST/$skill_name"
    skill_count=$((skill_count + 1))
  done < <(fd --type d --max-depth 1 . "$SKILLS_SRC")

  if [[ $skill_count -eq 0 ]]; then
    echo "  No skills found in $SKILLS_SRC"
  else
    echo "  Installed $skill_count skill(s)"
  fi
else
  echo "  No skills/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install agents
# ---------------------------------------------------------------------------
AGENTS_SRC="$DEVKIT_DIR/agents"
AGENTS_DEST="$CLAUDE_DIR/agents"

if [[ -d "$AGENTS_SRC" ]]; then
  mkdir -p "$AGENTS_DEST"
  agent_count=0

  while IFS= read -r agent_file; do
    [[ -f "$agent_file" ]] || continue
    agent_name="$(basename "$agent_file")"
    install_file "$agent_file" "$AGENTS_DEST/$agent_name"
    agent_count=$((agent_count + 1))
  done < <(fd --type f --extension md --max-depth 1 . "$AGENTS_SRC")

  if [[ $agent_count -eq 0 ]]; then
    echo "  No agents found in $AGENTS_SRC"
  else
    echo "  Installed $agent_count agent(s)"
  fi
else
  echo "  No agents/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install guidelines
# ---------------------------------------------------------------------------
GUIDELINES_SRC="$DEVKIT_DIR/guidelines"
GUIDELINES_DEST="$CLAUDE_DIR/guidelines"

if [[ -d "$GUIDELINES_SRC" ]]; then
  mkdir -p "$GUIDELINES_DEST"
  guideline_count=0

  # Install subdirectories (e.g. coding/, document/)
  while IFS= read -r guideline_dir; do
    [[ -d "$guideline_dir" ]] || continue
    dir_name="$(basename "$guideline_dir")"
    mkdir -p "$GUIDELINES_DEST/$dir_name"
    install_file "$guideline_dir" "$GUIDELINES_DEST/$dir_name"
    guideline_count=$((guideline_count + 1))
  done < <(fd --type d --max-depth 1 . "$GUIDELINES_SRC")

  # Install top-level .md files (for forward compatibility)
  while IFS= read -r guideline_file; do
    [[ -f "$guideline_file" ]] || continue
    guideline_name="$(basename "$guideline_file")"
    install_file "$guideline_file" "$GUIDELINES_DEST/$guideline_name"
    guideline_count=$((guideline_count + 1))
  done < <(fd --type f --extension md --max-depth 1 . "$GUIDELINES_SRC")

  if [[ $guideline_count -eq 0 ]]; then
    echo "  No guidelines found in $GUIDELINES_SRC"
  else
    echo "  Installed $guideline_count guideline(s)"
  fi
else
  echo "  No guidelines/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install settings
# ---------------------------------------------------------------------------
SETTINGS_SRC="$DEVKIT_DIR/settings"

if [[ -d "$SETTINGS_SRC" ]]; then
  settings_count=0

  while IFS= read -r settings_file; do
    [[ -f "$settings_file" ]] || continue
    settings_name="$(basename "$settings_file")"
    install_file "$settings_file" "$CLAUDE_DIR/$settings_name"
    settings_count=$((settings_count + 1))
  done < <(fd --type f --max-depth 1 . "$SETTINGS_SRC")

  if [[ $settings_count -eq 0 ]]; then
    echo "  No settings files found in $SETTINGS_SRC"
  else
    echo "  Installed $settings_count settings file(s)"
  fi
else
  echo "  No settings/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install profiles (detection rules)
# ---------------------------------------------------------------------------
PROFILES_SRC="$DEVKIT_DIR/profiles"
PROFILES_DEST="$CLAUDE_DIR/profiles"

if [[ -d "$PROFILES_SRC" ]]; then
  mkdir -p "$PROFILES_DEST"
  profile_count=0

  while IFS= read -r profile_file; do
    [[ -f "$profile_file" ]] || continue
    profile_name="$(basename "$profile_file")"
    install_file "$profile_file" "$PROFILES_DEST/$profile_name"
    profile_count=$((profile_count + 1))
  done < <(fd --type f --max-depth 1 . "$PROFILES_SRC")

  if [[ $profile_count -eq 0 ]]; then
    echo "  No profiles found in $PROFILES_SRC"
  else
    echo "  Installed $profile_count profile(s)"
  fi
else
  echo "  No profiles/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install repo-config CLAUDE.md (optional)
# ---------------------------------------------------------------------------
if [[ -n "$REPO_CONFIG" ]]; then
  REPO_CONFIG_SRC="$DEVKIT_DIR/repo-configs/$REPO_CONFIG/CLAUDE.md"
  REPO_CONFIG_DEST="$(pwd)/CLAUDE.md"

  if [[ ! -f "$REPO_CONFIG_SRC" ]]; then
    echo "Error: repo-config type '$REPO_CONFIG' not found at $REPO_CONFIG_SRC"
    echo "Available types:"
    fd --type d --max-depth 1 . "$DEVKIT_DIR/repo-configs" --exec basename {} \; 2>/dev/null | while read -r t; do
      echo "  $t"
    done
    exit 1
  fi

  echo "Installing repo-config CLAUDE.md for type: $REPO_CONFIG"
  backup_if_exists "$REPO_CONFIG_DEST"
  cp "$REPO_CONFIG_SRC" "$REPO_CONFIG_DEST"
  echo "  Copied CLAUDE.md -> $REPO_CONFIG_DEST"
  INSTALLED_ITEMS+=("$REPO_CONFIG_DEST")
  echo ""
fi

# ---------------------------------------------------------------------------
# Write manifest (for uninstall tracking)
# ---------------------------------------------------------------------------
{
  echo "# claude-devkit manifest — generated $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# mode=$MODE"
  echo "# devkit_dir=$DEVKIT_DIR"
  for item in "${INSTALLED_ITEMS[@]}"; do
    echo "$item"
  done
} > "$MANIFEST_FILE"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "========================================"
echo "  Installation complete"
echo "========================================"
echo ""
echo "Installed ${#INSTALLED_ITEMS[@]} item(s) in $MODE mode."
echo "Manifest written to $MANIFEST_FILE"
echo ""
echo "To uninstall, run:"
echo "  $DEVKIT_DIR/uninstall.sh"
echo ""
if [[ "$MODE" == "dev" ]]; then
  echo "Dev mode: files are symlinked. Changes in $DEVKIT_DIR"
  echo "will be reflected immediately in $CLAUDE_DIR."
fi
echo ""
echo "To test MCP server connectivity, run the /validate-mcp skill in Claude Code."
