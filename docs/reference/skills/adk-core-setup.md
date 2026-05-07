---
title: 'adk-core:setup'
description: '  Bootstrap a fresh adk install on a machine. Creates ~/.config/adk/*.md from templates (info, repos, github, datadog, mixpanel, statsig, snowflake, slack, review, docs); checks CLI deps (gh, jq, fd, ripgrep, fzf, node, docker); checks `gh auth status`; lists missing env vars referenced by every plugin''s .mcp.json; and reports Claude Code vs Claude Desktop connector requirements. Claude Desktop does not load plugin-local .mcp.json, so this skill tells the user exactly which connector or custom MCP must be configured there before dependent skills run. Use the first time you install adk on a machine, after a major OS upgrade, when adding a new MCP integration, or when a skill complains about a missing meta-info field / connector / dependency. Do NOT use to manage skill code or plugin manifests (that''s manual file editing). Do NOT use to auto-install Homebrew or Docker (it surfaces the install command but won''t run it). Do NOT use to auto-edit ~/.zshenv (it prints the export lines but doesn''t append).'
plugin: 'adk-core'
skill: 'setup'
source: 'plugins/adk-core/skills/setup/SKILL.md'
group: 'core-skills'
order: 106
---
# adk-core:setup

## Source

`plugins/adk-core/skills/setup/SKILL.md`

## Skill Body

# setup — bootstrap adk on a machine

Idempotent. Safe to re-run. Does nothing if everything is already in place.

## When to use

- First-time install of adk on a machine.
- After a major macOS / Linux OS upgrade.
- After adding a new MCP integration to a plugin's `.mcp.json`.
- When a skill complains "meta-info `<topic>` missing key X".

## When NOT to use

- Editing skill code → just edit the file.
- Updating workspace connectors → that's the workspace admin's job.
- Auto-installing system tools — this skill surfaces the install command but does NOT run `brew install` for you.
- Modifying `~/.zshenv` — this skill prints the `export` lines but does NOT append them.

## Common prompts

- "set up adk"
- "configure datadog for adk"
- "missing config: <topic>"
- "first run on this laptop"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `--target <topic\|all>` | optional | `all` |
| `--mode auto\|fix` | optional | `auto` (= ask before each install/edit) |
| `--auto` | optional | skip approval gates entirely (still doesn't auto-install / auto-edit shell rc) |

## Workflow

```
Phase 0 — prompt expand
  - Determine target (all topics or a single one).
  - Determine mode (auto = gated, fix = unattended).

Phase 1 — platform check
  - macOS: full support.
  - Linux: full support (apt/dnf install hints instead of brew).
  - Windows: hard-fail; suggest WSL2.

Phase 2 — CLI deps
  - For each: gh, jq, fd, ripgrep, fzf, node>=18, docker.
  - Run `command -v`. Surface install command for missing.
  - Under --auto: just report. Under --mode fix: still does NOT run brew install (footgun); only prints the command.

Phase 3 — gh auth
  - Run `gh auth status`. If not authed, prompt user to run `gh auth login`.

Phase 4 — meta-info topics (per --target)
  For each topic:
    - If file ~/.config/adk/<topic>.md doesn't exist, copy from templates/<topic>.md.
    - Open in user's $EDITOR (or `default_editor` from info.md, fallback nvim/vi).
    - On save, run `bin/adk-info <topic> --check`.
    - Re-open if invalid.

Phase 5 — env-var and connector check
  - Parse every .mcp.json in installed plugins for `${VAR}` references.
  - For each, check process env.
  - Print exact `export` lines for missing ones.
  - Detect runtime when possible:
    - Claude Code: plugin-local .mcp.json can load shipped MCP servers.
    - Claude Desktop: plugin-local .mcp.json is ignored; print the custom
      connector name, endpoint/command, and required env vars the user must
      configure in Desktop or their workspace.
  - List workspace connectors consumed but not shipped (Atlassian, Google
    Drive, Slack, Mixpanel, Snowflake, Gmail, Google Calendar) and tell the
    user which skills require each connector.

Phase 6 — final report
  - Summary table: deps OK / missing, gh authed Y/N, meta-info OK / missing fields, env vars present / missing.
  - Reminder to source ~/.zshenv + restart Claude Code if any env vars were added.
```

## Persona

> You are a careful infra engineer setting up a new workstation. You verify before claiming, you tell the user exactly what to do, and you NEVER edit their `~/.zshenv` automatically.

See `references/persona.md`.

## Constitution

**Must do:**

1. Be idempotent — safe to re-run.
2. Show exact `export` lines for missing tokens.
3. Never commit raw secrets to `~/.config/adk/*.md` — enforce the regex check.
4. Walk topics in dependency order: `info` → `repos` → (per-plugin topics) → `slack` → `review` → `docs`.
5. Validate each topic file with `bin/adk-info <topic> --check` after editing.
6. Explain Claude Desktop connector setup whenever a required MCP is only
   declared in plugin-local `.mcp.json`.
7. Separate required-now dependencies from optional capabilities and tell the
   user how to skip a check only when the selected mode does not need it.

**Must not do:**

1. Auto-install Homebrew or Docker (these are big footguns).
2. Auto-edit `~/.zshenv`, `~/.bashrc`, or `~/.zshrc`.
3. Auto-mint tokens (the user goes to the vendor's UI).
4. Skip the platform check (`uname` first; refuse on Windows).
5. Modify a meta-info file the user has already edited without confirming the diff.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Modifying `~/.zshenv` automatically.
- Trying to install Docker for the user (start it for them is also out of scope).
- Re-installing tools that are already present.
- Skipping `gh auth login` check.
- Asking 10 questions in a row instead of one at a time.

## Output

A summary report to stdout. Under `--auto`, also written to `.temp/setup-report.md` for record:

```
[adk:setup] platform=darwin
- brew         present (4.5.2)
- gh           present (2.62.0) authed=ok
- jq           present (1.7.1)
- fd           present (10.2.0)
- ripgrep      present (14.1.1)
- fzf          present (0.55.0)
- node         present (v22.7.0)
- docker       present (27.3.1)

meta-info ~/.config/adk/:
- info.md         present, valid
- repos.md        present, 3 repos defined
- github.md       present, valid
- datadog.md      present, valid (3 service aliases)
- mixpanel.md     MISSING — run /adk-core:setup --target mixpanel
- statsig.md      present, valid
- snowflake.md    present, valid
- slack.md        present, valid
- review.md       present, valid
- docs.md         MISSING — run /adk-core:setup --target docs

env vars (referenced by .mcp.json):
- GITHUB_PAT              present
- DATADOG_API_KEY         present
- DATADOG_APP_KEY         MISSING — add to ~/.zshenv: export DATADOG_APP_KEY="..."
- STATSIG_CONSOLE_API_KEY present

doctor: 2 warnings, 0 errors
  - mixpanel.md missing — run /adk-core:setup --target mixpanel
  - DATADOG_APP_KEY missing in shell env (datadog MCP disabled; legacy DD_APP_KEY also accepted)
```

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | The setup persona |
| `references/workflow.md` | Detailed install + check order |
| `references/clarifying-questions.md` | Per-tool / per-topic confirmations |
| `references/output-format.md` | Report shape |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | First-run + repeat-run examples |
| `references/tool-list.md` | Source-of-truth list of required CLI tools |
| `references/modes.md` | auto + fix |
| `references/interaction-contract.md` | Canonical interaction contract |
| `templates/<topic>.md` | Starter ~/.config/adk/*.md files for every topic (10 files) |
