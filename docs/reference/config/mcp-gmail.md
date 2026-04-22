---
title: 'mcp-gmail'
description: 'Gmail MCP. Requires GMAIL_CREDENTIALS_PATH env var.'
artifact_kind: mcp
---

# mcp-gmail

Gmail MCP. Requires GMAIL_CREDENTIALS_PATH env var.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "gmail": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-gmail"
    ],
    "env": {
      "GMAIL_CREDENTIALS_PATH": "${GMAIL_CREDENTIALS_PATH}"
    },
    "description": "Gmail MCP. Requires GMAIL_CREDENTIALS_PATH env var."
  }
}
```

## Required environment variables

- `GMAIL_CREDENTIALS_PATH`

Set these in `~/.zshenv` (or your shell's env file) so they are present when Claude Code launches the plugin.

## Source

`.mcp.json` (entry: `gmail`).
