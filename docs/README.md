---
title: Agent Development Kit
description: Self-contained ADK skills, runtime-specific custom subagents, hooks, and MCP configs for Claude / Cursor / Codex / Gemini and other coding agents.
layout: home
tagline: One opinionated playbook. Installed into every major coding agent.
actions:
  - text: Concepts
    link: /concepts/
    theme: brand
  - text: Public Skills
    link: /reference/skills/
    theme: alt
features:
  - title: Self-Contained Skills
    details: "Every skill is one folder: SKILL.md plus a flat references/ that ships its own persona, workflow, output format, and constitution. No _shared/, no auto-propagation, no cross-skill references."
  - title: One Installer, Every Harness
    details: "The Node CLI lays down skills, hooks, custom subagents, and MCP configs into Claude Code, Claude Desktop, Cursor, Codex CLI / Desktop, Gemini CLI, Antigravity, and Junie. Re-runs are idempotent."
  - title: Define Once, Symlink Where Identical
    details: "A single .agents/skills/ hub holds every skill once. Each runtime's skills/ folder is a symlink farm into the hub. Custom subagents stay independent per provider since their formats and capabilities differ."
  - title: Env Vars Through ~/.zshenv
    details: "MCP env vars (GITHUB_PAT, BITBUCKET_APP_PASSWORD, etc.) are read from and written to ~/.zshenv. The CLI prompts only for what is missing and persists with confirmation."
---

## Install

Three install paths, ordered from most-recommended to most-minimal. Paths 1 and 2 use the bundled Node CLI (`adk-install`) and wire up all five surfaces (skills, custom subagents, hooks, MCP servers, global prompts). Path 3 uses the third-party [`skills`](https://skills.sh) loader and lands only the skills.

### 1. Clone + install script — suggested

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit && npm install
npm run setup            # interactive; same as `adk-install`
```

Symlinks point back at the clone, so `git pull` refreshes every linked runtime instantly and local skill edits show up live.

### 2. npm modules — pinned / CI-reproducible

```bash
# Global ($HOME)
npm install -g agents-devkit
adk-install

# Per-project (pinned in package.json, CI-friendly)
cd <your-project>
npm install --save-dev agents-devkit
npx adk-install
```

### 3. `npx skills add` — for non-tech folks (skills only)

```bash
npx skills add sujeet-pro/agents-devkit
```

Drops just the `SKILL.md` files into your agent via the third-party [`skills`](https://skills.sh) loader. **Custom subagents, hooks, MCP servers, and global prompts are NOT installed via this path** — use path 1 or 2 if you want the full kit.

User config: `~/.config/adk/settings.json5`. Project config: `<project>/.adk/settings.json5`.

## What you get

- **37 self-contained `adk-*` skills**: 1 top router (`adk`) + 8 category routers + 28 task skills covering planning, building, reviewing, documenting, auditing, publishing, visualization, and frontend work.
- **9 custom subagents per provider** for Claude, Cursor, and Codex (each authored independently for its runtime).
- **Per-runtime hook configs** for Claude, Cursor, and Codex.
- **Pre-wired MCP server configs** for GitHub, Bitbucket, Confluence, Jira, Google Drive, and a local `brainstorming` server. Env vars resolved from `~/.zshenv`.

## New here? Read in this order

1. **[Philosophy](./concepts/philosophy.md)** — the principles every skill follows.
2. **[Skill Anatomy](./concepts/skill-anatomy.md)** — what one skill looks like and how its references work.
3. **[Agent Personas](./concepts/agents.md)** — the per-provider custom subagents ADK ships.
4. **[Hooks](./concepts/hooks.md)** — the safety layer below `--auto`.
5. **[MCP Servers](./concepts/mcp.md)** — when skills prefer MCP and how they fall back.

## Public skill catalog (37)

**Routers:** `adk` · `adk-plan` · `adk-build` · `adk-review` · `adk-docs` · `adk-audit` · `adk-publish` · `adk-visualize` · `adk-frontend`

**Plan tasks:** `adk-plan-brainstorm` · `adk-plan-research` · `adk-plan-spec` · `adk-plan-design` · `adk-plan-roadmap`

**Build tasks:** `adk-build-feature` · `adk-build-refactor` · `adk-build-migrate` · `adk-build-test` · `adk-build-deps`

**Review tasks:** `adk-review-pr` · `adk-review-local` · `adk-review-feedback` · `adk-review-handoff`

**Docs tasks:** `adk-docs-write` · `adk-docs-review`

**Audit tasks:** `adk-audit-repo` · `adk-audit-site`

**Publish tasks:** `adk-publish-commit` · `adk-publish-github` · `adk-publish-bitbucket` · `adk-publish-confluence` · `adk-publish-gdrive`

**Visualize tasks:** `adk-visualize-diagram` · `adk-visualize-chart`

**Frontend tasks:** `adk-frontend-design` · `adk-frontend-feature` · `adk-frontend-react-csr`

See the [full reference](./reference/skills/) for each skill's contract and references list.

## Repo maintenance

If you are contributing to ADK itself, read [`AGENTS.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/AGENTS.md) before any non-trivial change. Validate with `npm run validate`. Regenerate the manifest with `npm run skills:manifest`.
