---
title: 'Hooks'
description: 'Deterministic enforcement of the constitution. PreToolUse:Bash safety, PostToolUse:Edit validator, SessionStart banner. Wired into ~/.claude/settings.json by install.sh.'
source: 'hooks/'
group: 'hooks'
order: 5500
---
# Hooks

Deterministic enforcement of `shared/constitution.md`. Three events:

- **PreToolUse:Bash** — blocks force-push, hard-reset on protected branches, `rm -rf $HOME`, unrequested PR merges, writes to `~/.config/adk/learning/archive/`, `--no-verify` bypasses.
- **PostToolUse:Edit\|Write** — validates SKILL.md frontmatter on writes; touches `.temp/<task-slug>/.last-modified`; refuses raw-token writes to `~/.config/adk/overrides.yaml`.
- **SessionStart** — prints the adk status banner.

`install.sh` merges these into `~/.claude/settings.json` with an `_adk_managed: true` tag so they're idempotent and removable on uninstall.

## hooks/hooks.json

```json
{
  "comment": "adk v3 hooks — wired into ~/.claude/settings.json by install.sh. The Bash safety hook enforces constitution §I deterministically; the Edit validator catches SKILL.md frontmatter bugs at write-time; the SessionStart banner runs at session open.",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Inspect the Bash command being run. BLOCK these with a precise reason:\n\n1. `git push --force` / `git push -f` / `git push --force-with-lease` targeting any of: main, master, develop, release/*, prod/*, or any branch listed in ~/.config/adk/overrides.yaml.protected_branches.\n2. `git reset --hard` on main, master, develop, release/*, prod/*.\n3. `git clean -fd` at a repo root (cwd ends in the repo's top-level dir).\n4. `git branch -D` on main, master, develop, release/*, prod/*.\n5. `rm -rf` targeting `$HOME`, `/`, any path under `~/.config/adk/`, or any repo root.\n6. `gh pr merge` UNLESS the user's most recent message in this session explicitly asked to merge a PR (look for words: merge, ship, land, squash-merge, rebase-merge).\n7. `gh pr close` UNLESS the user explicitly asked to close a PR.\n8. Any command writing into `~/.config/adk/learning/archive/` (that path is managed by /adk-improve only).\n9. `--no-verify` flags on git commit or git push (bypasses hooks — banned per constitution §V).\n\nALLOW: normal git, gh, npm, jq, fd, rg, curl, python3, ./install.sh, claude operations, and writes to .temp/<task-slug>/ paths.\n\nReturn JSON:\n  - block: {\"decision\":\"block\",\"reason\":\"<one-line reason naming the rule>\"}\n  - allow: {\"decision\":\"allow\"}"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Lightweight post-write check.\n\nIf the edited file path matches `*/skills/<skill>/SKILL.md`:\n  - Verify the YAML frontmatter has `name:` and `description:` fields.\n  - Verify `name:` value equals the folder basename (segment after `skills/` and before `/SKILL.md`).\n  - On mismatch, return {\"ok\":false,\"reason\":\"...\"}; otherwise {\"ok\":true}.\n\nIf the edited file path is under `.temp/<task-slug>/`:\n  - Append the current ISO-8601 UTC timestamp to a file `.temp/<task-slug>/.last-modified` (create if missing) so monitor tools can detect activity.\n  - Return {\"ok\":true}.\n\nIf the edited file path is `~/.config/adk/overrides.yaml`:\n  - Run a regex check that no line contains a raw token-looking value (`/^[A-Z_]+\\s*:\\s*['\"]?[a-zA-Z0-9_-]{20,}['\"]?$/` outside the `${VAR}` interpolation pattern).\n  - On match, return {\"ok\":false,\"reason\":\"raw token detected — use ${ENV_VAR} instead\"}.\n\nOtherwise: {\"ok\":true}."
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
# adk v3 SessionStart banner — short status line shown at the top of every Claude Code session.
# Reads ~/.config/adk/overrides.yaml + scripts/adk_mcp_health.py for the summary.
# Stays under 30 lines so it doesn't dominate the session opener.

set -uo pipefail

ADK_REPO="${ADK_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
OVERRIDES="$HOME/.config/adk/overrides.yaml"

echo "[adk v3] — 8 skills: /adk-implement /adk-review /adk-investigate /adk-document /adk-sync /adk-setup /adk-improve /adk-explain"

if [ ! -f "$OVERRIDES" ]; then
  echo "[adk v3] ⚠ no ~/.config/adk/overrides.yaml — run /adk-setup --init"
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
proposals_dir="$HOME/.config/adk/learning/proposals"
if [ -d "$proposals_dir" ]; then
  count=$(find "$proposals_dir" -maxdepth 1 -type f -name '*.diff' 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" -gt 0 ]; then
    echo "[adk v3] $count pending /adk-improve proposals — run /adk-improve to review"
  fi
fi

```
