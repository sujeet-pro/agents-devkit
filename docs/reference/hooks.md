---
title: 'Hooks'
description: 'Deterministic enforcement of the constitution. PreToolUse:Bash safety, PostToolUse:Edit validator, SessionStart banner. Wired into ~/.claude/settings.json by install.sh.'
source: 'hooks/'
group: 'hooks'
order: 5500
---
# Hooks

Deterministic enforcement of `shared/constitution.md`. Three events:

- **PreToolUse:Bash** — blocks force-push, hard-reset on protected branches, `rm -rf $HOME`, unrequested PR merges, writes to `$ADK_DATA_HOME/improve/learning/archive/`, `--no-verify` bypasses.
- **PostToolUse:Edit\|Write** — validates SKILL.md frontmatter on writes; touches `.temp/<task-slug>/.last-modified`; refuses raw-token writes to `$ADK_CONFIG_HOME/overrides.yaml`.
- **SessionStart** — prints the adk status banner.

`install.sh` merges these into `~/.claude/settings.json` with an `_adk_managed: true` tag so they're idempotent and removable on uninstall.

## hooks/hooks.json

```json
{
  "comment": "adk v4 hooks — wired into ~/.claude/settings.json by install.sh. The Edit validator catches SKILL.md frontmatter bugs at write-time + scans config writes for raw tokens; the SessionStart banner runs at session open. The prompt-style PreToolUse Bash safety hook was removed 2026-05-19 (over-broad LLM interpretation produced too many false positives); the constitution §I rules still bind the assistant directly.",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Lightweight post-write check.\n\nIf the edited file path matches `*/skills/<skill>/SKILL.md`:\n  - Verify the YAML frontmatter has `name:` and `description:` fields.\n  - Verify `name:` value equals the folder basename (segment after `skills/` and before `/SKILL.md`).\n  - On mismatch, return {\"ok\":false,\"reason\":\"...\"}; otherwise {\"ok\":true}.\n\nIf the edited file path is under `.temp/<task-slug>/`:\n  - Append the current ISO-8601 UTC timestamp to a file `.temp/<task-slug>/.last-modified` (create if missing) so monitor tools can detect activity.\n  - Return {\"ok\":true}.\n\nIf the edited file path is `$ADK_CONFIG_HOME/core.yaml` or `$ADK_CONFIG_HOME/connectors/*.md` (frontmatter section between the leading `---` lines) or `$ADK_CONFIG_HOME/adk-cli.json5`:\n  - Run a regex check that no line contains a raw token-looking value (`/^[A-Z_]+\\s*:\\s*['\"]?[a-zA-Z0-9_-]{20,}['\"]?$/` outside the `${VAR}` interpolation pattern).\n  - On match, return {\"ok\":false,\"reason\":\"raw token detected — use ${ENV_VAR} instead\"}.\n\nOtherwise: {\"ok\":true}."
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${ADK_REPO}/hooks/banner.sh\""
          }
        ]
      }
    ]
  }
}
```

## hooks/banner.sh

```bash
#!/usr/bin/env bash
# adk v4 SessionStart banner — short status line shown at the top of every Claude Code session.
# Reads $ADK_CONFIG_HOME/core.yaml + scripts/adk_mcp_health.py for the summary.
# Stays under 30 lines so it doesn't dominate the session opener.

set -uo pipefail

ADK_REPO="${ADK_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
CORE_YAML="$ADK_CONFIG_HOME/core.yaml"

echo "[adk v4] — 9 skills: /adk-implement /adk-review /adk-pr-review /adk-investigate /adk-document /adk-sync /adk-setup /adk-improve /adk-explain"

if [ ! -f "$CORE_YAML" ]; then
  echo "[adk v4] ⚠ no $ADK_CONFIG_HOME/core.yaml — run /adk-setup --init"
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
  [ -n "$summary" ] && echo "[adk v4] $summary"
fi

# Surface pending improve proposals if any
proposals_dir="$ADK_DATA_HOME/improve/learning/proposals"
if [ -d "$proposals_dir" ]; then
  count=$(find "$proposals_dir" -maxdepth 1 -type f -name '*.diff' 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" -gt 0 ]; then
    echo "[adk v4] $count pending /adk-improve proposals — run /adk-improve to review"
  fi
fi

```
