---
title: 'adk-mcp-atlassian'
description: 'Atlassian MCP via uvx — Python package sooperset/mcp-atlassian. Covers Jira + Confluence including image / attachment upload (which the Anthropic Rovo connector does not). Auth: API token (ATLASSIAN_SITE +...'
mcp: 'adk-mcp-atlassian'
source: 'mcp/adk-mcp-atlassian.json'
group: 'mcp'
order: 3000
---
# adk-mcp-atlassian

Atlassian MCP via uvx — Python package sooperset/mcp-atlassian. Covers Jira + Confluence including image / attachment upload (which the Anthropic Rovo connector does not). Auth: API token (ATLASSIAN_SITE + ATLASSIAN_USERNAME + ATLASSIAN_API_TOKEN at https://id.atlassian.com/manage-profile/security/api-tokens). For OAuth: set ATLASSIAN_OAUTH_* per upstream README and remove the env block above. Requires `uv` on PATH. See SETUP.md.

## Source

`mcp/adk-mcp-atlassian.json`

## Environment variables referenced

- `ATLASSIAN_API_TOKEN`
- `ATLASSIAN_SITE`
- `ATLASSIAN_USERNAME`

## Configuration

```json
{
  "name": "adk-mcp-atlassian",
  "command": "uvx",
  "args": [
    "mcp-atlassian@latest"
  ],
  "env": {
    "CONFLUENCE_URL": "https://${ATLASSIAN_SITE}/wiki",
    "CONFLUENCE_USERNAME": "${ATLASSIAN_USERNAME}",
    "CONFLUENCE_API_TOKEN": "${ATLASSIAN_API_TOKEN}",
    "JIRA_URL": "https://${ATLASSIAN_SITE}",
    "JIRA_USERNAME": "${ATLASSIAN_USERNAME}",
    "JIRA_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
  },
  "description": "Atlassian MCP via uvx — Python package sooperset/mcp-atlassian. Covers Jira + Confluence including image / attachment upload (which the Anthropic Rovo connector does not). Auth: API token (ATLASSIAN_SITE + ATLASSIAN_USERNAME + ATLASSIAN_API_TOKEN at https://id.atlassian.com/manage-profile/security/api-tokens). For OAuth: set ATLASSIAN_OAUTH_* per upstream README and remove the env block above. Requires `uv` on PATH. See SETUP.md."
}
```
