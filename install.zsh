#!/usr/bin/env zsh
set -euo pipefail

# DevKit installer
# Idempotent: run for fresh install, or re-run to update after local edits / git pull / env var changes.
# By default, symlinks all skills/agents/settings/profiles (for contributors with live edits).
# Use --copy to copy files instead of symlinking (for testing without live edits).
# Also force-reconfigures MCP servers from current environment variables.
#
# For regular users (non-contributors), use the /plugin method or SETUP.md instead.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEVKIT_DIR="${CLAUDE_DEVKIT_DIR:-$SCRIPT_DIR}"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
MANIFEST_FILE="$CLAUDE_DIR/.devkit-manifest"

SKIP_CHECKS=false
COPY_MODE=false

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --skip-checks)
      SKIP_CHECKS=true
      ;;
    --copy)
      COPY_MODE=true
      ;;
    --list)
      echo "DevKit — available skills, agents, and guidelines"
      echo ""
      echo "Skills:"
      if [[ -d "$DEVKIT_DIR/skills" ]]; then
        for skill_dir in "$DEVKIT_DIR/skills"/*/; do
          [[ -d "$skill_dir" ]] || continue
          skill_name="$(basename "$skill_dir")"
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
      if [[ -d "$DEVKIT_DIR/skills/_references/guidelines" ]]; then
        for guideline_dir in "$DEVKIT_DIR/skills/_references/guidelines"/*/; do
          [[ -d "$guideline_dir" ]] || continue
          dir_name="$(basename "$guideline_dir")"
          count=$(fd --type f --extension md --max-depth 1 . "$guideline_dir" | wc -l | tr -d ' ')
          echo "  $dir_name/ ($count guidelines)"
        done
      fi
      exit 0
      ;;
    --help|-h)
      echo "Usage: install.zsh [--skip-checks] [--copy] [--list]"
      echo ""
      echo "Idempotent installer for DevKit contributors."
      echo "Symlinks (or copies with --copy) all skills/agents/settings/profiles"
      echo "into ~/.claude/ and force-reconfigures MCP servers from current environment variables."
      echo ""
      echo "Run this script to:"
      echo "  - Fresh install after cloning the repo"
      echo "  - Update after editing local files or running git pull"
      echo "  - Reconfigure MCP servers after updating env vars (e.g. expired tokens)"
      echo ""
      echo "For regular users, use the /plugin method in Claude Code:"
      echo "  /plugin marketplace add sujeet-pro/agents-devkit"
      echo "  /plugin install devkit@devkit-marketplace"
      echo ""
      echo "Options:"
      echo "  --skip-checks   Skip prerequisite and env var validation checks"
      echo "  --copy          Copy files instead of symlinking (for testing without live edits)"
      echo "  --list          List all available skills, agents, and guidelines"
      echo ""
      echo "Environment variables:"
      echo "  CLAUDE_DEVKIT_DIR  Override auto-detected devkit directory"
      echo "  CLAUDE_DIR         Override default ~/.claude/ directory"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Run install.zsh --help for usage."
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Pre-flight checks (prerequisite tools, env vars)
# ---------------------------------------------------------------------------
if [[ "$SKIP_CHECKS" == "false" ]]; then
  check_failed=false

  if [[ -f "$SCRIPT_DIR/scripts/check-prerequisites.zsh" ]]; then
    if ! zsh "$SCRIPT_DIR/scripts/check-prerequisites.zsh"; then
      check_failed=true
    fi
  else
    echo "Warning: scripts/check-prerequisites.zsh not found — skipping prerequisite check"
  fi

  if [[ -f "$SCRIPT_DIR/scripts/check-env.zsh" ]]; then
    if ! zsh "$SCRIPT_DIR/scripts/check-env.zsh"; then
      check_failed=true
    fi
  else
    echo "Warning: scripts/check-env.zsh not found — skipping env var check"
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

force_link() {
  local src="$1"
  local dest="$2"

  # Remove existing symlink or back up non-symlink file
  if [[ -L "$dest" ]]; then
    rm "$dest"
  elif [[ -e "$dest" ]]; then
    local backup="${dest}.backup.$(date +%Y%m%d%H%M%S)"
    echo "  Backing up existing $(basename "$dest") -> $(basename "$backup")"
    mv "$dest" "$backup"
  fi

  if [[ "$COPY_MODE" == "true" ]]; then
    if [[ -d "$src" ]]; then
      cp -R "$src" "$dest"
    else
      cp "$src" "$dest"
    fi
  else
    ln -s "$src" "$dest"
  fi
  INSTALLED_ITEMS+=("$dest")
}

# ---------------------------------------------------------------------------
# Ensure target directories exist
# ---------------------------------------------------------------------------
mkdir -p "$CLAUDE_DIR"

echo "========================================"
echo "  DevKit installer"
echo "========================================"
echo ""
echo "Devkit dir: $DEVKIT_DIR"
echo "Claude dir: $CLAUDE_DIR"
echo ""

# ---------------------------------------------------------------------------
# Install skills (individual symlinks — coexists with /plugin installs)
# ---------------------------------------------------------------------------
SKILLS_SRC="$DEVKIT_DIR/skills"
SKILLS_DEST="$CLAUDE_DIR/skills"

echo "Skills:"
if [[ -d "$SKILLS_SRC" ]]; then
  mkdir -p "$SKILLS_DEST"
  skill_count=0

  while IFS= read -r skill_dir; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    force_link "$skill_dir" "$SKILLS_DEST/$skill_name"
    skill_count=$((skill_count + 1))
  done <<< "$(fd --type d --max-depth 1 . "$SKILLS_SRC")"

  echo "  Linked $skill_count skill(s)"
else
  echo "  No skills/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install agents
# ---------------------------------------------------------------------------
AGENTS_SRC="$DEVKIT_DIR/agents"
AGENTS_DEST="$CLAUDE_DIR/agents"

echo "Agents:"
if [[ -d "$AGENTS_SRC" ]]; then
  mkdir -p "$AGENTS_DEST"
  agent_count=0

  while IFS= read -r agent_file; do
    [[ -f "$agent_file" ]] || continue
    agent_name="$(basename "$agent_file")"
    force_link "$agent_file" "$AGENTS_DEST/$agent_name"
    agent_count=$((agent_count + 1))
  done <<< "$(fd --type f --extension md --max-depth 1 . "$AGENTS_SRC")"

  echo "  Linked $agent_count agent(s)"
else
  echo "  No agents/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install guidelines (sourced from skills/_references/guidelines/)
# ---------------------------------------------------------------------------
GUIDELINES_SRC="$DEVKIT_DIR/skills/_references/guidelines"
GUIDELINES_DEST="$CLAUDE_DIR/guidelines"

echo "Guidelines:"
if [[ -d "$GUIDELINES_SRC" ]]; then
  mkdir -p "$GUIDELINES_DEST"
  guideline_count=0

  while IFS= read -r guideline_dir; do
    [[ -d "$guideline_dir" ]] || continue
    dir_name="$(basename "$guideline_dir")"
    mkdir -p "$GUIDELINES_DEST/$dir_name"
    force_link "$guideline_dir" "$GUIDELINES_DEST/$dir_name"
    guideline_count=$((guideline_count + 1))
  done <<< "$(fd --type d --max-depth 1 . "$GUIDELINES_SRC")"

  while IFS= read -r guideline_file; do
    [[ -f "$guideline_file" ]] || continue
    guideline_name="$(basename "$guideline_file")"
    force_link "$guideline_file" "$GUIDELINES_DEST/$guideline_name"
    guideline_count=$((guideline_count + 1))
  done <<< "$(fd --type f --extension md --max-depth 1 . "$GUIDELINES_SRC")"

  echo "  Linked $guideline_count guideline(s)"
else
  echo "  No skills/_references/guidelines/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install settings: merge contextInstructions into settings.json + symlink .md files
# ---------------------------------------------------------------------------
SETTINGS_SRC="$DEVKIT_DIR/settings"

echo "Settings:"
if [[ -d "$SETTINGS_SRC" ]]; then
  settings_count=0

  # Merge contextInstructions from base-settings.json into ~/.claude/settings.json
  BASE_SETTINGS="$SETTINGS_SRC/base-settings.json"
  SETTINGS_TARGET="$CLAUDE_DIR/settings.json"

  if [[ -f "$BASE_SETTINGS" ]] && command -v jq &>/dev/null; then
    # Ensure settings.json exists
    if [[ ! -f "$SETTINGS_TARGET" ]]; then
      echo '{}' > "$SETTINGS_TARGET"
    fi

    # Merge all devkit-managed settings into settings.json
    # base-settings.json keys overwrite settings.json keys; user-only keys are preserved
    tmp_settings="$(mktemp)"
    jq -s '.[0] * .[1]' "$SETTINGS_TARGET" "$BASE_SETTINGS" > "$tmp_settings"
    mv "$tmp_settings" "$SETTINGS_TARGET"

    managed_keys="$(jq -r 'keys | join(", ")' "$BASE_SETTINGS")"
    echo "  Merged devkit settings ($managed_keys) into $SETTINGS_TARGET"
    settings_count=$((settings_count + 1))
    INSTALLED_ITEMS+=("settings:contextInstructions")
  fi

  # Symlink non-JSON files (markdown reference docs)
  while IFS= read -r settings_file; do
    [[ -f "$settings_file" ]] || continue
    [[ "$settings_file" == *.json ]] && continue  # skip JSON files (merged above)
    settings_name="$(basename "$settings_file")"
    force_link "$settings_file" "$CLAUDE_DIR/$settings_name"
    settings_count=$((settings_count + 1))
  done <<< "$(fd --type f --max-depth 1 . "$SETTINGS_SRC")"

  echo "  Configured $settings_count settings item(s)"
else
  echo "  No settings/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install profiles (detection rules)
# ---------------------------------------------------------------------------
PROFILES_SRC="$DEVKIT_DIR/profiles"
PROFILES_DEST="$CLAUDE_DIR/profiles"

echo "Profiles:"
if [[ -d "$PROFILES_SRC" ]]; then
  mkdir -p "$PROFILES_DEST"
  profile_count=0

  while IFS= read -r profile_file; do
    [[ -f "$profile_file" ]] || continue
    profile_name="$(basename "$profile_file")"
    force_link "$profile_file" "$PROFILES_DEST/$profile_name"
    profile_count=$((profile_count + 1))
  done <<< "$(fd --type f --max-depth 1 . "$PROFILES_SRC")"

  echo "  Linked $profile_count profile(s)"
else
  echo "  No profiles/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Install scripts (multi-model detection, execution, context assembly)
# ---------------------------------------------------------------------------
SCRIPTS_SRC="$DEVKIT_DIR/scripts"
SCRIPTS_DEST="$CLAUDE_DIR/scripts"

echo "Scripts:"
if [[ -d "$SCRIPTS_SRC" ]]; then
  mkdir -p "$SCRIPTS_DEST"
  script_count=0

  while IFS= read -r script_file; do
    [[ -f "$script_file" ]] || continue
    script_name="$(basename "$script_file")"
    force_link "$script_file" "$SCRIPTS_DEST/$script_name"
    script_count=$((script_count + 1))
  done <<< "$(fd --type f --max-depth 1 . "$SCRIPTS_SRC")"

  echo "  Linked $script_count script(s)"
else
  echo "  No scripts/ directory found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Force-reconfigure MCP servers into ~/.claude.json
# Always resolves from current env vars — handles fresh install, token rotation, etc.
# ---------------------------------------------------------------------------
CLAUDE_JSON_TEMPLATE="$DEVKIT_DIR/claude.json"
CLAUDE_JSON_TARGET="$HOME/.claude.json"

echo "MCP servers:"
if [[ -f "$CLAUDE_JSON_TEMPLATE" ]]; then
  if ! command -v envsubst &>/dev/null; then
    echo "  Warning: envsubst not found — skipping MCP server configuration"
    echo "  Install with: brew install gettext"
  elif ! command -v jq &>/dev/null; then
    echo "  Warning: jq not found — skipping MCP server configuration"
    echo "  Install with: brew install jq"
  else
    ENVSUBST_VARS='$CONFLUENCE_URL $CONFLUENCE_USERNAME $CONFLUENCE_API_TOKEN $BITBUCKET_URL $BITBUCKET_USERNAME $BITBUCKET_WORKSPACE $BITBUCKET_TOKEN $GOOGLE_DRIVE_OAUTH_CREDENTIALS'
    resolved_json="$(envsubst "$ENVSUBST_VARS" < "$CLAUDE_JSON_TEMPLATE")"

    if ! echo "$resolved_json" | jq empty 2>/dev/null; then
      echo "  Error: resolved claude.json is not valid JSON — skipping MCP server configuration"
    else
      mcp_server_names="$(echo "$resolved_json" | jq -r '.mcpServers | keys[]')"

      if [[ ! -f "$CLAUDE_JSON_TARGET" ]]; then
        echo '{}' > "$CLAUDE_JSON_TARGET"
      fi

      # Remove previously-managed devkit servers (handles servers removed from template)
      if [[ -f "$MANIFEST_FILE" ]]; then
        while IFS= read -r line; do
          if [[ "$line" == mcp:* ]]; then
            old_server="${line#mcp:}"
            if ! echo "$resolved_json" | jq -e ".mcpServers.\"$old_server\"" &>/dev/null; then
              # Server was in old manifest but not in current template — remove it
              tmp_rm="$(jq "del(.mcpServers.\"$old_server\")" "$CLAUDE_JSON_TARGET")"
              echo "$tmp_rm" > "$CLAUDE_JSON_TARGET"
              echo "  Removed stale MCP server: $old_server"
            fi
          fi
        done < "$MANIFEST_FILE"
      fi

      # Shallow merge: replace each devkit-managed server entirely (no deep merge)
      merged="$(echo "$resolved_json" | jq -s '
        .[0] + {mcpServers: ((.[0].mcpServers // {}) + .[1].mcpServers)}
      ' "$CLAUDE_JSON_TARGET" -)"

      tmp_claude_json="$(mktemp)"
      echo "$merged" > "$tmp_claude_json"
      mv "$tmp_claude_json" "$CLAUDE_JSON_TARGET"

      server_count="$(echo "$resolved_json" | jq '.mcpServers | length')"
      echo "  Configured $server_count MCP server(s) in $CLAUDE_JSON_TARGET"

      for name in $mcp_server_names; do
        INSTALLED_ITEMS+=("mcp:$name")
      done
    fi
  fi
else
  echo "  No claude.json template found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Node.js dependencies (shared utilities in lib/)
# ---------------------------------------------------------------------------
echo "Node.js utilities:"
if [[ -f "$DEVKIT_DIR/scripts/setup-node.zsh" ]]; then
  if command -v node &>/dev/null && command -v npm &>/dev/null; then
    if zsh "$DEVKIT_DIR/scripts/setup-node.zsh" 2>/dev/null; then
      echo "  Node.js dependencies installed"
    else
      echo "  Warning: Node.js dependency install failed (non-fatal)"
    fi
  else
    echo "  Skipping: node or npm not found (optional — needed for advanced skill utilities)"
  fi
else
  echo "  No scripts/setup-node.zsh found — skipping"
fi
echo ""

# ---------------------------------------------------------------------------
# Write manifest (for uninstall tracking)
# ---------------------------------------------------------------------------
{
  echo "# DevKit manifest — generated $(date -u +%Y-%m-%dT%H:%M:%SZ)"
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
echo "Installed ${#INSTALLED_ITEMS[@]} item(s)."
if [[ "$COPY_MODE" == "true" ]]; then
  echo "Mode: copy (files copied, not symlinked)"
else
  echo "Mode: symlink (changes reflect immediately)"
fi
echo "MCP servers configured from current environment variables."
echo ""
echo "Re-run this script to:"
echo "  - Pick up new skills/agents after git pull or local edits"
echo "  - Reconfigure MCP servers after updating env vars in ~/.zshenv"
echo ""
echo "To update:    /devkit:manage-update (inside Claude Code) or zsh scripts/update-devkit.zsh"
echo "To uninstall: zsh $DEVKIT_DIR/uninstall.zsh"
echo "To test MCP:  /devkit:manage-validate (inside Claude Code)"
