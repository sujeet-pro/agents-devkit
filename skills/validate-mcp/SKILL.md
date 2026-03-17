---
name: validate-mcp
description: Validate all MCP server connections and help with OAuth login flows
user_invocable: true
arguments:
  - name: server
    description: "Specific server to validate: confluence, bitbucket, google-drive, slack, gmail, calendar, all (default: all)"
    required: false
---

# MCP Connection Validator

This skill tests all MCP server connections and helps with OAuth login if needed.

If the `--server` argument is provided, only validate that specific server. Otherwise, validate all servers.

## Phase 1: Check MCP Server Availability

For each MCP server, attempt a lightweight read operation to verify connectivity. Run these checks in parallel where possible.

### Atlassian Confluence

- Try: `mcp__atlassian-confluence__confluence_search` with query `"test"` and limit `1`
- **Success**: report "Confluence MCP connected" with the site URL
- **Failure**: report the error and suggest checking these environment variables in `~/.zshenv`:
  - `CONFLUENCE_API_TOKEN`
  - `CONFLUENCE_BASE_URL`
  - `CONFLUENCE_EMAIL`

### Bitbucket

- Try: `mcp__bitbucket__listRepositories` with limit `1`
- **Success**: report "Bitbucket MCP connected" with the workspace name
- **Failure**: report the error and suggest checking `BITBUCKET_TOKEN` in `~/.zshenv`

### Google Drive

- Try: `mcp__google-drive__search` with query `"test"` (this will trigger OAuth if not authenticated)
- **Success**: report "Google Drive MCP connected"
- **Failure**: If OAuth is needed, instruct the user:
  1. The Google Drive MCP uses browser-based OAuth
  2. Run `npx -y @piotr-agier/google-drive-mcp` manually in terminal to trigger the OAuth flow
  3. Complete the Google sign-in in the browser
  4. Tokens will be saved to `~/.config/google-drive-mcp/tokens.json`
  5. Restart Claude Code after authenticating

### Slack (Claude.ai built-in)

- Try: `mcp__claude_ai_Slack__slack_search_channels` with query `"general"` and limit `1`
- **Success**: report "Slack MCP connected"
- **Failure**: instruct user to connect Slack via Claude Desktop -> Settings -> Integrations

### Gmail (Claude.ai built-in)

- Try: `mcp__claude_ai_Gmail__gmail_get_profile`
- **Success**: report "Gmail MCP connected" with the email address
- **Failure**: instruct user to connect Gmail via Claude Desktop -> Settings -> Integrations

### Google Calendar (Claude.ai built-in)

- Try: `mcp__claude_ai_Google_Calendar__gcal_list_calendars`
- **Success**: report "Google Calendar MCP connected"
- **Failure**: instruct user to connect Calendar via Claude Desktop -> Settings -> Integrations

## Phase 2: Summary

After checking all servers (or the single specified server), print a summary table like this:

```
MCP Server              Status      Auth Type
─────────────────────────────────────────────────
Confluence              ✓ Connected  API Token
Bitbucket               ✓ Connected  App Password
Google Drive            ✓ Connected  OAuth
Slack                   ✗ Not connected  Claude.ai Integration
Gmail                   ✓ Connected  Claude.ai Integration
Google Calendar         ✓ Connected  Claude.ai Integration
```

Use checkmarks for connected servers and crosses for failed ones.

## Phase 3: Help with Failed Connections

For any failed connection, provide specific, actionable steps to fix:

- **Token-based services** (Confluence, Bitbucket): Check if environment variables are set by running `echo $VARIABLE_NAME` in a Bash shell. If unset, explain how to add them to `~/.zshenv` and reload with `source ~/.zshenv`.
- **OAuth-based services** (Google Drive): Offer to help trigger the auth flow. The first connection requires a browser-based OAuth login — there are no env vars to set.
- **Claude.ai integrations** (Slack, Gmail, Calendar): Direct the user to Claude Desktop -> Settings -> Integrations. These authenticate through Claude Desktop, NOT through local configuration.

## Important Notes

- This skill only performs read operations. It never writes, creates, or modifies anything in the external services.
- If `--server` is specified, only validate that specific server and skip all others.
- For Google Drive MCP, the first connection requires a browser-based OAuth login — there are no environment variables to configure.
- For Slack, Gmail, and Calendar, these are Claude.ai built-in integrations that authenticate through Claude Desktop, not through local configuration files or environment variables.
- This skill is safe to run at any time as a connectivity health check.
