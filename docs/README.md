---
title: Agent Development Kit
description: A Claude Code plugin shipping 50+ self-contained, highly-interactive skills covering the full developer loop — also installable via npm, repo clone, or npx skills for Cursor, Codex, Gemini, and other harnesses.
layout: home
tagline: Principal-engineer-grade skills for software development agents.
install: 
  claude --plugin marketplace add sujeet-pro/agents-devkit
  && /plugin install adk@sujeet-pro-adk
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
  - title: Claude-native, harness-friendly
    details: 'This repo IS the adk Claude Code plugin (.claude-plugin/plugin.json). A parallel agents-skills/ symlink farm exposes the same skills as adk-<name> for Cursor, Codex, Gemini, Antigravity, and the npx skills loader.'
  - title: Highly interactive by default
    details: 'Every skill brainstorms with the user, surfaces 2-3 explained options, and asks one question at a time. Pass --auto for unattended runs. Many skills also support --mode review | fix.'
  - title: One setup command, every harness
    details: 'After install, run the setup skill (or npx adk). It installs CLI deps via Homebrew, registers MCP servers from .mcp.json against ~/.zshenv, and writes a managed block into the user-level memory file of every detected harness so each one auto-discovers ADK.'
---

## Install

The same plugin reaches every major coding agent. Pick the path that matches how you work — they install the same skills, just through different harnesses.

> [!TIP]
> Whichever path you pick, finish with **`/adk:setup`** (Claude) or **`npx adk`** (everywhere else) to install CLI deps, register MCP servers, and wire user memory.

### 1. Claude Code plugin — primary path

This repo IS the `adk` Claude Code plugin. The Claude plugin host loads every skill, subagent, hook, and MCP server in one shot — no external installer needed.

```sh
# In Claude Code:
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@sujeet-pro-adk
/reload-plugins
```

Then run the setup skill once to register MCP servers and wire your user-level `CLAUDE.md`:

```sh
/adk:setup            # interactive — walks you through each step
/adk:setup --auto     # unattended; safe defaults
```

Local development against a clone:

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
claude --plugin-dir ./agents-devkit
```

What `/adk:setup` does:

1. Verifies `gh`, `jq`, `fd`, `ripgrep`, `fzf`, `claude`, `node` (`brew install …` if missing).
2. Reads `.mcp.json`, resolves `${ENV_VAR}` placeholders from `~/.zshenv`, and runs `claude mcp add …` for each accepted server.
3. Writes a managed `<!-- adk:start --> ... <!-- adk:end -->` block into `~/.claude/CLAUDE.md` (and the AGENTS.md / GEMINI.md of every other harness it detects) so every agent on this machine auto-discovers ADK.
4. Runs `bin/adk-doctor` and surfaces the report.

### 2. npm module — works for every harness

Useful when you want a pinned version, are not on Claude Code yet, or want to drive setup from a non-Claude harness. Installs the same code via npm and gives you the `adk-*` CLIs.

```bash
# One-shot, no install
npx --yes agents-devkit adk           # runs the setup skill end-to-end

# Project-pinned (CI-friendly)
npm install --save-dev agents-devkit
npx adk

# Global
npm install -g agents-devkit
adk
```

`adk` (alias for `adk-setup`) auto-detects which agents are present — Claude Code, Claude Desktop, Cursor, Codex CLI, Gemini CLI, Antigravity — and:

- symlinks every `agents-skills/adk-<name>` folder into the right per-agent skill directory (Cursor / Codex / Gemini / Antigravity);
- registers MCP servers via `claude mcp add` (when Claude is present);
- updates the user-level memory file for each detected harness.

Per-step CLIs are also exposed:

```bash
npx adk-install                # symlink skill folders into detected harnesses
npx adk-mcp-install            # register MCP servers from .mcp.json
npx adk-update-memory          # write the managed block into ~/.claude/CLAUDE.md etc.
npx adk-doctor                 # health check
npx adk-validate               # structural + content validator
```

### 3. Clone + symlink — for contributors

When you want every edit live (no `npm install` step) and full git access to skills/agents/hooks/MCP:

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
npm install
node bin/adk-setup            # same as `/adk:setup`
```

Symlinks point back at the clone, so `git pull` instantly refreshes every linked harness and local skill edits show up live in Claude / Cursor / Codex.

Per-target install (skip auto-detection):

```bash
node bin/adk-install --target cursor                  # only Cursor
node bin/adk-install --target cursor,codex            # Cursor + Codex
node bin/adk-install --mode project                   # link into <cwd>/.cursor/skills/ (project-local)
node bin/adk-install --dry-run                        # preview, no writes
node bin/adk-update-memory --target claude            # only update ~/.claude/CLAUDE.md
node bin/adk-update-memory --remove                   # remove the managed block from every harness
```

### 4. `npx skills add` — skills only

The third-party [`skills`](https://skills.sh) loader picks up the `agents-skills/adk-<name>` folders. **Subagents, hooks, MCP servers, monitors, and the user-memory wiring are NOT installed via this path** — use one of the paths above for the full kit.

```bash
npx skills add sujeet-pro/agents-devkit                    # all skills, all detected agents
npx skills add sujeet-pro/agents-devkit -a claude-code     # one harness
npx skills add sujeet-pro/agents-devkit -s adk-plan-brainstorm -s adk-review-pr   # specific skills
```

## What you get

- **59 self-contained skills** — top router (`adk`), 8 category routers, 50 task skills covering planning, building, reviewing, documenting, auditing, publishing, observability, and frontend work. Full catalog at [`skills-manifest.json`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills-manifest.json).
- **10 Claude Code subagents** — `dispatcher`, `implementer`, `code-reviewer`, `debugger`, `doc-writer`, `plan-reviewer`, `research-agent`, `security-reviewer`, `test-engineer`, `brainstorm-facilitator`. See [Agents](./reference/agents/README.md).
- **Plugin hooks** — `PreToolUse:Bash` (block destructive git/rm), `PostToolUse:Edit|Write` (validate SKILL.md frontmatter), `Stop` (validator gate), `SessionStart` (announce plugin loaded). See [hooks](./reference/config/hooks.md).
- **13 pre-wired MCP servers** — GitHub, Bitbucket, Jira, Confluence, Google Drive, Gmail, Slack, Datadog, Mixpanel, Chrome DevTools, Cursor IDE Browser, Playwright, Brainstorming. Env vars resolved from `~/.zshenv`. See [MCP](./reference/config/README.md).
- **6 CLI scripts** under `bin/` — `adk-setup`, `adk-install`, `adk-mcp-install`, `adk-update-memory`, `adk-doctor`, `adk-validate`, `adk-sync-contracts`. See [bin](./reference/config/README.md).
- **One CI/CD monitor** — `ci-status` watches `gh pr checks` for the active PR and feeds `cicd-monitor` / `cicd-fix`. See [monitor-ci-status](./reference/config/monitor-ci-status.md).

## New here? Read in this order

1. **[Installation](./guide/getting-started/installation.md)** — pick a path, run setup, verify with `adk-doctor`.
2. **[First skill](./guide/getting-started/first-skill.md)** — run `/adk:auto` (or `adk-auto`) on a real task.
3. **[Philosophy](./concepts/philosophy.md)** — the principles every skill follows.
4. **[Skill anatomy](./concepts/skill-anatomy.md)** — what one skill looks like and how its references work.
5. **[Memory files](./concepts/memory-files.md)** — how `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` compose.
6. **[Reference](./reference/skills/README.md)** — one auto-generated page per skill, agent, hook, MCP server, and CLI script.

## Repo maintenance

If you are contributing to ADK itself, read [`AGENTS.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/AGENTS.md) before any non-trivial change. Validate with `npm run validate`. Regenerate the manifest with `npm run skills:manifest`. Refresh the docs with `/adk:prj-update-docs`.
