# MCP Server Registry

All MCP servers that DevKit skills depend on. Each entry defines the server name, config shape, required env vars, and how to install/update.

## GitHub MCP

- **Server name**: `github`
- **Package**: `github/github-mcp-server` (Docker image: `ghcr.io/github/github-mcp-server`)
- **Env vars** (from `~/.zshenv`):
  - `GITHUB_PAT` — GitHub Personal Access Token
- **Config** (`~/.claude.json` → `mcpServers.github`):
  ```json
  {
    "command": "docker",
    "args": [
      "run", "-i", "--rm",
      "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
      "ghcr.io/github/github-mcp-server"
    ],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}"
    }
  }
  ```
- **Update**: `docker pull ghcr.io/github/github-mcp-server`

### GitHub MCP — HTTP variant (preferred when supported)

```json
{
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/"
}
```

No env vars needed for the HTTP variant. Prefer this when the host supports HTTP MCP.

## Bitbucket MCP

- **Server name**: `bitbucket`
- **Package**: `bitbucket-mcp` (npx)
- **Env vars** (from `~/.zshenv`):
  - `BITBUCKET_USERNAME` — Bitbucket email
  - `BITBUCKET_TOKEN` — Bitbucket app password
- **Config** (`~/.claude.json` → `mcpServers.bitbucket`):
  ```json
  {
    "command": "sh",
    "args": [
      "-c",
      "BITBUCKET_USERNAME=${BITBUCKET_USERNAME} BITBUCKET_PASSWORD=${BITBUCKET_TOKEN} npx -y bitbucket-mcp@latest"
    ],
    "env": {
      "BITBUCKET_USERNAME": "${BITBUCKET_USERNAME}",
      "BITBUCKET_TOKEN": "${BITBUCKET_TOKEN}"
    }
  }
  ```
- **Update**: Automatic — `npx -y bitbucket-mcp@latest` always pulls latest

## Atlassian Confluence MCP

- **Server name**: `atlassian-confluence`
- **Package**: `mcp-atlassian` (uvx)
- **Env vars** (from `~/.zshenv`):
  - `CONFLUENCE_URL` — e.g. `https://yoursite.atlassian.net/wiki`
  - `CONFLUENCE_USERNAME` — Atlassian email
  - `CONFLUENCE_API_TOKEN` — Atlassian API token
- **Config** (`~/.claude.json` → `mcpServers.atlassian-confluence`):
  ```json
  {
    "command": "uvx",
    "args": [
      "mcp-atlassian",
      "--confluence-url", "${CONFLUENCE_URL}",
      "--confluence-username", "${CONFLUENCE_USERNAME}",
      "--confluence-token", "${CONFLUENCE_API_TOKEN}"
    ],
    "env": {
      "CONFLUENCE_URL": "${CONFLUENCE_URL}",
      "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
      "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}"
    }
  }
  ```
- **Update**: `uvx upgrade mcp-atlassian` or `pip install --upgrade mcp-atlassian`

## Google Drive MCP

- **Server name**: `google-drive`
- **Package**: `@piotr-agier/google-drive-mcp` (npx)
- **Env vars** (from `~/.zshenv`):
  - `GOOGLE_MCP_CLIENT_ID` — Google OAuth client ID
  - `GOOGLE_MCP_CLIENT_SECRET` — Google OAuth client secret
  - `GOOGLE_DRIVE_OAUTH_CREDENTIALS` — path to OAuth credentials JSON (default: `~/.config/google-drive-mcp/gcp-oauth.keys.json`)
- **Config** (`~/.claude.json` → `mcpServers.google-drive`):
  ```json
  {
    "command": "npx",
    "args": ["-y", "@piotr-agier/google-drive-mcp"],
    "env": {}
  }
  ```
- **Update**: `npm cache clean --force && npx -y @piotr-agier/google-drive-mcp` (npx caches, so clearing forces update)
- **Note**: Requires one-time browser OAuth flow on first run. Credentials file must exist at the configured path.
