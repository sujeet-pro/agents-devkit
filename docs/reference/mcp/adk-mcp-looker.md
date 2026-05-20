---
title: 'adk-mcp-looker'
description: 'Looker MCP via uvx. Read-only. Auth: API3 client credentials (mint in Looker Admin > Users > Edit > API3 keys). The server reads LOOKER_BASE_URL / LOOKER_CLIENT_ID / LOOKER_CLIENT_SECRET natively — we map them into...'
mcp: 'adk-mcp-looker'
source: 'mcp/adk-mcp-looker.json'
group: 'mcp'
order: 3005
---
# adk-mcp-looker

Looker MCP via uvx. Read-only. Auth: API3 client credentials (mint in Looker Admin > Users > Edit > API3 keys). The server reads LOOKER_BASE_URL / LOOKER_CLIENT_ID / LOOKER_CLIENT_SECRET natively — we map them into the subprocess from LOOKER_BASE_URL + our `_CRED` vars. Covers dashboards, looks, explores, fields, and safe SQL queries. Use overrides.yaml.data_sources.looker.{dashboards,explores} for the metadata cache. See SETUP.md.

## Source

`mcp/adk-mcp-looker.json`

## Environment variables referenced

- `LOOKER_BASE_URL`
- `LOOKER_CLIENT_ID_CRED`
- `LOOKER_CLIENT_SECRET_CRED`
- `LOOKER_VERIFY_SSL`

## Configuration

```json
{
  "name": "adk-mcp-looker",
  "command": "uvx",
  "args": [
    "looker-mcp-server@latest",
    "--groups",
    "explore,query,schema,content"
  ],
  "env": {
    "LOOKER_BASE_URL": "${LOOKER_BASE_URL}",
    "LOOKER_CLIENT_ID": "${LOOKER_CLIENT_ID_CRED}",
    "LOOKER_CLIENT_SECRET": "${LOOKER_CLIENT_SECRET_CRED}",
    "LOOKER_VERIFY_SSL": "${LOOKER_VERIFY_SSL:-true}"
  },
  "description": "Looker MCP via uvx. Read-only. Auth: API3 client credentials (mint in Looker Admin > Users > Edit > API3 keys). The server reads LOOKER_BASE_URL / LOOKER_CLIENT_ID / LOOKER_CLIENT_SECRET natively — we map them into the subprocess from LOOKER_BASE_URL + our `_CRED` vars. Covers dashboards, looks, explores, fields, and safe SQL queries. Use overrides.yaml.data_sources.looker.{dashboards,explores} for the metadata cache. See SETUP.md."
}
```
