---
title: Agent Development Kit
description: A Claude Code plugin shipping 69 self-contained, highly-interactive skills covering the full developer loop — planning, building, reviewing, documenting, auditing, publishing, observability, frontend work, plus version-pinned diagram (Mermaid / Graphviz / Excalidraw / Drawio) and Pagesmith-flavored markdown skills.
layout: home
tagline: Principal-engineer-grade skills for software development agents.
install:
  language: sh
  title: Claude Code
  code: |
    /plugin marketplace add sujeet-pro/agents-devkit
    /plugin install adk@sujeet-pro-adk
    /adk:setup
actions:
  - text: Install
    link: /guide/getting-started/installation/
    theme: brand
  - text: First skill
    link: /guide/getting-started/first-skill/
    theme: alt
features:
  - title: Self-contained skills
    details: 'Every skill is one folder: SKILL.md plus a flat references/ shipping its own persona, workflow, output format, and constitution. No _shared/, no auto-propagation, no cross-skill references. The validator (bin/adk-validate) enforces it.'
  - title: Claude-native plugin
    details: 'This repo IS the adk Claude Code plugin (.claude-plugin/plugin.json). The Claude plugin host loads every skill, subagent, hook, and MCP server in one shot — no external installer step. Distributed via the marketplace for the GitHub source, and via npm for semver-pinned installs.'
  - title: Highly interactive by default
    details: 'Every skill brainstorms with the user, surfaces 2-3 explained options, and asks one question at a time. Pass --auto for unattended runs. Many skills also support --mode review | fix.'
  - title: One setup command
    details: 'After install, run /adk:setup. It verifies CLI deps (Homebrew packages, gh, jq, fd, ripgrep, fzf, node 18+, Docker for the containerized MCP servers), checks gh auth status, and reports which ${ENV_VAR} placeholders referenced in .mcp.json are missing from your shell environment.'
  - title: Version-pinned diagrams
    details: 'Five engine-specific diagram skills (mermaid / graphviz / excalidraw / drawio / review) shell out to a locally-installed diagramkit (npx diagramkit ...) and enforce WCAG 2.2 AA contrast plus ASPECT_RATIO_EXTREME / CONTAINS_FOREIGN_OBJECT guards via diagramkit validate.'
  - title: Pagesmith-grade markdown
    details: 'A self-contained markdown skill pinned to @pagesmith/core@0.9.9 — full feature surface (GFM, alerts, math, code tabs, themed light/dark image pairs, Shiki dual themes, language aliases) plus a validate-markdown.sh that auto-installs @pagesmith/core globally and runs pagesmith-core validate against your content.'
---

## Install

ADK is a single Claude Code plugin loaded via `.claude-plugin/plugin.json`. The Claude plugin host loads every skill, subagent, hook, and MCP server in one shot — there is no separate installer step. Distribution goes through the marketplace at `.claude-plugin/marketplace.json`, which exposes two plugin sources:

| Source            | Marketplace plugin id | Tracks                                                |
| ----------------- | --------------------- | ----------------------------------------------------- |
| `github`          | `adk`                 | `main` of [`sujeet-pro/agents-devkit`](https://github.com/sujeet-pro/agents-devkit) |
| `npm`             | `adk-npm`             | The `agents-devkit` package on npm (semver-pinned)   |

> [!TIP]
> Whichever source you pick, finish with **`/adk:setup`** to verify CLI dependencies and surface any missing MCP env vars.

### 1. Claude Code plugin (recommended)

```sh
# In Claude Code:
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@sujeet-pro-adk
/reload-plugins
```

Then run the setup skill once to verify external deps and your MCP env:

```sh
/adk:setup            # interactive — walks you through each step
/adk:setup --auto     # unattended; safe defaults
```

### 2. Local clone (for contributors)

When you want every edit live and full git access to skills/agents/hooks/MCP:

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
claude --plugin-dir "$(pwd)"
```

Inside Claude:

```text
/adk:auto                  # prompt-routing dispatcher (recommended starting point)
/adk:plan-brainstorm       # any specific skill, by name
/reload-plugins            # after editing a SKILL.md, agent, hook, or MCP entry
```

### 3. From npm (for semver-pinned installs)

```sh
# In Claude Code:
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk-npm@sujeet-pro-adk
```

The `agents-devkit` package on npm ships the same plugin layout (`.claude-plugin/`, `skills/`, `agents/`, `hooks/`, `monitors/`, `bin/`, `.mcp.json`, `settings.json`, `skills-manifest.json`).

> [!NOTE]
> ADK targets Claude Code and Claude Desktop only. There is no projection into Cursor, Codex, Gemini, or other harnesses, and there is no separate `AGENTS.md` / `GEMINI.md` — `CLAUDE.md` at the repo root is the single source of truth.

## What you get

- **69 self-contained skills** — top router (`adk`), 8 category routers (`plan`, `build`, `review`, `docs`, `audit`, `publish`, `frontend`, `visualize`), task skills, and standalone task skills (`auto`, `requirements`, `scoping`, `setup`, `markdown`, `temp-folder`, `mode-contract`, `adopt-ai-in-repo`, `personal-skill-create`). Full catalog at [`skills-manifest.json`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills-manifest.json).
- **10 Claude Code subagents** — `dispatcher`, `implementer`, `code-reviewer`, `debugger`, `doc-writer`, `plan-reviewer`, `research-agent`, `security-reviewer`, `test-engineer`, `brainstorm-facilitator`. See [Agents](./reference/agents/README.md).
- **Plugin hooks** — `PreToolUse:Bash` (block destructive git / rm), `PostToolUse:Edit|Write` (validate SKILL.md frontmatter), `Stop` (validator gate), `SessionStart` (cat the canonical system prompt). See [hooks](./reference/config/hooks.md).
- **13 pre-wired MCP servers** — GitHub, Bitbucket, Jira, Confluence, Google Drive, Gmail, Slack, Datadog, Mixpanel, Chrome DevTools, Cursor IDE Browser, Playwright, Brainstorming. `${ENV_VAR}` placeholders are resolved from your shell environment at session start. See [MCP](./reference/config/README.md).
- **2 maintainer CLI scripts** under `bin/` — [`adk-validate`](./reference/config/bin-adk-validate.md) (structural + content validator, regenerates `skills-manifest.json`) and [`adk-sync-contracts`](./reference/config/bin-adk-sync-contracts.md) (propagates `bin/canonical/interaction-contract.md` and `bin/canonical/system-prompt.md` into every skill's `references/`). Plus `bin/internal/manifest.mjs` and `bin/internal/generate-skill-docs.mjs` for the docs site.
- **One CI/CD monitor** — [`ci-status`](./reference/config/monitor-ci-status.md) watches `gh pr checks` for the active PR and feeds `cicd-monitor` / `cicd-fix`.

## New here? Read in this order

1. **[Installation](./guide/getting-started/installation.md)** — pick a path, run setup, verify the plugin is loaded.
2. **[First skill](./guide/getting-started/first-skill.md)** — run `/adk:auto` on a real task.
3. **[Philosophy](./concepts/philosophy.md)** — the principles every skill follows.
4. **[Skill anatomy](./concepts/skill-anatomy.md)** — what one skill looks like and how its references work.
5. **[Memory files](./concepts/memory-files.md)** — how `CLAUDE.md` composes with the plugin.
6. **[Reference](./reference/README.md)** — one auto-generated page per skill, agent, hook, MCP server, and CLI script.

## Repo maintenance

If you are contributing to ADK itself, read [`CLAUDE.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/CLAUDE.md) before any non-trivial change.

```bash
npm install                # only needed when building the docs site
npm run validate           # bin/adk-validate — structural + content checks; regenerates skills-manifest.json
npm run validate:sync      # bin/adk-sync-contracts --check
npm run sync-contracts     # bin/adk-sync-contracts (propagate canonical files)
npm run skills:manifest    # bin/internal/manifest.mjs (regenerates skills-manifest.json)
npm run docs:build         # build gh-pages/ from docs/
npm run docs:dev           # local pagesmith-docs dev server
```

To refresh this doc site after a source change, run `/prj-update-docs` from inside the repo.
