---
title: 'adk-mcp-google'
description: 'Optional Google Workspace MCP — taylorwilsdon/google_workspace_mcp via uvx (PyPI: workspace-mcp). Surface: Drive, Docs, Sheets, Slides, Calendar, Gmail, Forms, Chat, Tasks. The server reads GOOGLE_OAUTH_CLIENT_ID +...'
mcp: 'adk-mcp-google'
source: 'mcp/adk-mcp-google.json'
group: 'mcp'
order: 3004
---
# adk-mcp-google

Optional Google Workspace MCP — taylorwilsdon/google_workspace_mcp via uvx (PyPI: workspace-mcp). Surface: Drive, Docs, Sheets, Slides, Calendar, Gmail, Forms, Chat, Tasks. The server reads GOOGLE_OAUTH_CLIENT_ID + GOOGLE_OAUTH_CLIENT_SECRET + WORKSPACE_MCP_CREDENTIALS_DIR natively — we map those into the subprocess from our `_CRED` / GOOGLE_* canonical names. NOTE: the server runs its OWN OAuth dance — on first tool invocation a browser opens and you authorize. Tokens are stored at $GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR. This is SEPARATE from ~/.config/creds/google/google.token.json — the standalone `creds login google` flow stays useful for `creds validate` and other mac-setup scripts, but the MCP server does not consume it. The scope list the server requests is fixed by the server version (configurable via `--tool-tier`); make sure your GCP OAuth consent screen includes the scopes listed in ~/.config/creds/google/app.json. See SETUP.md.

## Source

`mcp/adk-mcp-google.json`

## Environment variables referenced

- `GOOGLE_CLIENT_ID_CRED`
- `GOOGLE_CLIENT_SECRET_CRED`
- `GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR`
- `USER_GOOGLE_EMAIL`

## Configuration

```json
{
  "name": "adk-mcp-google",
  "command": "uvx",
  "args": [
    "workspace-mcp@latest"
  ],
  "env": {
    "GOOGLE_OAUTH_CLIENT_ID": "${GOOGLE_CLIENT_ID_CRED}",
    "GOOGLE_OAUTH_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET_CRED}",
    "USER_GOOGLE_EMAIL": "${USER_GOOGLE_EMAIL:-}",
    "WORKSPACE_MCP_CREDENTIALS_DIR": "${GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR}"
  },
  "description": "Optional Google Workspace MCP — taylorwilsdon/google_workspace_mcp via uvx (PyPI: workspace-mcp). Surface: Drive, Docs, Sheets, Slides, Calendar, Gmail, Forms, Chat, Tasks. The server reads GOOGLE_OAUTH_CLIENT_ID + GOOGLE_OAUTH_CLIENT_SECRET + WORKSPACE_MCP_CREDENTIALS_DIR natively — we map those into the subprocess from our `_CRED` / GOOGLE_* canonical names. NOTE: the server runs its OWN OAuth dance — on first tool invocation a browser opens and you authorize. Tokens are stored at $GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR. This is SEPARATE from ~/.config/creds/google/google.token.json — the standalone `creds login google` flow stays useful for `creds validate` and other mac-setup scripts, but the MCP server does not consume it. The scope list the server requests is fixed by the server version (configurable via `--tool-tier`); make sure your GCP OAuth consent screen includes the scopes listed in ~/.config/creds/google/app.json. See SETUP.md."
}
```
