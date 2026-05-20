---
title: 'adk-mcp-datadog'
description: 'Datadog Bits AI hosted MCP (Preview). Auth: DATADOG_API_KEY_CRED + DATADOG_APP_KEY_CRED (App key needs scope mcp_read; mcp_write only if you mute monitors). Non-US1 sites: set DATADOG_MCP_URL to the regional MCP...'
mcp: 'adk-mcp-datadog'
source: 'mcp/adk-mcp-datadog.json'
group: 'mcp'
order: 3002
---
# adk-mcp-datadog

Datadog Bits AI hosted MCP (Preview). Auth: DATADOG_API_KEY_CRED + DATADOG_APP_KEY_CRED (App key needs scope mcp_read; mcp_write only if you mute monitors). Non-US1 sites: set DATADOG_MCP_URL to the regional MCP host. The Datadog server itself reads DD_API_KEY / DD_APPLICATION_KEY natively — we map those header names to our _CRED vars at request time. Not GovCloud-eligible. See SETUP.md.

## Source

`mcp/adk-mcp-datadog.json`

## Environment variables referenced

- `DATADOG_API_KEY_CRED`
- `DATADOG_APP_KEY_CRED`
- `DATADOG_MCP_URL`

## Configuration

```json
{
  "name": "adk-mcp-datadog",
  "type": "http",
  "url": "${DATADOG_MCP_URL:-https://mcp.datadoghq.com/api/unstable/mcp-server/mcp}?toolsets=core,dashboards,error-tracking,product-analytics,security,workflows,apm,llmobs",
  "headers": {
    "DD_API_KEY": "${DATADOG_API_KEY_CRED}",
    "DD_APPLICATION_KEY": "${DATADOG_APP_KEY_CRED}"
  },
  "description": "Datadog Bits AI hosted MCP (Preview). Auth: DATADOG_API_KEY_CRED + DATADOG_APP_KEY_CRED (App key needs scope mcp_read; mcp_write only if you mute monitors). Non-US1 sites: set DATADOG_MCP_URL to the regional MCP host. The Datadog server itself reads DD_API_KEY / DD_APPLICATION_KEY natively — we map those header names to our _CRED vars at request time. Not GovCloud-eligible. See SETUP.md."
}
```
