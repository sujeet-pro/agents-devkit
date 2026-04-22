---
title: 'mcp-datadog'
description: 'Datadog MCP. Requires DD_API_KEY, DD_APP_KEY, DD_SITE (e.g. datadoghq.com) env vars.'
artifact_kind: mcp
---

# mcp-datadog

Datadog MCP. Requires DD_API_KEY, DD_APP_KEY, DD_SITE (e.g. datadoghq.com) env vars.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "datadog": {
    "command": "npx",
    "args": [
      "-y",
      "@datadog/mcp-server"
    ],
    "env": {
      "DD_API_KEY": "${DD_API_KEY}",
      "DD_APP_KEY": "${DD_APP_KEY}",
      "DD_SITE": "${DD_SITE}"
    },
    "description": "Datadog MCP. Requires DD_API_KEY, DD_APP_KEY, DD_SITE (e.g. datadoghq.com) env vars."
  }
}
```

## Required environment variables

- `DD_API_KEY`
- `DD_APP_KEY`
- `DD_SITE`

Set these in `~/.zshenv` (or your shell's env file) so they are present when Claude Code launches the plugin.

## Source

`.mcp.json` (entry: `datadog`).
