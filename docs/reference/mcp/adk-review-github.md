---
title: 'adk-review:github'
description: 'GitHub MCP via Docker (ghcr.io/github/github-mcp-server pinned to v1.0.3). Requires GITHUB_PAT (fine-grained PAT, repo+pull-request+actions+read:org). Read-only by default; flip GITHUB_READ_ONLY=0 only for approved postback stages. See SETUP.md.'
plugin: 'adk-review'
mcp: 'github'
source: 'plugins/adk-review/.mcp.json'
group: 'review-mcp'
order: 2301
---
# adk-review:github

GitHub MCP via Docker (ghcr.io/github/github-mcp-server pinned to v1.0.3). Requires GITHUB_PAT (fine-grained PAT, repo+pull-request+actions+read:org). Read-only by default; flip GITHUB_READ_ONLY=0 only for approved postback stages. See SETUP.md.

## Source

`plugins/adk-review/.mcp.json`

## Environment Variables

- `GITHUB_PAT`
- `GITHUB_READ_ONLY`
- `GITHUB_TOOLSETS`

## Configuration

```json
{
  "github": {
    "command": "sh",
    "args": [
      "-c",
      "GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PAT GITHUB_TOOLSETS=$GITHUB_TOOLSETS GITHUB_READ_ONLY=$GITHUB_READ_ONLY docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN -e GITHUB_TOOLSETS -e GITHUB_READ_ONLY ghcr.io/github/github-mcp-server:v1.0.3"
    ],
    "env": {
      "GITHUB_PAT": "${GITHUB_PAT}",
      "GITHUB_TOOLSETS": "${GITHUB_TOOLSETS:-context,repos,issues,pull_requests,actions,users}",
      "GITHUB_READ_ONLY": "${GITHUB_READ_ONLY:-1}"
    },
    "description": "GitHub MCP via Docker (ghcr.io/github/github-mcp-server pinned to v1.0.3). Requires GITHUB_PAT (fine-grained PAT, repo+pull-request+actions+read:org). Read-only by default; flip GITHUB_READ_ONLY=0 only for approved postback stages. See SETUP.md."
  }
}
```
