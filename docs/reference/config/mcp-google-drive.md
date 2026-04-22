---
title: 'mcp-google-drive'
description: 'Google Drive MCP.'
artifact_kind: mcp
---

# mcp-google-drive

Google Drive MCP. Requires GDRIVE_CREDENTIALS_PATH env var pointing to OAuth credentials JSON.

## Usage

Install via `bin/adk-mcp-install`:

```bash
node bin/adk-mcp-install              # interactive picker
node bin/adk-mcp-install --auto       # enable every server with env vars present
```

The installer reads `.mcp.json`, resolves `${ENV_VAR}` placeholders from `~/.zshenv`, and registers the server with `claude mcp add`.

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

Set these in `~/.zshenv` before running `bin/adk-mcp-install`.

## Source

`.mcp.json` (entry: `google-drive`).
