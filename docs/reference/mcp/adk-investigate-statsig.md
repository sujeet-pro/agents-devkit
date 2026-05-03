---
title: 'adk-investigate:statsig'
description: 'Statsig hosted MCP. Header auth via STATSIG_CONSOLE_API_KEY (https://console.statsig.com/api_keys → type=Console → scope=omni_read_only). For browser-based OAuth, omit headers. Use omni_write only for skills that toggle gates / start experiments. See SETUP.md.'
plugin: 'adk-investigate'
mcp: 'statsig'
source: 'plugins/adk-investigate/.mcp.json'
group: 'investigate-mcp'
order: 4302
---
# adk-investigate:statsig

Statsig hosted MCP. Header auth via STATSIG_CONSOLE_API_KEY (https://console.statsig.com/api_keys → type=Console → scope=omni_read_only). For browser-based OAuth, omit headers. Use omni_write only for skills that toggle gates / start experiments. See SETUP.md.

## Source

`plugins/adk-investigate/.mcp.json`

## Environment Variables

- `STATSIG_CONSOLE_API_KEY`

## Configuration

```json
{
  "statsig": {
    "type": "http",
    "url": "https://api.statsig.com/v1/mcp",
    "headers": {
      "statsig-api-key": "${STATSIG_CONSOLE_API_KEY}"
    },
    "description": "Statsig hosted MCP. Header auth via STATSIG_CONSOLE_API_KEY (https://console.statsig.com/api_keys → type=Console → scope=omni_read_only). For browser-based OAuth, omit headers. Use omni_write only for skills that toggle gates / start experiments. See SETUP.md."
  }
}
```
