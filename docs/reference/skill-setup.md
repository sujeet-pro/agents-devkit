---
title: "setup"
description: CLI tool installation, MCP server configuration, hooks, and DevKit settings validation
skill_name: setup
category: task
workflow_tier: abbreviated
user_invocable: true
---

# setup

Idempotently installs, validates, and updates CLI tools, MCP servers, hooks, and configuration used by DevKit skills. Handles four categories: CLI tools (via Homebrew), MCP server configuration (tokens from `~/.zshenv`), SessionStart hooks, and user-level settings. Uses abbreviated workflow (phases 2-3 skipped).

## When to Use

- Set up all DevKit dependencies from scratch (tools, MCPs, hooks, config)
- Install or update specific CLI tools (git, node, gh, diagramkit, pagesmith, etc.)
- Configure MCP servers (GitHub, Bitbucket, Confluence, Google Drive)
- Set up SessionStart hooks for compaction reminders
- Configure `/adk:use` as the default agent
- Check the status of installed tools and MCP servers without making changes
- Sync MCP server tokens after updating `~/.zshenv`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--type` | `tools`, `mcps`, `hooks`, `config`, `all` | `all` | Which category to set up |
| `--check-only` | flag | off | Report status without making changes |
| `--tool` | `git`, `python3`, `node`, `npm`, `jq`, `curl`, `dot`, `uvx`, `docker`, `gh`, `diagramkit`, `pagesmith` | all tools | Only process a specific CLI tool (implies `--type tools`) |
| `--server` | `github`, `bitbucket`, `confluence`, `google-drive` | all servers | Only process a specific MCP server (implies `--type mcps`) |
| `--skip-update` | flag | off | Install/configure missing items but do not update existing ones |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Full setup** (default) | Installs missing tools, configures MCP servers, sets up hooks and config, updates everything |
| `--type tools` | Only processes CLI tools, skips MCP servers, hooks, and config |
| `--type mcps` | Only processes MCP servers, skips CLI tools, hooks, and config |
| `--type hooks` | Only processes SessionStart hooks and compaction reminders |
| `--type config` | Only processes user-level settings (default agent, routing) |
| `--check-only` | Reports status without modifications |
| `--tool <name>` | Only processes the specified tool, skips all others (implies `--type tools`) |
| `--server <name>` | Only processes the specified MCP server, skips all others (implies `--type mcps`) |
| `--skip-update` | Installs/configures missing items but leaves existing ones at current version |
| `--verbosity short` | Status table only (installed/missing per item) |
| `--verbosity detailed` | Full config details, token sync results, version info, and package versions |

## Key Behaviors

- **Idempotent operations**: safe to run repeatedly — installs only what's missing, updates only what's outdated
- **Auto-detection of type**: `--tool` implies `--type tools`, `--server` implies `--type mcps`
- **Token sync**: compares `~/.zshenv` values against MCP server config and updates if they differ
- **SessionStart hook management**: adds a hook that reminds about ADK on compaction, ensuring skill awareness across long sessions
- **Plugin validation**: verifies `.claude-plugin/plugin.json` exists and is valid JSON with expected skills and entry points
- **Homebrew-based installation**: all CLI tools install via Homebrew (except uv which uses curl); provides instructions if Homebrew is missing

## Workflow

Uses abbreviated workflow — phases 2 (Approach Selection) and 3 (Planning) are skipped.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal, assumptions, required tools, and success criteria |
| 1. Research & Options | yes | Analyze requirements and context |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Run setup scripts for tools, MCPs, hooks, and/or config |
| 5. Validate & Learn | yes | Report results and any items that need manual attention |

## Managed Resources

### CLI Tools

| Tool | Command | Install Method | Used By |
|------|---------|---------------|---------|
| git | `git` | `brew install git` | Nearly all skills |
| Python 3 | `python3` | `brew install python` | preflight.py, scripts |
| Node.js | `node` | `brew install node` | Diagram skills, audit-dependency |
| npm | `npm` | Bundled with node | Same as Node.js |
| jq | `jq` | `brew install jq` | Bitbucket, Confluence, Jira connectors |
| curl | `curl` | `brew install curl` | Bitbucket, Confluence, Jira connectors |
| Graphviz | `dot` | `brew install graphviz` | `/adk:diagram-graphviz` |
| uv / uvx | `uvx` | `curl` installer | Confluence MCP |
| Docker | `docker` | `brew install --cask docker` | GitHub MCP (Docker variant) |
| GitHub CLI | `gh` | `brew install gh` | PR management |
| diagramkit | `diagramkit` | `npm install -g diagramkit` | Mermaid, Excalidraw, draw.io, Graphviz diagram skills |
| pagesmith | `pagesmith` | `npm install -g @pagesmith/docs` | `/adk:docs-crud`, `/adk:docs-repo` |

### MCP Servers

| Server | Config Key | Transport | Env Vars from `~/.zshenv` |
|--------|-----------|-----------|--------------------------|
| GitHub | `github` | HTTP | `GITHUB_PAT` |
| Bitbucket | `bitbucket` | stdio | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| Confluence | `atlassian-confluence` | stdio | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Google Drive | `google-drive` | stdio | `GOOGLE_DRIVE_OAUTH_CREDENTIALS` |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |

## Output Format

All output is markdown. Post-setup validation reports:

- **Tools**: installation status, version info, and any tools that could not be installed (with Homebrew install instructions if Homebrew is missing)
- **MCPs**: configuration status, token sync results, and any servers skipped due to missing env vars
- **Hooks**: whether the SessionStart hook was added or already existed
- **Config**: whether `/adk:use` was set as default or was already configured

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:use` | The orchestrator that routes general prompts to the right skill |
| `/adk:project` | Initialize new projects and manage milestones |

## Examples

```
/adk:setup
/adk:setup --type tools
/adk:setup --type mcps
/adk:setup --type hooks
/adk:setup --type config
/adk:setup --check-only
/adk:setup --tool git
/adk:setup --tool diagramkit
/adk:setup --tool node --verbosity detailed
/adk:setup --server github
/adk:setup --server confluence
/adk:setup --skip-update
/adk:setup --type tools --check-only
/adk:setup --type mcps --check-only --verbosity short
```
