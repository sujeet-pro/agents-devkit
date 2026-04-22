---
title: 'mcp-slack'
description: 'Slack MCP. Requires SLACK_BOT_TOKEN (xoxb-...) and SLACK_TEAM_ID env vars.'
artifact_kind: mcp
---

# mcp-slack

Slack MCP. Requires SLACK_BOT_TOKEN (xoxb-...) and SLACK_TEAM_ID env vars.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "slack": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-slack"
    ],
    "env": {
      "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
      "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
    },
    "description": "Slack MCP. Requires SLACK_BOT_TOKEN (xoxb-...) and SLACK_TEAM_ID env vars."
  }
}
```

## Required environment variables

- `SLACK_BOT_TOKEN`
- `SLACK_TEAM_ID`

Set these in `~/.zshenv` (or your shell's env file) so they are present when Claude Code launches the plugin.

## Source

`.mcp.json` (entry: `slack`).
