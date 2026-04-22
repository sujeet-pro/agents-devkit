---
title: 'mcp-mixpanel'
description: 'Mixpanel MCP. Requires MIXPANEL_PROJECT_ID and service-account credentials.'
artifact_kind: mcp
---

# mcp-mixpanel

Mixpanel MCP. Requires MIXPANEL_PROJECT_ID and service-account credentials.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "mixpanel": {
    "command": "npx",
    "args": [
      "-y",
      "@mixpanel/mcp-server"
    ],
    "env": {
      "MIXPANEL_PROJECT_ID": "${MIXPANEL_PROJECT_ID}",
      "MIXPANEL_SERVICE_ACCOUNT_USER": "${MIXPANEL_SERVICE_ACCOUNT_USER}",
      "MIXPANEL_SERVICE_ACCOUNT_SECRET": "${MIXPANEL_SERVICE_ACCOUNT_SECRET}"
    },
    "description": "Mixpanel MCP. Requires MIXPANEL_PROJECT_ID and service-account credentials."
  }
}
```

## Required environment variables

- `MIXPANEL_PROJECT_ID`
- `MIXPANEL_SERVICE_ACCOUNT_SECRET`
- `MIXPANEL_SERVICE_ACCOUNT_USER`

Set these in `~/.zshenv` (or your shell's env file) so they are present when Claude Code launches the plugin.

## Source

`.mcp.json` (entry: `mixpanel`).
