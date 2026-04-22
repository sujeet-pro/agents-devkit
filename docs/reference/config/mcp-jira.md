---
title: 'mcp-jira'
description: 'Jira MCP. Requires ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, JIRA_BASE_URL env vars.'
artifact_kind: mcp
---

# mcp-jira

Jira MCP. Requires ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, JIRA_BASE_URL env vars.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

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

- `ATLASSIAN_API_TOKEN`
- `ATLASSIAN_EMAIL`
- `JIRA_BASE_URL`

Set these in `~/.zshenv` (or your shell's env file) so they are present when Claude Code launches the plugin.

## Source

`.mcp.json` (entry: `jira`).
