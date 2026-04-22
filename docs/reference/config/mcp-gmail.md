---
title: 'mcp-gmail'
description: 'Gmail MCP.'
artifact_kind: mcp
---

# mcp-gmail

Gmail MCP. Requires GMAIL_CREDENTIALS_PATH env var.

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

Set these in `~/.zshenv` before running `bin/adk-mcp-install`.

## Source

`.mcp.json` (entry: `gmail`).
