---
title: MCP Setup
description: How ADK installs MCP server configs and reads / writes their env vars via ~/.zshenv.
---

# MCP Setup

MCP servers are optional. `adk-install` knows about them, can wire them into each runtime's `mcp.json`, and persists their env vars to `~/.zshenv`.

## Available servers

The package ships one config per server under `mcp-config/servers/<name>.json`:

- `github`
- `bitbucket`
- `confluence`
- `jira`
- `google-drive`
- `brainstorming`

Each JSON declares the runtime command line and an `env` map with `${ENV_VAR}` placeholders.

## How the installer wires MCP

When you pick MCP servers in the `adk-install` prompt, the CLI:

1. Reads existing values from `~/.zshenv`.
2. Prompts for any env vars that don't have a value, with a one-line "how to get this" hint.
3. Appends new exports to `~/.zshenv` (with confirmation).
4. Merges each server config into every chosen runtime's `mcp.json` under the `mcpServers` key, preserving servers you have already configured manually.

Re-running converges: removed servers are not pruned (so you can add a server manually and keep it), but added/changed entries always overwrite the ADK-managed ones.

## Per-runtime config paths

| Runtime | Path |
| --- | --- |
| Claude Code | `<root>/.claude/mcp.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) |
| Cursor | `<root>/.cursor/mcp.json` |
| Codex CLI | `<root>/.codex/mcp.json` |
| Codex Desktop | `~/Library/Application Support/Codex/mcp.json` (macOS) |
| Gemini CLI | `<root>/.gemini/mcp.json` |

`<root>` is `$HOME` for global mode and the project root for project mode.

## Brainstorming MCP fallback

Skills like `adk-plan-brainstorm` prefer the `brainstorming` MCP server when configured but ship a `references/mcp-fallback.md` describing the manual workflow when it is missing. Skills will warn once and continue.

## Env-var portability

Use environment variables (`BITBUCKET_USERNAME`, `BRAINSTORMING_MCP_ROOT`, etc.) instead of hard-coded paths. This keeps a project's `mcp.json` portable across machines.
