# MCP Server Setup Guide

DevKit skills that interact with external sources use MCP (Model Context Protocol) servers:

| MCP Server           | Package or Image                | Auth         | Typical Use                             |
| -------------------- | ------------------------------- | ------------ | --------------------------------------- |
| GitHub               | `github/github-mcp-server`      | GitHub PAT   | GitHub PR review and PR descriptions    |
| Bitbucket            | `bitbucket-mcp`                 | App password | Bitbucket PR review and PR descriptions |
| Atlassian Confluence | `mcp-atlassian`                 | API token    | Confluence doc review and publishing    |
| Google Drive         | `@piotr-agier/google-drive-mcp` | OAuth        | Google Docs review and publishing       |

## Where to Configure

Each agent stores MCP servers in a different file. Store secrets in `~/.zshenv` and reference them from the config file.

| Agent | User-Scope Config File | Project-Scope Config File | Format | Env Var Expansion |
|-------|------------------------|---------------------------|--------|-------------------|
| **Claude Code** | `~/.claude.json` | `.mcp.json` | JSON | `${VAR}` syntax |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) | — | JSON | No (literal values only) |
| **OpenAI Codex** | `~/.codex/config.toml` | `.codex/config.toml` | TOML | `env_vars = ["VAR"]` (by name) |
| **Cursor** | `~/.cursor/mcp.json` | `.cursor/mcp.json` | JSON | `${VAR}` syntax |
| **VS Code (Copilot)** | VS Code user settings | `.vscode/mcp.json` | JSON | `${VAR}` syntax |

> **No universal standard.** The MCP specification defines the wire protocol, not config file locations. Each agent uses its own path and format. There is an [open proposal](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2218) for a standard, but it has not been adopted.

All JSON-based agents (Claude Code, Cursor, VS Code) share the same schema — `mcpServers` as root key with `command`, `args`, `env` per server. You can often copy config between them. Codex is the outlier using TOML.

## GitHub MCP

GitHub maintains an official MCP server. The official hosted endpoint is the easiest path:

```json
"github": {
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/"
}
```

If your host requires a local `stdio` server:

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
       "run", "-i", "--rm",
       "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
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
       "--confluence-url", "$CONFLUENCE_BASE_URL",
       "--confluence-username", "$CONFLUENCE_EMAIL",
       "--confluence-token", "$CONFLUENCE_API_TOKEN"
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

## Claude Desktop

Claude Desktop does **not** support environment variable expansion. Paste literal token values directly. Edit `~/Library/Application Support/Claude/claude_desktop_config.json` and restart the app.

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

## OpenAI Codex

Edit `~/.codex/config.toml`. Use `env_vars` to forward shell variables by name (reads from `~/.zshenv`).

```toml
[mcp_servers.github]
type = "http"
url = "https://api.githubcopilot.com/mcp/"

[mcp_servers.bitbucket]
command = "npx"
args = ["-y", "bitbucket-mcp@latest"]
env_vars = ["BITBUCKET_USERNAME", "BITBUCKET_TOKEN"]

[mcp_servers.atlassian-confluence]
command = "uvx"
args = ["--with", "fakeredis<2.35", "mcp-atlassian", "--confluence-url", "", "--confluence-username", "", "--confluence-token", ""]
env_vars = ["CONFLUENCE_URL", "CONFLUENCE_USERNAME", "CONFLUENCE_API_TOKEN"]
```

CLI: `codex mcp add`, `codex mcp list`, `codex mcp remove`.

## Cursor (Manual)

Edit `~/.cursor/mcp.json` (user-scope) or `.cursor/mcp.json` (project-scope). Supports `${VAR}` expansion.

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "bitbucket": {
      "command": "npx",
      "args": ["-y", "bitbucket-mcp@latest"],
      "env": {
        "BITBUCKET_USERNAME": "${BITBUCKET_USERNAME}",
        "BITBUCKET_PASSWORD": "${BITBUCKET_TOKEN}"
      }
    }
  }
}
```

## Secrets in `~/.zshenv`

All MCP servers read tokens from environment variables. Store them in `~/.zshenv` so they are available to every shell session and every agent that spawns stdio servers:

```bash
# GitHub
export GITHUB_PAT="ghp_your_token"

# Bitbucket
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_TOKEN="your-app-password"

# Confluence
export CONFLUENCE_URL="https://your-company.atlassian.net"
export CONFLUENCE_USERNAME="your-email@company.com"
export CONFLUENCE_API_TOKEN="your-api-token"

# Google Drive (OAuth credentials file path)
export GOOGLE_DRIVE_OAUTH_CREDENTIALS="$HOME/.config/google-drive-mcp/gcp-oauth.keys.json"
```

After editing, run `source ~/.zshenv` or open a new terminal.

## Validation

After configuration, validate from within a skill by running:

```bash
python3 skills/<skill-name>/scripts/preflight.py skills/<skill-name> pr=https://github.com/org/repo/pull/42
```

Each skill ships `scripts/preflight.py` (kept in sync from `templates/skill/scripts/preflight.py`) and uses it to check MCP and CLI dependencies before starting work.