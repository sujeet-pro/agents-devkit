---
title: 'mcp-slack'
description: 'Slack MCP.'
artifact_kind: mcp
---

# mcp-slack

Slack MCP. Requires SLACK_BOT_TOKEN (xoxb-...) and SLACK_TEAM_ID env vars.

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

Set these in `~/.zshenv` before running `bin/adk-mcp-install`.

## Source

`.mcp.json` (entry: `slack`).
