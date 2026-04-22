---
title: MCP Setup
description: How the adk Claude Code plugin auto-loads MCP servers from .mcp.json and resolves their ${ENV_VAR} placeholders from your shell env.
---

# MCP Setup

MCP servers are optional. The `adk` plugin ships a single `.mcp.json` at the repo root that Claude Code loads automatically when the plugin is enabled — there is no separate installer step.

## Available servers

`.mcp.json` registers these 13 servers (one section per page under `docs/reference/config/mcp-<name>.md`):

- `bitbucket`
- `brainstorming`
- `chrome-devtools`
- `confluence`
- `cursor-ide-browser`
- `datadog`
- `github`
- `gmail`
- `google-drive`
- `jira`
- `mixpanel`
- `playwright`
- `slack`

Each entry declares its `command`, `args`, and an `env` map with `${ENV_VAR}` placeholders that Claude Code resolves from the launching shell at session start.

## How loading works

1. You install the `adk` plugin (locally via `claude --plugin-dir <path>`, or from the marketplace at `.claude-plugin/marketplace.json`).
2. Claude Code reads `.mcp.json` when the plugin is loaded.
3. For each server, every `${ENV_VAR}` in `args` / `env` is substituted from `process.env`.
4. The server is registered with its own MCP transport (stdio / docker / npx) and tools become available in the session.

To inspect or override entries, edit `.mcp.json` directly and reload the plugin with `/reload-plugins`.

## Setting environment variables

Add the required env vars to `~/.zshenv` (or your shell's equivalent) before launching Claude. Example:

```bash
# ~/.zshenv
export GITHUB_PAT=ghp_...
export ATLASSIAN_EMAIL=you@company.com
export ATLASSIAN_API_TOKEN=...
export DD_API_KEY=...
export DD_APP_KEY=...
export DD_SITE=datadoghq.com
```

Each per-server page lists its own required env vars.

## MCP fallback in skills

Skills like `/adk:plan-brainstorm` prefer the `brainstorming` MCP server when configured but ship a fallback workflow when it is missing. They warn once and continue.

## Source

`.mcp.json` at the repo root.
