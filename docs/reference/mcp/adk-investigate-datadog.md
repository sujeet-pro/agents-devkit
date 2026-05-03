---
title: 'adk-investigate:datadog'
description: 'Datadog hosted MCP (Preview). Auth via DD_API_KEY + DD_APP_KEY (App key needs scope `mcp_read`; add `mcp_write` only if you actually need to mute/silence monitors). Override DD_MCP_URL for non-US1 sites: datadoghq.eu, us3.datadoghq.com, us5.datadoghq.com, ap1.datadoghq.com, ap2.datadoghq.com. NOT GovCloud-eligible. See SETUP.md.'
plugin: 'adk-investigate'
mcp: 'datadog'
source: 'plugins/adk-investigate/.mcp.json'
group: 'investigate-mcp'
order: 4301
---
# adk-investigate:datadog

Datadog hosted MCP (Preview). Auth via DD_API_KEY + DD_APP_KEY (App key needs scope `mcp_read`; add `mcp_write` only if you actually need to mute/silence monitors). Override DD_MCP_URL for non-US1 sites: datadoghq.eu, us3.datadoghq.com, us5.datadoghq.com, ap1.datadoghq.com, ap2.datadoghq.com. NOT GovCloud-eligible. See SETUP.md.

## Source

`plugins/adk-investigate/.mcp.json`

## Environment Variables

- `DD_API_KEY`
- `DD_APP_KEY`
- `DD_MCP_URL`

## Configuration

```json
{
  "datadog": {
    "type": "http",
    "url": "${DD_MCP_URL:-https://mcp.datadoghq.com/api/unstable/mcp-server/mcp}?toolsets=core,dashboards,error-tracking,product-analytics,security,workflows,apm,llmobs",
    "headers": {
      "DD_API_KEY": "${DD_API_KEY}",
      "DD_APPLICATION_KEY": "${DD_APP_KEY}"
    },
    "description": "Datadog hosted MCP (Preview). Auth via DD_API_KEY + DD_APP_KEY (App key needs scope `mcp_read`; add `mcp_write` only if you actually need to mute/silence monitors). Override DD_MCP_URL for non-US1 sites: datadoghq.eu, us3.datadoghq.com, us5.datadoghq.com, ap1.datadoghq.com, ap2.datadoghq.com. NOT GovCloud-eligible. See SETUP.md."
  }
}
```
