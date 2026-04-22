---
title: 'mcp-github'
description: 'GitHub MCP via Docker.'
artifact_kind: mcp
---

# mcp-github

GitHub MCP via Docker. Falls back to gh CLI if not enabled. Requires GITHUB_PAT env var (typically in ~/.zshenv).

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
  "github": {
    "command": "sh",
    "args": [
      "-c",
      "GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PAT docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server"
    ],
    "env": {
      "GITHUB_PAT": "${GITHUB_PAT}"
    },
    "description": "GitHub MCP via Docker. Falls back to gh CLI if not enabled. Requires GITHUB_PAT env var (typically in ~/.zshenv)."
  }
}
```

## Required environment variables

- `GITHUB_PAT`

Set these in `~/.zshenv` before running `bin/adk-mcp-install`.

## Source

`.mcp.json` (entry: `github`).
