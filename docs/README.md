---
title: adk — agents-devkit
description: Single-repo, multi-agent skill kit. Eight polymorphic skills, nine MCPs, nine subagents, installed via install.sh into Claude Code / Cursor / Codex CLI / Junie at user level.
layout: home
tagline: Implement, review, investigate, document — composed with an advisor strategy and a self-improving decision-log loop.
install:
  lang: bash
  title: Clone + install (Claude Code shown)
  frame: terminal
  code: |
    git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
    cd ~/code/agents-devkit
    ./install.sh --target claude
    # then in Claude Code:
    # /adk-setup --init
actions:
  - text: Install
    link: /guide/getting-started/installation/
    theme: brand
  - text: Philosophy
    link: /guide/philosophy/
    theme: alt
features:
  - title: Eight polymorphic skills
    details: /adk-implement, /adk-review, /adk-investigate, /adk-document, /adk-sync, /adk-setup, /adk-improve, /adk-explain. Each routes internally based on input shape — a Jira URL dispatches the from-jira sub-flow, a PR URL dispatches review-pr, etc.
  - title: Multi-agent, one repo
    details: install.sh symlinks the right wrappers into Claude Code, Cursor, Codex CLI, and Junie at user level. No marketplace. Same content, native format per agent.
  - title: Question-first, every run
    details: Every skill goes through a mandatory ≤3-question phase before any execution. The Q&A is logged to ~/.config/adk/learning/decisions.jsonl as training data for the self-improvement loop.
  - title: Self-improving by design
    details: /adk-improve reads accumulated decision logs and proposes updates to ~/.config/adk/overrides.yaml. After each run the log rotates so improvements compound over time.
  - title: Plan/act tool enforcement
    details: --plan mode literally restricts the implementer to read-only tools; --act unlocks edits. Cline-style separation, not advisor-prose-only.
  - title: Deterministic hooks
    details: PreToolUse:Bash safety blocks force-push, hard-reset on protected branches, unrequested PR merges; PostToolUse:Edit validates SKILL.md frontmatter and refuses raw-token writes; SessionStart prints the status banner. Idempotently merged into ~/.claude/settings.json.
---

## Install

`adk` is distributed as a single repo. Clone it once, then run `./install.sh` for each agent you use:

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
./install.sh                       # autodetect installed agents
./install.sh --target claude       # one agent
./install.sh --target claude,cursor
./install.sh --target all          # try every supported agent
./install.sh --uninstall           # remove everything by marker; leaves your overrides
```

`install.sh` symlinks skills + agents + slash commands into the agent's config dir, merges MCP configs, and appends a pointer to `AGENTS.md` in the agent's global guidelines. `git pull` propagates updates instantly.

See the full [Installation](./guide/getting-started/installation.md) guide for per-agent details and the [SETUP.md](https://github.com/sujeet-pro/agents-devkit/blob/main/SETUP.md) for env-var requirements.

## What this site covers

`adk` is an opinionated skill kit for a single operator (Principal Engineer): code writing, code review, documentation, and production investigations. It composes scripts (deterministic), MCPs (data access), and an advisor wrapper around every skill so each run is plan → clarify → execute → validate → report.

The reference section is generated from the repository source. To refresh it after editing a skill, agent, MCP, or script, run:

```bash
npm run docs:reference
```

For local development:

```bash
npm install
npm run docs:dev
```

## New here? Read in this order

1. **[Philosophy](./guide/philosophy.md)** — operating principles behind every skill.
2. **[Installation](./guide/getting-started/installation.md)** — clone + install.sh + per-agent wiring.
3. **[Multi-agent setup](./guide/usage/multi-agent.md)** — Claude / Cursor / Codex / Junie capability matrix.
4. **[overrides.yaml](./guide/usage/overrides-yaml.md)** — the single source of user/company truth (workspaces, repos, data dictionary, defaults).
5. **[Concepts](./guide/concepts/)** — advisor strategy, question-first, decision logs, plan/act, edit-format, hooks.
6. **[Reference](./reference/)** — generated pages for every skill, agent, MCP, script, and shared file.
