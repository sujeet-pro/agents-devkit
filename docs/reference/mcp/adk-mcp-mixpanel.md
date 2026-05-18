---
title: 'adk-mcp-mixpanel'
description: 'Mixpanel hosted MCP. OAuth on first connect (browser pop, cached) — no env vars required. Covers events, funnels, cohorts, dashboards, experiments, feature flags. Project resolved from the authenticated identity; pin...'
mcp: 'adk-mcp-mixpanel'
source: 'mcp/adk-mcp-mixpanel.json'
group: 'mcp'
order: 3004
---
# adk-mcp-mixpanel

Mixpanel hosted MCP. OAuth on first connect (browser pop, cached) — no env vars required. Covers events, funnels, cohorts, dashboards, experiments, feature flags. Project resolved from the authenticated identity; pin the canonical project_id in ~/.config/adk/overrides.yaml.repos[*].mixpanel.project_id so skills don't ask. See SETUP.md.

## Source

`mcp/adk-mcp-mixpanel.json`

## Environment variables referenced

_(none)_

## Configuration

```json
{
  "name": "adk-mcp-mixpanel",
  "type": "http",
  "url": "https://mcp.mixpanel.com/mcp",
  "description": "Mixpanel hosted MCP. OAuth on first connect (browser pop, cached) — no env vars required. Covers events, funnels, cohorts, dashboards, experiments, feature flags. Project resolved from the authenticated identity; pin the canonical project_id in ~/.config/adk/overrides.yaml.repos[*].mixpanel.project_id so skills don't ask. See SETUP.md."
}
```
