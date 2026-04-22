---
title: 'mcp-mixpanel'
description: 'Mixpanel MCP.'
artifact_kind: mcp
---

# mcp-mixpanel

Mixpanel MCP. Requires MIXPANEL_PROJECT_ID and service-account credentials.

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
- `MIXPANEL_SERVICE_ACCOUNT_USER`
- `MIXPANEL_SERVICE_ACCOUNT_SECRET`

Set these in `~/.zshenv` before running `bin/adk-mcp-install`.

## Source

`.mcp.json` (entry: `mixpanel`).
