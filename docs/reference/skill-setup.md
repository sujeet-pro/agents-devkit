---
title: 'setup'
description: 'Use when setting up, validating, or updating CLI tools and MCP server configurations for DevKit skills'
skill_name: setup
category: task
workflow_tier: abbreviated
user_invocable: true
---

# setup

Use `setup` when setting up, validating, or updating CLI tools and MCP server configurations for DevKit skills. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`setup` belongs to the `task` layer and is declared at the `abbreviated` tier with the `quick-action` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter       | Values                                                                                   | Default       | Description                                                     |
| --------------- | ---------------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------- |
| `--type`        | `tools`, `mcps`, `hooks`, `config`, `all`                                                | `all`         | Which category to set up                                        |
| `--check-only`  | flag                                                                                     | off           | Report status without making changes                            |
| `--tool`        | `git`, `python3`, `node`, `npm`, `jq`, `curl`, `dot`, `uvx`, `docker`, `gh`, `diagramkit`, `pagesmith` | (all tools)   | Only process a specific CLI tool (implies `--type tools`)       |
| `--server`      | `github`, `bitbucket`, `confluence`, `google-drive`                                      | (all servers) | Only process a specific MCP server (implies `--type mcps`)      |
| `--ide`         | `claude`, `cursor`, `windsurf`, `codex`, `all`                                           | (auto-detect) | Target AI tool for MCP config (implies `--type mcps`)           |
| `--skip-update` | flag                                                                                     | off           | Install/configure missing items but do not update existing ones |
| `--verbosity`   | `short`, `standard`, `detailed`                                                          | `standard`    | Output detail level                                             |

### Parameter Notes

- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.


| Skill                | Load When | Inline Fallback                                                             |
| -------------------- | --------- | --------------------------------------------------------------------------- |
| `/adk:workflow --family quick-action` | always | Quick Action workflow: confirm → execute → verify. For narrow tasks with single execution path. `--auto` skips confirmations. |
| `/adk:communication` | always    | Lead with conclusion. Bullet points. No preamble. Concrete specifics.       |

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Execution

Determine the effective type:

- If `--tool` is present: type = `tools`
- If `--server` is present: type = `mcps`
- If `--type` is explicitly set: use that value
- Otherwise: type = `all`

### Tools Setup

When type is `tools` or `all`, run the tools setup script:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/setup-tools.sh <args>
```

Where `<args>` are the relevant arguments (e.g. `--check-only`, `--tool node`, `--skip-update`).

Load stage details: `stages/tools.md`.

### MCP Setup

When type is `mcps` or `all`, run the MCP setup script:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/setup-mcps.sh <args>
```

Where `<args>` are the relevant arguments (e.g. `--check-only`, `--server github`, `--ide cursor`).

If the script exits with code 2 and outputs `PROMPT_USER:` lines, ask the user which IDE to target and re-run with `--ide <chosen>`.

Load stage details: `stages/mcps.md`.

### Hooks Setup

When type is `hooks` or `all`:

1. Read `~/.claude/settings.json`
2. Check if a SessionStart hook exists that reminds about ADK on compaction
3. If missing, add it:
  - Hook type: `SessionStart`
  - Purpose: remind the agent about ADK skill availability after context compaction
  - The hook should include a brief reminder of the `/adk:use` entry point and available skills

### Config Setup

When type is `config` or `all`:

1. Read the project or user `settings.json`
2. Set `/adk:use` as the default agent for general prompts
3. Validate the configuration is syntactically correct

### What Gets Configured

### `~/.claude/settings.json`

- **SessionStart hook**: adds a hook that reminds about ADK on compaction, ensuring the agent retains awareness of available skills across long sessions
- **Default agent**: sets `/adk:use` as the default routing entry point

### MCP Servers

Config is written to the correct user-level path per tool:

| Tool | Config path |
| ---- | ----------- |
| Claude Code | `~/.claude.json` → `mcpServers` |
| Cursor | `~/.cursor/mcp.json` → `mcpServers` |
| Windsurf | `~/.windsurf/mcp.json` → `mcpServers` |
| Codex | `~/.codex/mcp.json` → `mcpServers` |

Use `--ide all` to configure every detected tool at once.

| Server       | Config Key             | Transport | Env vars from `~/.zshenv`                                       |
| ------------ | ---------------------- | --------- | --------------------------------------------------------------- |
| GitHub       | `github`               | stdio     | `GITHUB_PAT` (mapped to `GITHUB_PERSONAL_ACCESS_TOKEN` for Docker) |
| Bitbucket    | `bitbucket`            | stdio     | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN`                         |
| Confluence   | `atlassian-confluence` | stdio     | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Atlassian    | `atlassian`            | HTTP      | — none — (OAuth, browser-based)                                 |
| Google Drive | `google-drive`         | stdio     | `GOOGLE_DRIVE_OAUTH_CREDENTIALS`                                |


All stdio servers use `zsh -c` to auto-source `~/.zshenv` and resolve env vars at startup. Atlassian HTTP MCP uses OAuth (covers Jira, Confluence, and Bitbucket via browser login). Google Drive is optional and configured on request.

### CLI Tools


| Tool       | Command      | Install Method                 | Used By                                                                  |
| ---------- | ------------ | ------------------------------ | ------------------------------------------------------------------------ |
| git        | `git`        | `brew install git`             | Nearly all skills                                                        |
| Python 3   | `python3`    | `brew install python`          | preflight.py, scripts                                                    |
| Node.js    | `node`       | `brew install node`            | Diagram skills, audit-dependency                                         |
| npm        | `npm`        | Bundled with node              | Same as Node.js                                                          |
| jq         | `jq`         | `brew install jq`              | Bitbucket, Confluence, Jira connectors                                   |
| curl       | `curl`       | `brew install curl`            | Bitbucket, Confluence, Jira connectors (pre-installed on macOS)          |
| Graphviz   | `dot`        | `brew install graphviz`        | `/adk:diagram-graphviz`                                                  |
| uv / uvx   | `uvx`        | `curl` installer               | Confluence MCP                                                           |
| Docker     | `docker`     | `brew install --cask docker`   | GitHub MCP (Docker variant)                                              |
| GitHub CLI | `gh`         | `brew install gh`              | PR management (run `gh auth login` after install)                        |
| diagramkit | `diagramkit` | `npm install -g diagramkit`    | `/adk:diagram-mermaid`, `/adk:diagram-excalidraw`, `/adk:diagram-drawio` |
| pagesmith  | `pagesmith`  | `npm install -g @pagesmith/docs` | `/adk:docs-crud`, `/adk:docs-repo`                                       |


Validation: confirm git, node, npm are installed and on PATH. Install diagramkit and pagesmith globally if not present.

### Plugin Validation

- Verify `.claude-plugin/plugin.json` exists and is valid JSON
- Check that the plugin declares the expected skills and entry points
- Report any missing or malformed entries

### Usage

```
/adk:setup                                  # Full setup: install + configure + update all
/adk:setup --type tools                     # Tools only: install + update CLI tools
/adk:setup --type mcps                      # MCPs only: configure + update + sync all servers
/adk:setup --type hooks                     # Hooks only: configure SessionStart hook
/adk:setup --type config                    # Config only: set default agent routing
/adk:setup --check-only                     # Report status without making changes
/adk:setup --tool git                       # Only process git
/adk:setup --server github                  # Only process GitHub MCP
/adk:setup --skip-update                    # Install/configure missing but don't update existing
```

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **Full setup** (default): installs missing tools, configures MCP servers, sets up hooks and config, updates everything
- `**--type tools`**: only processes CLI tools, skips MCP servers, hooks, and config
- `**--type mcps**`: only processes MCP servers, skips CLI tools, hooks, and config
- `**--type hooks**`: only processes SessionStart hooks and compaction reminders
- `**--type config**`: only processes user-level settings (default agent, routing)
- `**--check-only**`: reports status without modifications
- `**--tool <name>**`: only processes the specified tool, skips all others
- `**--server <name>**`: only processes the specified MCP server, skips all others
- `**--skip-update**`: installs/configures missing items but leaves existing ones at current version
- `**--verbosity short**`: status table only (installed/missing per item)
- `**--verbosity detailed**`: full config details, token sync results, version info, and package versions

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

All output is markdown by default. Structure varies by deliverable type -- see the skill-specific execution sections above for the exact format.

## Related Skills

### Adjacent Skills

- `/adk:use` — the orchestrator that routes general prompts to the right skill
- `/adk:project` — for initializing new projects and managing milestones

## Additional Reference

### Post-Setup Validation

After the scripts complete, report the results to the user:

- **Tools**: If Homebrew is not installed, provide installation instructions. List any tools that could not be installed.
- **MCPs**: If any servers were skipped due to missing env vars, list what needs to be added to `~/.zshenv`.
- **Hooks**: Report whether the SessionStart hook was added or already existed.
- **Config**: Report whether `/adk:use` was set as default or was already configured.

If the user asks to validate a specific skill's MCP dependencies, run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py <skill-dir>
```

### Prerequisites

- **macOS**: Homebrew must be installed for tool installations (the script checks and provides install instructions if missing)
- All brew installations require an internet connection
- MCP server configuration requires tokens in `~/.zshenv`

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:setup
/adk:setup                                  # Full setup: tools + MCPs + hooks + config
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:setup --type tools                     # Only set up CLI tools
/adk:setup --type mcps                      # Only set up MCP servers
/adk:setup --type hooks                     # Only set up SessionStart hooks
/adk:setup --type config                    # Only configure default agent routing
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:setup --check-only                     # Report status without changes
/adk:setup --tool node --verbosity detailed # Only process node with full details
/adk:setup --skip-update                    # Install missing but don't update
/adk:setup --type tools --check-only        # Check tool status only
```
