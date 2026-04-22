---
title: 'mcp-bitbucket'
description: 'Bitbucket Cloud MCP. Requires BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD env vars.'
artifact_kind: mcp
---

# mcp-bitbucket

Bitbucket Cloud MCP. Requires BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD env vars.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "bitbucket": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-e",
      "BITBUCKET_USERNAME",
      "-e",
      "BITBUCKET_APP_PASSWORD",
      "ghcr.io/atlassian-mcp/bitbucket-mcp-server"
    ],
    "env": {
      "BITBUCKET_USERNAME": "${BITBUCKET_USERNAME}",
      "BITBUCKET_APP_PASSWORD": "${BITBUCKET_APP_PASSWORD}"
    },
    "description": "Bitbucket Cloud MCP. Requires BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD env vars."
  }
}
```

## Required environment variables

- `BITBUCKET_APP_PASSWORD`
- `BITBUCKET_USERNAME`

Set these in `~/.zshenv` (or your shell's env file) so they are present when Claude Code launches the plugin.

## Source

`.mcp.json` (entry: `bitbucket`).
