#!/usr/bin/env bash
# adk v3 SessionStart banner — short status line shown at the top of every Claude Code session.
# Reads ~/.agents-devkit/config/overrides.yaml + scripts/adk_mcp_health.py for the summary.
# Stays under 30 lines so it doesn't dominate the session opener.

set -uo pipefail

ADK_REPO="${ADK_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
OVERRIDES="$HOME/.agents-devkit/config/overrides.yaml"

echo "[adk v3] — 8 skills: /adk-implement /adk-review /adk-investigate /adk-document /adk-sync /adk-setup /adk-improve /adk-explain"

if [ ! -f "$OVERRIDES" ]; then
  echo "[adk v3] ⚠ no ~/.agents-devkit/config/overrides.yaml — run /adk-setup --init"
  exit 0
fi

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
  [ -n "$summary" ] && echo "[adk v3] $summary"
fi

# Surface pending improve proposals if any
proposals_dir="$HOME/.agents-devkit/improve/learning/proposals"
if [ -d "$proposals_dir" ]; then
  count=$(find "$proposals_dir" -maxdepth 1 -type f -name '*.diff' 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" -gt 0 ]; then
    echo "[adk v3] $count pending /adk-improve proposals — run /adk-improve to review"
  fi
fi
