---
title: 'adk-mcp-bitbucket'
description: 'Bitbucket Cloud MCP via npx — npm bitbucket-mcp (MatanYemini/bitbucket-mcp). Read + write (PRs, repos, branches, commits, pipelines); destructive ops are gated behind BITBUCKET_ENABLE_DANGEROUS=true (we leave it...'
mcp: 'adk-mcp-bitbucket'
source: 'mcp/adk-mcp-bitbucket.json'
group: 'mcp'
order: 3001
---
# adk-mcp-bitbucket

Bitbucket Cloud MCP via npx — npm bitbucket-mcp (MatanYemini/bitbucket-mcp). Read + write (PRs, repos, branches, commits, pipelines); destructive ops are gated behind BITBUCKET_ENABLE_DANGEROUS=true (we leave it unset, per shared/constitution.md §I). Auth: Atlassian API token (the unified API token replacing legacy Bitbucket app passwords) in $BITBUCKET_TOKEN_CRED, passed as BITBUCKET_PASSWORD per the upstream README's 'Atlassian API Key' note. $BITBUCKET_USERNAME is your Bitbucket account email (not the legacy username). $BITBUCKET_WORKSPACE defaults the workspace for tools that take one. Mint a token at https://id.atlassian.com/manage-profile/security/api-tokens with scopes: Repositories:Read, Pull requests:Read+Write, Pipelines:Read. Requires `node`/`npx` on PATH. See SETUP.md.

## Source

`mcp/adk-mcp-bitbucket.json`

## Environment variables referenced

- `BITBUCKET_TOKEN_CRED`
- `BITBUCKET_URL`
- `BITBUCKET_USERNAME`
- `BITBUCKET_WORKSPACE`

## Configuration

```json
{
  "name": "adk-mcp-bitbucket",
  "command": "npx",
  "args": [
    "-y",
    "bitbucket-mcp@latest"
  ],
  "env": {
    "BITBUCKET_URL": "${BITBUCKET_URL:-https://api.bitbucket.org/2.0}",
    "BITBUCKET_USERNAME": "${BITBUCKET_USERNAME}",
    "BITBUCKET_WORKSPACE": "${BITBUCKET_WORKSPACE}",
    "BITBUCKET_PASSWORD": "${BITBUCKET_TOKEN_CRED}"
  },
  "description": "Bitbucket Cloud MCP via npx — npm bitbucket-mcp (MatanYemini/bitbucket-mcp). Read + write (PRs, repos, branches, commits, pipelines); destructive ops are gated behind BITBUCKET_ENABLE_DANGEROUS=true (we leave it unset, per shared/constitution.md §I). Auth: Atlassian API token (the unified API token replacing legacy Bitbucket app passwords) in $BITBUCKET_TOKEN_CRED, passed as BITBUCKET_PASSWORD per the upstream README's 'Atlassian API Key' note. $BITBUCKET_USERNAME is your Bitbucket account email (not the legacy username). $BITBUCKET_WORKSPACE defaults the workspace for tools that take one. Mint a token at https://id.atlassian.com/manage-profile/security/api-tokens with scopes: Repositories:Read, Pull requests:Read+Write, Pipelines:Read. Requires `node`/`npx` on PATH. See SETUP.md."
}
```
