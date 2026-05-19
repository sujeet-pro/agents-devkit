---
title: 'adk-mcp-github'
description: 'GitHub hosted MCP. Acts on behalf of the authenticated identity (token scopes = MCP capability). Auth: fine-grained PAT in $GITHUB_TOKEN_CRED (preferred); falls back to classic PAT in $GITHUB_TOKEN_CRED if the first is...'
mcp: 'adk-mcp-github'
source: 'mcp/adk-mcp-github.json'
group: 'mcp'
order: 3002
---
# adk-mcp-github

GitHub hosted MCP. Acts on behalf of the authenticated identity (token scopes = MCP capability). Auth: fine-grained PAT in $GITHUB_TOKEN_CRED (preferred); falls back to classic PAT in $GITHUB_TOKEN_CRED if the first is unset. To switch to OAuth: remove the `headers` block; agent will run OAuth on first connect. Skills fall back through MCP → `gh` CLI → direct REST (last resort). See SETUP.md.

## Source

`mcp/adk-mcp-github.json`

## Environment variables referenced

- `GITHUB_TOKEN_CRED`

## Configuration

```json
{
  "name": "adk-mcp-github",
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": {
    "Authorization": "Bearer ${GITHUB_TOKEN_CRED:-${GITHUB_TOKEN_CRED}}"
  },
  "description": "GitHub hosted MCP. Acts on behalf of the authenticated identity (token scopes = MCP capability). Auth: fine-grained PAT in $GITHUB_TOKEN_CRED (preferred); falls back to classic PAT in $GITHUB_TOKEN_CRED if the first is unset. To switch to OAuth: remove the `headers` block; agent will run OAuth on first connect. Skills fall back through MCP → `gh` CLI → direct REST (last resort). See SETUP.md."
}
```
