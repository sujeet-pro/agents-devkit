---
title: 'setup'
description: 'Bootstrap the local environment so every other adk skill works.'
artifact_kind: skill
skill_name: setup
category: standalone
---
# setup

Bootstrap the local environment so every other adk skill works. Verifies & installs missing dependencies (Homebrew, gh, jq, fd, ripgrep, fzf, claude CLI, node 18+), checks env vars in `~/.zshenv`, and runs `bin/adk-mcp-install` to wire MCP servers from `.mcp.json`. Use the first time you install adk on a machine, after a major OS upgrade, when adding a new MCP integration, or when `bin/adk-doctor` reports something missing. macOS only.

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-setup` form via `agents-skills/`.

```text
/adk:setup            # interactive run (Claude Code)
/adk:setup --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-setup` (resolved through the
`agents-skills/adk-setup/` symlink).

## Source

Direct from `skills/setup/SKILL.md` — this page is auto-generated.

Idempotent. Safe to re-run. Does nothing if everything is already in place.

## When to use

- First-time install of adk on a machine.
- After a major macOS upgrade.
- After adding a new MCP integration to `.mcp.json`.
- When `bin/adk-doctor` flags a missing dependency.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `--mode auto \| fix` | optional | `auto` = ask before installing; `fix` = install missing without asking |
| `--auto` | optional | Skip approval gates entirely |
| `--target <subset>` | optional | Comma-separated subset: `cli`, `mcp`, `env`, `all` (default) |

## Workflow

1. **Detect platform.** Hard-fail if not macOS. Ask user to install manually on Linux/Windows (we do not support those).
2. **Check Homebrew.** If missing, prompt to install via `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
3. **Check core CLI tools** (each via `command -v`):
   - `gh` (GitHub CLI) — `brew install gh`
   - `jq` — `brew install jq`
   - `fd` — `brew install fd`
   - `ripgrep` — `brew install ripgrep`
   - `fzf` — `brew install fzf`
   - `claude` (Claude Code) — `brew install --cask claude-code` (or surface install URL if cask missing)
   - `node` ≥ 18 — `brew install node` if missing
4. **Check `gh auth status`.** If not authed, prompt user to run `gh auth login`.
5. **Check env vars.** Source `~/.zshenv` (read-only) and verify presence of every `${VAR}` referenced in `.mcp.json`. Print a report: present / missing. For missing, show the export line the user would add (do NOT modify their `.zshenv` automatically — that file may be sensitive).
6. **MCP install.** Hand off to `bin/adk-mcp-install` (or `@adk:` is the same code path). Interactive picker: which servers to enable. Runs `claude mcp add ...` per choice.
7. **Validate.** Run `bin/adk-doctor`. Show its report.

## Mode contract

- `--mode auto` (default): each install step is gated by approval. Good for first run.
- `--mode fix --auto`: install everything missing without asking. Good for CI / repeatable provisioning.

## Output

Single report at end:

```
[adk:setup] platform=darwin
- brew         present (4.5.2)
- gh           present (2.62.0) authed=ok
- jq           present (1.7.1)
- fd           present (10.2.0)
- ripgrep      present (14.1.1)
- fzf          present (0.55.0)
- claude       present (1.2.0)
- node         present (v22.7.0)

env vars (.zshenv):
- GITHUB_PAT                 present
- ATLASSIAN_API_TOKEN        MISSING — add: export ATLASSIAN_API_TOKEN="..."
- DD_API_KEY                 present
- DD_APP_KEY                 MISSING — add: export DD_APP_KEY="..."
- ...

mcp servers (claude mcp ls):
- github            installed
- jira              skipped (env missing)
- datadog           installed
- ...

doctor: 2 warnings, 0 errors
  - ATLASSIAN_API_TOKEN missing in ~/.zshenv (jira/confluence MCP disabled)
  - DD_APP_KEY missing in ~/.zshenv (datadog MCP disabled)
```

## Anti-patterns

See `references/anti-patterns.md`. Headlines:

- Modifying `~/.zshenv` automatically.
- Running on Linux/Windows.
- Re-installing tools that are already present.
- Skipping `gh auth login` check.

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Mermaid: detect → install → MCP → validate |
| `references/modes.md` | auto + fix |
| `references/persona.md` | The setup agent |
| `references/workflow.md` | Detailed install order |
| `references/clarifying-questions.md` | Per-tool install confirmations |
| `references/output-format.md` | Report shape |
| `references/artifact-format.md` | Where the report goes |
| `references/validator.md` | Post-setup health check |
| `references/anti-patterns.md` | What NOT to do |
| `references/tool-list.md` | Source-of-truth list of tools to install |
| `references/examples.md` | First-run + repeat-run examples |
| `references/interaction-contract.md` | Synced from canonical |


## Related skills

- [`auto`](./skill-auto.md) — `@adk:auto` (a.k.a. `adk-auto`)
