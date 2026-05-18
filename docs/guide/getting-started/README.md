---
title: Getting Started
description: Clone the repo, run install.sh, scaffold overrides.yaml, verify. Five minutes to first skill invocation.
order: 1
---

# Getting Started

Five minutes from clone to first skill invocation.

## Fast path

```bash
# 1. Clone the repo
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit

# 2. Install for your agent(s)
./install.sh                   # autodetect everything installed
# OR explicit:
./install.sh --target claude

# 3. Set env vars in ~/.zshenv (see SETUP.md §2)
export GITHUB_PAT="github_pat_..."
export DATADOG_API_KEY="..."
export DATADOG_APP_KEY="..."
export STATSIG_CONSOLE_API_KEY="console-..."
export ATLASSIAN_SITE="acme.atlassian.net"
export ATLASSIAN_USERNAME="you@acme.com"
export ATLASSIAN_API_TOKEN="ATATT..."

# 4. Restart your agent (Claude Code etc.) so env vars + MCPs load
```

Then in your agent:

```text
/adk-setup --init                 # scaffold ~/.config/adk/overrides.yaml
/adk-setup --check                # verify env, MCPs, agents
/adk-setup --enrich               # auto-populate metadata cache from MCPs
```

## What just happened

`install.sh` did the following for each detected agent:

| Agent | What landed |
|---|---|
| Claude Code | symlinks for 8 skills + 9 subagents + 8 slash commands; MCP merge into `~/.claude/settings.json`; 3 hooks (PreToolUse/PostToolUse/SessionStart); CLAUDE.md pointer to `AGENTS.md` |
| Cursor | 8 rule files in `~/.cursor/rules/`; MCP merge into `~/.cursor/mcp.json`; global "always" rule pointing at `AGENTS.md` |
| Codex CLI | 8 prompts in `~/.codex/prompts/`; MCP config in `~/.codex/config.toml`; instructions pointer to `AGENTS.md` |
| Junie | `~/.junie/guidelines.md` append with `AGENTS.md` pointer; honest gap doc — Junie's skill auto-routing isn't full yet |

All installs are idempotent — re-running `install.sh` updates symlinks and merge blocks without duplicating. Uninstall via `./install.sh --uninstall --target <agent>`.

## Try a skill

```text
# Polymorphic on input — works with a Jira URL, GH issue URL, Slack thread, freeform description
/adk-implement <Jira URL or KEY-NUM>

# Polymorphic on target — PR URL, local working tree, doc path, comment thread
/adk-review <PR URL>

# Read-only multi-source investigator
/adk-investigate "checkout 500s since 13:00"

# Generate any markdown artifact (runbook / ADR / RCA / PR body / commit msg / diagram / ...)
/adk-document <intent> --type runbook

# Push markdown to Confluence / Jira / GDoc / Slack
/adk-sync --write .temp/foo.md --to confluence --target "My Page"
```

Every skill starts with up to 3 questions about scope, constraints, and (when relevant) scale verification. Your answers are training data for `/adk-improve`.

## Next

- [Installation](./installation.md) — detailed clone + install paths
- [Multi-agent setup](../usage/multi-agent.md) — per-agent capability matrix
- [overrides.yaml](../usage/overrides-yaml.md) — the single config file you maintain
- [Philosophy](../philosophy.md) — why adk works this way
