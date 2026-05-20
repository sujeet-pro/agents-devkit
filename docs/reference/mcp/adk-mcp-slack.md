---
title: 'adk-mcp-slack'
description: 'Optional Slack MCP — npm slack-mcp-server (korotovsky/slack-mcp-server). A python3 wrapper reads ~/.config/creds/slack/slack.token.json (override path via $SLACK_CREDENTIALS_FILE) and passes bot_token →...'
mcp: 'adk-mcp-slack'
source: 'mcp/adk-mcp-slack.json'
group: 'mcp'
order: 3008
---
# adk-mcp-slack

Optional Slack MCP — npm slack-mcp-server (korotovsky/slack-mcp-server). A python3 wrapper reads ~/.config/creds/slack/slack.token.json (override path via $SLACK_CREDENTIALS_FILE) and passes bot_token → SLACK_MCP_XOXB_TOKEN and user_token → SLACK_MCP_XOXP_TOKEN before exec-ing the server. Accepts both the curated {bot_token, user_token} shape written by creds_login_slack AND the raw Slack oauth.v2.access response shape ({access_token, authed_user.access_token}). Mint the token with `creds_login_slack` (mac-setup); scopes requested during OAuth come from ~/.config/creds/slack/app.json. If the token file is missing or has no usable token, the MCP shows as not-connected and Slack-touching skills degrade per shared/constitution.md §VI. Posting requires bot_token. See SETUP.md.

## Source

`mcp/adk-mcp-slack.json`

## Environment variables referenced

_(none)_

## Configuration

```json
{
  "name": "adk-mcp-slack",
  "command": "python3",
  "args": [
    "-c",
    "import json, os, sys\np = os.environ.get('SLACK_CREDENTIALS_FILE') or os.path.expanduser('~/.config/creds/slack/slack.token.json')\nenv = os.environ.copy()\ntry:\n    with open(p) as f:\n        d = json.load(f)\n    # Accept curated shape {bot_token, user_token, ...} OR raw Slack oauth.v2.access\n    # response {access_token (bot), authed_user: {access_token (user), ...}, ...}.\n    bot = d.get('bot_token') or d.get('access_token')\n    user = d.get('user_token') or ((d.get('authed_user') or {}).get('access_token'))\n    if bot: env['SLACK_MCP_XOXB_TOKEN'] = bot\n    if user: env['SLACK_MCP_XOXP_TOKEN'] = user\n    if not bot and not user:\n        sys.stderr.write(f'adk-mcp-slack: no bot_token or user_token in {p}\\n')\nexcept FileNotFoundError:\n    sys.stderr.write(f'adk-mcp-slack: token file not found at {p} \\u2014 run creds_login_slack first\\n')\nexcept Exception as e:\n    sys.stderr.write(f'adk-mcp-slack: failed to read {p}: {e}\\n')\nos.execvpe('npx', ['npx', '-y', 'slack-mcp-server@latest'], env)"
  ],
  "env": {
    "SLACK_MCP_ADD_MESSAGE_TOOL": "true"
  },
  "description": "Optional Slack MCP — npm slack-mcp-server (korotovsky/slack-mcp-server). A python3 wrapper reads ~/.config/creds/slack/slack.token.json (override path via $SLACK_CREDENTIALS_FILE) and passes bot_token → SLACK_MCP_XOXB_TOKEN and user_token → SLACK_MCP_XOXP_TOKEN before exec-ing the server. Accepts both the curated {bot_token, user_token} shape written by creds_login_slack AND the raw Slack oauth.v2.access response shape ({access_token, authed_user.access_token}). Mint the token with `creds_login_slack` (mac-setup); scopes requested during OAuth come from ~/.config/creds/slack/app.json. If the token file is missing or has no usable token, the MCP shows as not-connected and Slack-touching skills degrade per shared/constitution.md §VI. Posting requires bot_token. See SETUP.md."
}
```
