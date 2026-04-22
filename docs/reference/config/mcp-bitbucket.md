---
title: 'mcp-bitbucket'
description: 'Bitbucket Cloud MCP.'
artifact_kind: mcp
---

# mcp-bitbucket

Bitbucket Cloud MCP. Requires BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD env vars.

## Usage

Install via `bin/adk-mcp-install`:

```bash
node bin/adk-mcp-install              # interactive picker
node bin/adk-mcp-install --auto       # enable every server with env vars present
```

The installer reads `.mcp.json`, resolves `${ENV_VAR}` placeholders from `~/.zshenv`, and registers the server with `claude mcp add`.

## Configuration

```json
{
  "bitbucket": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-e",
      "BITBUCKET_USERNAME",
      "-e",
      "BITBUCKET_APP_PASSWORD",
      "ghcr.io/atlassian-mcp/bitbucket-mcp-server"
    ],
    "env": {
      "BITBUCKET_USERNAME": "${BITBUCKET_USERNAME}",
      "BITBUCKET_APP_PASSWORD": "${BITBUCKET_APP_PASSWORD}"
    },
    "description": "Bitbucket Cloud MCP. Requires BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD env vars."
  }
}
```

## Required environment variables

- `BITBUCKET_USERNAME`
- `BITBUCKET_APP_PASSWORD`

Set these in `~/.zshenv` before running `bin/adk-mcp-install`.

## Source

`.mcp.json` (entry: `bitbucket`).
