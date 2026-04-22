---
title: 'mcp-datadog'
description: 'Datadog MCP.'
artifact_kind: mcp
---

# mcp-datadog

Datadog MCP. Requires DD_API_KEY, DD_APP_KEY, DD_SITE (e.g. datadoghq.com) env vars.

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

Set these in `~/.zshenv` before running `bin/adk-mcp-install`.

## Source

`.mcp.json` (entry: `datadog`).
