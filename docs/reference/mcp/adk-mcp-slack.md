---
title: 'adk-mcp-slack'
description: 'Optional Slack MCP — npm slack-mcp-server (korotovsky/slack-mcp-server). Wrapper sources $SLACK_CREDENTIALS_FILE (expected to export SLACK_BOT_TOKEN and/or SLACK_USER_TOKEN), then launches the server. If neither...'
mcp: 'adk-mcp-slack'
source: 'mcp/adk-mcp-slack.json'
group: 'mcp'
order: 3006
---
# adk-mcp-slack

Optional Slack MCP — npm slack-mcp-server (korotovsky/slack-mcp-server). Wrapper sources $SLACK_CREDENTIALS_FILE (expected to export SLACK_BOT_TOKEN and/or SLACK_USER_TOKEN), then launches the server. If neither token resolves, the MCP shows as not-connected and Slack-touching skills degrade per shared/constitution.md §VI. Posting messages requires SLACK_BOT_TOKEN with chat:write. See SETUP.md.

## Source

`mcp/adk-mcp-slack.json`

## Environment variables referenced

- `SLACK_BOT_TOKEN`
- `SLACK_USER_TOKEN`

## Configuration

```json
{
  "name": "adk-mcp-slack",
  "command": "sh",
  "args": [
    "-c",
    "if [ -n \"$SLACK_CREDENTIALS_FILE\" ] && [ -r \"$SLACK_CREDENTIALS_FILE\" ]; then . \"$SLACK_CREDENTIALS_FILE\"; fi; exec npx -y slack-mcp-server@latest"
  ],
  "env": {
    "SLACK_MCP_XOXP_TOKEN": "${SLACK_USER_TOKEN:-}",
    "SLACK_MCP_XOXB_TOKEN": "${SLACK_BOT_TOKEN:-}",
    "SLACK_MCP_ADD_MESSAGE_TOOL": "true"
  },
  "description": "Optional Slack MCP — npm slack-mcp-server (korotovsky/slack-mcp-server). Wrapper sources $SLACK_CREDENTIALS_FILE (expected to export SLACK_BOT_TOKEN and/or SLACK_USER_TOKEN), then launches the server. If neither token resolves, the MCP shows as not-connected and Slack-touching skills degrade per shared/constitution.md §VI. Posting messages requires SLACK_BOT_TOKEN with chat:write. See SETUP.md."
}
```
