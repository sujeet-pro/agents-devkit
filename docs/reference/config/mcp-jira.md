---
title: 'mcp-jira'
description: 'Jira MCP.'
artifact_kind: mcp
---

# mcp-jira

Jira MCP. Requires ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, JIRA_BASE_URL env vars.

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
  "jira": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-e",
      "ATLASSIAN_EMAIL",
      "-e",
      "ATLASSIAN_API_TOKEN",
      "-e",
      "JIRA_BASE_URL",
      "ghcr.io/atlassian-mcp/jira-mcp-server"
    ],
    "env": {
      "ATLASSIAN_EMAIL": "${ATLASSIAN_EMAIL}",
      "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}",
      "JIRA_BASE_URL": "${JIRA_BASE_URL}"
    },
    "description": "Jira MCP. Requires ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, JIRA_BASE_URL env vars."
  }
}
```

## Required environment variables

- `ATLASSIAN_EMAIL`
- `ATLASSIAN_API_TOKEN`
- `JIRA_BASE_URL`

Set these in `~/.zshenv` before running `bin/adk-mcp-install`.

## Source

`.mcp.json` (entry: `jira`).
