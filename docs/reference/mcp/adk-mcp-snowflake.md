---
title: 'adk-mcp-snowflake'
description: 'Snowflake MCP via uvx (community: isaacwasserman/mcp-snowflake-server). Read-only by default (per shared/constitution.md §I). Auth: password (SNOWFLAKE_PASSWORD) OR externalbrowser SSO (set...'
mcp: 'adk-mcp-snowflake'
source: 'mcp/adk-mcp-snowflake.json'
group: 'mcp'
order: 3007
---
# adk-mcp-snowflake

Snowflake MCP via uvx (community: isaacwasserman/mcp-snowflake-server). Read-only by default (per shared/constitution.md §I). Auth: password (SNOWFLAKE_PASSWORD) OR externalbrowser SSO (set SNOWFLAKE_AUTHENTICATOR=externalbrowser). PII protection: skills refuse to query columns listed in overrides.yaml.data_sources.snowflake.pii_columns. Requires `uv` on PATH. See SETUP.md.

## Source

`mcp/adk-mcp-snowflake.json`

## Environment variables referenced

- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_AUTHENTICATOR`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_ROLE`
- `SNOWFLAKE_SCHEMA`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_WAREHOUSE`

## Configuration

```json
{
  "name": "adk-mcp-snowflake",
  "command": "uvx",
  "args": [
    "mcp-snowflake-server@latest"
  ],
  "env": {
    "SNOWFLAKE_ACCOUNT": "${SNOWFLAKE_ACCOUNT}",
    "SNOWFLAKE_USER": "${SNOWFLAKE_USER}",
    "SNOWFLAKE_PASSWORD": "${SNOWFLAKE_PASSWORD:-}",
    "SNOWFLAKE_AUTHENTICATOR": "${SNOWFLAKE_AUTHENTICATOR:-}",
    "SNOWFLAKE_WAREHOUSE": "${SNOWFLAKE_WAREHOUSE}",
    "SNOWFLAKE_ROLE": "${SNOWFLAKE_ROLE}",
    "SNOWFLAKE_DATABASE": "${SNOWFLAKE_DATABASE:-}",
    "SNOWFLAKE_SCHEMA": "${SNOWFLAKE_SCHEMA:-}"
  },
  "description": "Snowflake MCP via uvx (community: isaacwasserman/mcp-snowflake-server). Read-only by default (per shared/constitution.md §I). Auth: password (SNOWFLAKE_PASSWORD) OR externalbrowser SSO (set SNOWFLAKE_AUTHENTICATOR=externalbrowser). PII protection: skills refuse to query columns listed in overrides.yaml.data_sources.snowflake.pii_columns. Requires `uv` on PATH. See SETUP.md."
}
```
