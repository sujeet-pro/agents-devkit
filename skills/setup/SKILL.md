---
name: setup
description: |
  Bootstrap the local environment so every other adk skill works. Verifies & installs missing dependencies (Homebrew, gh, jq, fd, ripgrep, fzf, node 18+, Docker for the containerized MCP servers), checks `gh auth status`, and reports which `${ENV_VAR}` placeholders referenced in `.mcp.json` are missing from your shell environment so you can add the exports to `~/.zshenv`. Use the first time you install adk on a machine, after a major OS upgrade, or when adding a new MCP integration. macOS only. The Claude Code plugin host loads skills, agents, hooks, MCP servers, and monitors automatically — this skill only handles the *external* dependencies (CLI tools and shell env).
metadata:
  category: meta
  kind: task
  modes: [auto, fix]
  layer: 0
  needs_mcp: []
---

# setup — env + tools health check

Idempotent. Safe to re-run. Does nothing if everything is already in place.

> [!NOTE]
> ADK installs as a Claude Code plugin. The plugin host loads every skill, subagent, hook, MCP entry, and monitor automatically as soon as you run `/plugin install adk@sujeet-pro-adk` and `/reload-plugins`. There is no separate symlink-installer step. This skill only checks the *external* dependencies (CLI tools, Docker, shell env vars) those components rely on.

## When to use

- First-time install of adk on a machine.
- After a major macOS upgrade.
- After adding a new MCP integration to `.mcp.json`.
- When a skill complains that a CLI dep or env var is missing.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `--mode auto \| fix` | optional | `auto` = ask before installing; `fix` = install missing without asking |
| `--auto` | optional | Skip approval gates entirely |
| `--target <subset>` | optional | Comma-separated subset: `cli`, `env`, `mcp`, `all` (default) |

## Workflow

1. **Detect platform.** Hard-fail if not macOS. Ask the user to install dependencies manually on Linux/Windows (this skill does not support those — but the plugin itself works wherever Claude Code runs).
2. **Check Homebrew.** If missing, prompt to install via `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
3. **Check core CLI tools** (each via `command -v`):
   - `gh` (GitHub CLI) — `brew install gh`
   - `jq` — `brew install jq`
   - `fd` — `brew install fd`
   - `ripgrep` — `brew install ripgrep`
   - `fzf` — `brew install fzf`
   - `node` ≥ 18 — `brew install node` (only required for the docs-site build)
   - `docker` — `brew install --cask docker` (only required for the containerized MCP servers: `github`, `bitbucket`, `jira`, `confluence`)
4. **Check `gh auth status`.** If not authed, prompt the user to run `gh auth login`.
5. **Check env vars.** Read the user's shell env and verify presence of every `${VAR}` referenced in `.mcp.json`. Print a report: present / missing. For missing, show the export line the user would add (do NOT modify their `~/.zshenv` automatically — that file may be sensitive).
6. **MCP server inventory.** Read `.mcp.json` and report which servers will work given the current env. Servers whose env vars are missing simply fail to start; the dependent ADK skills fall back to documented CLI alternatives where available.
7. **Validate.** Re-summarize and emit the final report.

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
- node         present (v22.7.0)
- docker       present (27.3.1)

env vars (referenced by .mcp.json):
- GITHUB_PAT                 present
- ATLASSIAN_API_TOKEN        MISSING — add: export ATLASSIAN_API_TOKEN="..."
- DD_API_KEY                 present
- DD_APP_KEY                 MISSING — add: export DD_APP_KEY="..."
- ...

mcp servers (resolved from .mcp.json):
- github            ready
- jira              missing-env (ATLASSIAN_API_TOKEN)
- datadog           missing-env (DD_APP_KEY)
- chrome-devtools   ready
- ...

doctor: 2 warnings, 0 errors
  - ATLASSIAN_API_TOKEN missing in ~/.zshenv (jira/confluence MCP disabled)
  - DD_APP_KEY missing in ~/.zshenv (datadog MCP disabled)
```

## Anti-patterns

See `references/anti-patterns.md`. Headlines:

- Modifying `~/.zshenv` automatically.
- Trying to write to `~/.claude/CLAUDE.md` or any user-level memory file (the Claude plugin host wires that up — leave it alone).
- Running on Linux/Windows (this skill is macOS-only; the plugin itself is cross-platform).
- Re-installing tools that are already present.
- Skipping the `gh auth login` check.

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Mermaid: detect → install → env-check → report |
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
