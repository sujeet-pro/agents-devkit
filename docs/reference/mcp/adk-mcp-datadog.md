---
title: 'adk-mcp-datadog'
description: 'Datadog Bits AI hosted MCP (Preview). Auth: DATADOG_API_KEY + DATADOG_APP_KEY (App key needs scope mcp_read; mcp_write only if you mute monitors). Non-US1 sites: override DD_MCP_URL to the regional MCP host. Legacy...'
mcp: 'adk-mcp-datadog'
source: 'mcp/adk-mcp-datadog.json'
group: 'mcp'
order: 3001
---
# adk-mcp-datadog

Datadog Bits AI hosted MCP (Preview). Auth: DATADOG_API_KEY + DATADOG_APP_KEY (App key needs scope mcp_read; mcp_write only if you mute monitors). Non-US1 sites: override DD_MCP_URL to the regional MCP host. Legacy DD_API_KEY / DD_APP_KEY env names: alias them to the canonical names in your shell rc. Not GovCloud-eligible. See SETUP.md.

## Source

`mcp/adk-mcp-datadog.json`

## Environment variables referenced

- `DATADOG_API_KEY`
- `DATADOG_APP_KEY`
- `DD_MCP_URL`

## Configuration

```json
{
  "name": "adk-mcp-datadog",
  "type": "http",
  "url": "${DD_MCP_URL:-https://mcp.datadoghq.com/api/unstable/mcp-server/mcp}?toolsets=core,dashboards,error-tracking,product-analytics,security,workflows,apm,llmobs",
  "headers": {
    "DD_API_KEY": "${DATADOG_API_KEY}",
    "DD_APPLICATION_KEY": "${DATADOG_APP_KEY}"
  },
  "description": "Datadog Bits AI hosted MCP (Preview). Auth: DATADOG_API_KEY + DATADOG_APP_KEY (App key needs scope mcp_read; mcp_write only if you mute monitors). Non-US1 sites: override DD_MCP_URL to the regional MCP host. Legacy DD_API_KEY / DD_APP_KEY env names: alias them to the canonical names in your shell rc. Not GovCloud-eligible. See SETUP.md."
}
```
