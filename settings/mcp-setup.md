# MCP Server Setup Guide

## Overview

claude-devkit requires three locally-configured MCP servers and optionally uses Claude.ai built-in integrations.

| MCP Server | Package | Auth Method | Required? |
|---|---|---|---|
| atlassian-confluence | `mcp-atlassian` (PyPI) | API Token | Yes |
| bitbucket | `bitbucket-mcp` (npm) | App Password | Yes |
| google-drive | `@piotr-agier/google-drive-mcp` (npm) | OAuth (browser) | Yes |
| Slack | Claude.ai built-in | OAuth (browser) | Optional |
| Gmail | Claude.ai built-in | OAuth (browser) | Optional |
| Google Calendar | Claude.ai built-in | OAuth (browser) | Optional |

## Atlassian Confluence MCP

### Setup
1. Generate an Atlassian API token at https://id.atlassian.com/manage-profile/security/api-tokens
2. Add to `~/.zshenv`:
   ```bash
   export CONFLUENCE_API_TOKEN="your-token"
   export CONFLUENCE_BASE_URL="https://yoursite.atlassian.net/wiki"
   export CONFLUENCE_EMAIL="your-email@example.com"
   ```
3. Add MCP server to `~/.claude.json` under `mcpServers`:
   ```json
   "atlassian-confluence": {
     "command": "uvx",
     "args": ["mcp-atlassian", "--confluence-url", "$CONFLUENCE_BASE_URL", "--confluence-username", "$CONFLUENCE_EMAIL", "--confluence-token", "$CONFLUENCE_API_TOKEN"],
     "env": {
       "CONFLUENCE_URL": "$CONFLUENCE_BASE_URL",
       "CONFLUENCE_USERNAME": "$CONFLUENCE_EMAIL",
       "CONFLUENCE_API_TOKEN": "$CONFLUENCE_API_TOKEN"
     }
   }
   ```

   Note: Replace `$VARIABLE` with actual values, or use the shell wrapper pattern shown in the Bitbucket section.

### Alternative: Browser-based OAuth
The `mcp-atlassian` package also supports OAuth. See: https://github.com/sooperset/mcp-atlassian

## Bitbucket MCP

### Setup
1. Create a Bitbucket App Password at https://bitbucket.org/account/settings/app-passwords/
   - Required permissions: Repositories (Read), Pull Requests (Read, Write)
2. Add to `~/.zshenv`:
   ```bash
   export BITBUCKET_TOKEN="your-app-password"
   ```
3. Add MCP server to `~/.claude.json`:
   ```json
   "bitbucket": {
     "command": "sh",
     "args": ["-c", "BITBUCKET_USERNAME=your-email BITBUCKET_PASSWORD=$BITBUCKET_TOKEN npx -y bitbucket-mcp@latest"],
     "env": {
       "BITBUCKET_TOKEN": "$BITBUCKET_TOKEN"
     }
   }
   ```

## Google Drive MCP (Docs, Sheets, Slides, Drive, Calendar)

### Setup (OAuth — browser-based, no env vars needed)
1. Create a Google Cloud project and OAuth 2.0 credentials:
   - Go to https://console.cloud.google.com/apis/credentials
   - Create OAuth 2.0 Client ID (Desktop app type)
   - Download credentials JSON
2. Save credentials to `~/.config/google-drive-mcp/gcp-oauth.keys.json`
3. Add MCP server to `~/.claude.json`:
   ```json
   "google-drive": {
     "command": "npx",
     "args": ["-y", "@piotr-agier/google-drive-mcp"],
     "env": {}
   }
   ```
4. First run will open a browser for Google OAuth consent
5. Tokens are saved to `~/.config/google-drive-mcp/tokens.json` and auto-refreshed

### Re-authentication
If tokens expire, delete `~/.config/google-drive-mcp/tokens.json` and restart Claude Code.

## Claude.ai Built-in Integrations (Slack, Gmail, Calendar)

These are remote MCP servers managed by Claude.ai. No local configuration needed.

### Setup
1. Open Claude Desktop
2. Go to Settings → Integrations
3. Click "Connect" for each service (Slack, Gmail, Google Calendar)
4. Complete the OAuth flow in your browser
5. The integrations are now available in both Claude Desktop and Claude Code

### Re-authentication
If a service needs re-auth, Claude will prompt you. You can also check `~/.claude/mcp-needs-auth-cache.json` for services flagged for re-auth.

## Validating Setup

After configuration:
1. Run `zsh scripts/validate-mcp.zsh` to check MCP server entries exist
2. Use the `/validate-mcp` skill in Claude Code to test actual connectivity
3. The skill will attempt to read a sample resource from each MCP server
