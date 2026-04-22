---
title: 'mcp-github'
description: 'GitHub MCP via Docker. Falls back to gh CLI if not enabled. Requires GITHUB_PAT env var (typically in ~/.zshenv).'
artifact_kind: mcp
---

# mcp-github

GitHub MCP via Docker. Falls back to gh CLI if not enabled. Requires GITHUB_PAT env var (typically in ~/.zshenv).

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "github": {
    "command": "sh",
    "args": [
      "-c",
      "GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PAT docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server"
    ],
    "env": {
      "GITHUB_PAT": "${GITHUB_PAT}"
    },
    "description": "GitHub MCP via Docker. Falls back to gh CLI if not enabled. Requires GITHUB_PAT env var (typically in ~/.zshenv)."
  }
}
```

## Required environment variables

- `GITHUB_PAT`

Set these in `~/.zshenv` (or your shell's env file) so they are present when Claude Code launches the plugin.

## Source

`.mcp.json` (entry: `github`).
