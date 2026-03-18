#!/usr/bin/env zsh
set -euo pipefail

# Assemble a self-contained prompt for external CLI tools.
# Gathers skill instructions, guidelines, CLAUDE.md, and the user's task
# into a single prompt that any AI CLI can process without devkit access.
#
# Usage: assemble-context.zsh --task "task description" [--skill name] [--guideline path]... [--claude-md path] [--extra "text"]

TASK=""
SKILL_NAME=""
GUIDELINE_PATHS=()
CLAUDE_MD=""
EXTRA_CONTEXT=""
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task) TASK="$2"; shift 2 ;;
    --skill) SKILL_NAME="$2"; shift 2 ;;
    --guideline) GUIDELINE_PATHS+=("$2"); shift 2 ;;
    --claude-md) CLAUDE_MD="$2"; shift 2 ;;
    --extra) EXTRA_CONTEXT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$TASK" ]]; then
  echo "Error: --task is required" >&2
  exit 1
fi

{
  cat <<'HEADER'
You are a Principal Engineer. All output must be technically accurate, actionable,
and cite authoritative sources where applicable. Address performance, security,
accessibility, maintainability, DX, and cost implications.
HEADER

  echo ""
  echo "# Task"
  echo ""
  echo "$TASK"
  echo ""

  # Project CLAUDE.md
  if [[ -n "$CLAUDE_MD" && -f "$CLAUDE_MD" ]]; then
    echo "# Project Instructions"
    echo ""
    cat "$CLAUDE_MD"
    echo ""
  fi

  # Skill instructions
  if [[ -n "$SKILL_NAME" ]]; then
    skill_file="$CLAUDE_DIR/skills/$SKILL_NAME/SKILL.md"
    if [[ -f "$skill_file" ]]; then
      echo "# Skill Instructions: $SKILL_NAME"
      echo ""
      cat "$skill_file"
      echo ""
    fi
  fi

  # Guidelines
  for gpath in "${GUIDELINE_PATHS[@]}"; do
    if [[ -f "$gpath" ]]; then
      echo "# Guideline: $(basename "$gpath" .md)"
      echo ""
      cat "$gpath"
      echo ""
    fi
  done

  # Extra context
  if [[ -n "$EXTRA_CONTEXT" ]]; then
    echo "# Additional Context"
    echo ""
    echo "$EXTRA_CONTEXT"
    echo ""
  fi

  cat <<'FOOTER'
# Output Requirements

- Return your complete response in markdown format.
- Be thorough, specific, and actionable.
- Cite sources for factual claims.
- Do NOT ask clarifying questions — work with the information provided.
FOOTER
}
