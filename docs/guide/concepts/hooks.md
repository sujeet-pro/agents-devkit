---
title: Hooks
description: PreToolUse:Bash safety blocker, PostToolUse:Edit validator, SessionStart banner. Deterministic enforcement of the constitution, wired into ~/.claude/settings.json by install.sh.
order: 11
---

# Hooks (deterministic enforcement)

`shared/constitution.md` lists hard rules: no force-push, no merge from a skill, no `rm -rf $HOME`, no `--no-verify`, etc. Without hooks, those are advisory — the agent COULD follow them, and usually does, but nothing stops a buggy run from breaking the rules.

Hooks make the constitution real.

Source: `hooks/hooks.json` + `hooks/banner.sh`.

## Three events

### 1. PreToolUse:Bash (safety blocker)

Inspects every `Bash` invocation before it runs. Blocks (with a precise reason in the agent's transcript):

- `git push --force` / `--force-with-lease` to main / master / develop / release/* / prod/* or any branch in `overrides.yaml.protected_branches`
- `git reset --hard` on protected branches
- `git clean -fd` at a repo root
- `git branch -D main` / `master` / `develop` / `release/*` / `prod/*`
- `rm -rf` targeting `$HOME`, `/`, anything under `~/.config/adk/`, or any repo root
- `gh pr merge` UNLESS the user explicitly asked to merge a PR in the current session
- `gh pr close` UNLESS the user explicitly asked
- Any command writing into `~/.config/adk/learning/archive/` (only `/adk-improve` writes there)
- `--no-verify` flags on `git commit` or `git push`

Allows: normal `git`, `gh`, `npm`, `jq`, `fd`, `rg`, `curl`, `python3`, `./install.sh`, `claude` operations, and writes to `.temp/<task-slug>/` paths.

### 2. PostToolUse:Edit|Write (validator)

After any `Edit` or `Write`:

- If the edited file is a `*/skills/<skill>/SKILL.md`: verifies YAML frontmatter has `name:` and `description:`, and that `name:` matches the folder basename.
- If the edited file is under `.temp/<task-slug>/`: touches `.temp/<task-slug>/.last-modified` so monitors can detect activity.
- If the edited file is `~/.config/adk/overrides.yaml`: regex-checks for raw token-looking values (`/^[A-Z_]+:\s*['"]?[a-zA-Z0-9_-]{20,}['"]?$/` outside `${VAR}` patterns). Refuses if a likely secret is detected.

### 3. SessionStart (banner)

Prints a one-screen status at session open:

```
[adk v3] — 8 skills: /adk-implement /adk-review /adk-investigate /adk-document /adk-sync /adk-setup /adk-improve /adk-explain
[adk v3] MCPs: 6 env-ok, 2 env-missing  ·  env: 12 present, 4 missing
[adk v3] 3 pending /adk-improve proposals — run /adk-improve to review
```

Uses `scripts/adk_mcp_health.py --json` for the health summary. Surfaces pending `/adk-improve` proposals when they exist.

## How they're installed

`install.sh --target claude` merges `hooks/hooks.json` into `~/.claude/settings.json` with each entry tagged `_adk_managed: true`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "_adk_managed": true,
        "matcher": "Bash",
        "hooks": [{ "type": "prompt", "prompt": "..." }]
      }
    ],
    "PostToolUse": [...],
    "SessionStart": [...]
  }
}
```

The marker makes the merge idempotent (re-running `install.sh` replaces only adk-managed entries — user-authored hooks are left untouched) and removable (`install.sh --uninstall --target claude` strips them).

## Why only Claude Code

Cursor, Codex CLI, and Junie don't have an equivalent hook system. In those environments, the constitution is enforced by advisor prose only.

If you need the safety guarantees outside Claude Code, run agents-as-CLI (Claude Code in a subprocess) or wait for the agent ecosystem to land a hooks equivalent.

## Customizing

To add a custom rule:

1. Edit `hooks/hooks.json`. Add your entry — `_adk_managed: true` is set automatically by `install.py` during merge.
2. Re-run `./install.sh --target claude`.

To remove all adk hooks:

```bash
./install.sh --uninstall --target claude
```

To remove a SINGLE adk hook without uninstalling everything: edit `~/.claude/settings.json` and remove the specific entry. Re-running `install.sh` will re-add it; if you want it permanently gone, also edit `hooks/hooks.json` in the repo to remove the source.

## Next

- [Project-scoped overrides](../usage/project-scoped.md)
- [Decision logs](./decision-logs.md)
