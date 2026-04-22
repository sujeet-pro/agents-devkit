---
title: 'mcp-google-drive'
description: 'Google Drive MCP. Requires GDRIVE_CREDENTIALS_PATH env var pointing to OAuth credentials JSON.'
artifact_kind: mcp
---

# mcp-google-drive

Google Drive MCP. Requires GDRIVE_CREDENTIALS_PATH env var pointing to OAuth credentials JSON.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "google-drive": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-gdrive"
    ],
    "env": {
      "GDRIVE_CREDENTIALS_PATH": "${GDRIVE_CREDENTIALS_PATH}"
    },
    "description": "Google Drive MCP. Requires GDRIVE_CREDENTIALS_PATH env var pointing to OAuth credentials JSON."
  }
}
```

## Required environment variables

- `GDRIVE_CREDENTIALS_PATH`

Set these in `~/.zshenv` (or your shell's env file) so they are present when Claude Code launches the plugin.

## Source

`.mcp.json` (entry: `google-drive`).
