---
title: 'adk-mcp-github'
description: 'GitHub hosted MCP. Acts on behalf of the authenticated identity (token scopes = MCP capability). Auth: fine-grained PAT in $GITHUB_PAT (preferred); falls back to classic PAT in $GITHUB_PAT_CLASSIC if the first is...'
mcp: 'adk-mcp-github'
source: 'mcp/adk-mcp-github.json'
group: 'mcp'
order: 3002
---
# adk-mcp-github

GitHub hosted MCP. Acts on behalf of the authenticated identity (token scopes = MCP capability). Auth: fine-grained PAT in $GITHUB_PAT (preferred); falls back to classic PAT in $GITHUB_PAT_CLASSIC if the first is unset. To switch to OAuth: remove the `headers` block; agent will run OAuth on first connect. Skills fall back through MCP → `gh` CLI → direct REST (last resort). See SETUP.md.

## Source

`mcp/adk-mcp-github.json`

## Environment variables referenced

- `GITHUB_PAT`

## Configuration

```json
{
  "name": "adk-mcp-github",
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": {
    "Authorization": "Bearer ${GITHUB_PAT:-${GITHUB_PAT_CLASSIC}}"
  },
  "description": "GitHub hosted MCP. Acts on behalf of the authenticated identity (token scopes = MCP capability). Auth: fine-grained PAT in $GITHUB_PAT (preferred); falls back to classic PAT in $GITHUB_PAT_CLASSIC if the first is unset. To switch to OAuth: remove the `headers` block; agent will run OAuth on first connect. Skills fall back through MCP → `gh` CLI → direct REST (last resort). See SETUP.md."
}
```
