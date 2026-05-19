---
title: 'adk-mcp-statsig'
description: 'Statsig hosted MCP. Auth: STATSIG_CONSOLE_API_KEY_CRED (mint at https://console.statsig.com/api_keys with type=Console, scope=omni_read_only). For OAuth: remove headers; agent runs browser flow. Use omni_write only for...'
mcp: 'adk-mcp-statsig'
source: 'mcp/adk-mcp-statsig.json'
group: 'mcp'
order: 3008
---
# adk-mcp-statsig

Statsig hosted MCP. Auth: STATSIG_CONSOLE_API_KEY_CRED (mint at https://console.statsig.com/api_keys with type=Console, scope=omni_read_only). For OAuth: remove headers; agent runs browser flow. Use omni_write only for skills that toggle gates / start experiments (none of adk's read-only skills need this). See SETUP.md.

## Source

`mcp/adk-mcp-statsig.json`

## Environment variables referenced

- `STATSIG_CONSOLE_API_KEY_CRED`

## Configuration

```json
{
  "name": "adk-mcp-statsig",
  "type": "http",
  "url": "https://api.statsig.com/v1/mcp",
  "headers": {
    "statsig-api-key": "${STATSIG_CONSOLE_API_KEY_CRED}"
  },
  "description": "Statsig hosted MCP. Auth: STATSIG_CONSOLE_API_KEY_CRED (mint at https://console.statsig.com/api_keys with type=Console, scope=omni_read_only). For OAuth: remove headers; agent runs browser flow. Use omni_write only for skills that toggle gates / start experiments (none of adk's read-only skills need this). See SETUP.md."
}
```
