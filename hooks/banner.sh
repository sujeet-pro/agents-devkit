#!/usr/bin/env bash
# adk v5 SessionStart banner — short status line shown at the top of every Claude Code session.
# Reads $ADK_CONFIG_HOME/core.json5 + scripts/adk_mcp_health.py for the summary.
# Stays under 30 lines so it doesn't dominate the session opener.

set -uo pipefail

: "${ADK_DATA_HOME:?ADK_DATA_HOME unset — see ~/personal/mac-setup/configs/shell/.zshenv.example}"
: "${ADK_CONFIG_HOME:?ADK_CONFIG_HOME unset — see ~/personal/mac-setup/configs/shell/.zshenv.example}"
: "${ADK_MEMORY_HOME:?ADK_MEMORY_HOME unset — see ~/personal/mac-setup/configs/shell/.zshenv.example}"

ADK_REPO="${ADK_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
CORE_JSON5="$ADK_CONFIG_HOME/core.json5"

FIRST_NAME=$(python3 -c "import json5,sys; print(json5.load(open(sys.argv[1]))['user'].get('first_name','adk'))" "$CORE_JSON5" 2>/dev/null || echo "adk")

echo "[adk v5] — 9 skills: /adk-implement /adk-review /adk-pr-review /adk-investigate /adk-document /adk-sync /adk-setup /adk-improve /adk-explain"

if [ ! -f "$CORE_JSON5" ]; then
  echo "[adk v5] ⚠ ADK_CONFIG_HOME=$ADK_CONFIG_HOME has no core.json5 — edit the scaffolded template to add your details"
  exit 0
fi

echo "[adk v5] hi $FIRST_NAME"

# One-line health summary
if command -v python3 >/dev/null 2>&1 && [ -f "$ADK_REPO/scripts/adk_mcp_health.py" ]; then
  summary=$(python3 "$ADK_REPO/scripts/adk_mcp_health.py" --json 2>/dev/null \
    | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ok = sum(1 for m in d.get('mcps', []) if m.get('status') == 'env-ok')
miss = sum(1 for m in d.get('mcps', []) if m.get('status') == 'env-missing')
env_present = sum(1 for v in d.get('env_vars', {}).values() if v.startswith('present'))
env_missing = sum(1 for v in d.get('env_vars', {}).values() if v == 'MISSING')
print(f'MCPs: {ok} env-ok, {miss} env-missing  ·  env: {env_present} present, {env_missing} missing')
" 2>/dev/null)
  [ -n "$summary" ] && echo "[adk v5] $summary"
fi

# Surface pending improve proposals if any
proposals_dir="$ADK_MEMORY_HOME/learning/proposals"
if [ -d "$proposals_dir" ]; then
  count=$(find "$proposals_dir" -maxdepth 1 -type f -name '*.diff' 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" -gt 0 ]; then
    echo "[adk v5] $count pending /adk-improve proposals — run /adk-improve to review"
  fi
fi
