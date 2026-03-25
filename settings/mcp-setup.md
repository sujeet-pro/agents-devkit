# MCP Server Setup Guide

AKIT's core workflows rely on four MCP integrations:

| MCP Server | Package or Image | Auth | Typical Use |
|---|---|---|---|
| GitHub | `github/github-mcp-server` | GitHub PAT | GitHub PR review and PR descriptions |
| Bitbucket | `bitbucket-mcp` | App password | Bitbucket PR review and PR descriptions |
| Atlassian Confluence | `mcp-atlassian` | API token | Confluence doc review and publishing |
| Google Drive | `@piotr-agier/google-drive-mcp` | OAuth | Google Docs review and publishing |

## GitHub MCP

GitHub now maintains an official MCP server.

For hosts that support remote MCP servers, the official hosted endpoint is the easiest path:

```json
"github": {
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/"
}
```

If your host requires a local `stdio` server, use the official local server.

1. Create a GitHub Personal Access Token with the scopes you need.
2. Add it to `~/.zshenv`:

   ```bash
   export GITHUB_PERSONAL_ACCESS_TOKEN="your-token"
   ```

3. Add a server entry to `~/.claude.json`:

   ```json
   "github": {
     "command": "docker",
     "args": [
       "run",
       "-i",
       "--rm",
       "-e",
       "GITHUB_PERSONAL_ACCESS_TOKEN",
       "ghcr.io/github/github-mcp-server"
     ],
     "env": {
       "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_PERSONAL_ACCESS_TOKEN"
     }
   }
   ```

If you do not use Docker, build the server from the official repository and run the binary with `stdio`.

## Bitbucket MCP

1. Create a Bitbucket app password with repository and pull-request access.
2. Add it to `~/.zshenv`:

   ```bash
   export BITBUCKET_TOKEN="your-app-password"
   ```

3. Add a server entry to `~/.claude.json`:

   ```json
   "bitbucket": {
     "command": "sh",
     "args": [
       "-c",
       "BITBUCKET_USERNAME=your-email BITBUCKET_PASSWORD=$BITBUCKET_TOKEN npx -y bitbucket-mcp@latest"
     ],
     "env": {
       "BITBUCKET_TOKEN": "$BITBUCKET_TOKEN"
     }
   }
   ```

## Atlassian Confluence MCP

1. Create an Atlassian API token.
2. Add the variables to `~/.zshenv`:

   ```bash
   export CONFLUENCE_BASE_URL="https://yoursite.atlassian.net/wiki"
   export CONFLUENCE_EMAIL="your-email@example.com"
   export CONFLUENCE_API_TOKEN="your-token"
   ```

3. Add a server entry to `~/.claude.json`:

   ```json
   "atlassian-confluence": {
     "command": "uvx",
     "args": [
       "mcp-atlassian",
       "--confluence-url",
       "$CONFLUENCE_BASE_URL",
       "--confluence-username",
       "$CONFLUENCE_EMAIL",
       "--confluence-token",
       "$CONFLUENCE_API_TOKEN"
     ],
     "env": {
       "CONFLUENCE_URL": "$CONFLUENCE_BASE_URL",
       "CONFLUENCE_USERNAME": "$CONFLUENCE_EMAIL",
       "CONFLUENCE_API_TOKEN": "$CONFLUENCE_API_TOKEN"
     }
   }
   ```

## Google Drive MCP

1. Create Google OAuth desktop credentials.
2. Save the credentials file to `~/.config/google-drive-mcp/gcp-oauth.keys.json`.
3. Add a server entry to `~/.claude.json`:

   ```json
   "google-drive": {
     "command": "npx",
     "args": ["-y", "@piotr-agier/google-drive-mcp"],
     "env": {}
   }
   ```

4. Complete the browser OAuth flow on first run.

## Validation

After configuration:

```bash
zsh scripts/check-env.zsh
zsh scripts/validate-mcp.zsh
zsh scripts/check-skill-deps.zsh review-pr pr=https://github.com/org/repo/pull/42
zsh scripts/check-skill-deps.zsh review-doc source=https://docs.google.com/document/d/123/edit
```

Inside AKIT-enabled hosts, use `/manage-validate` for a workflow-oriented check.
