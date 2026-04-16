# MCP Server Configurations

Pre-configured MCP server definitions for popular services. Install into any supported agent with the install script.

## Included Servers


| Server         | Service              | Required Env Vars                                               |
| -------------- | -------------------- | --------------------------------------------------------------- |
| `github`       | GitHub API           | `GITHUB_PAT`                                                    |
| `bitbucket`    | Bitbucket API        | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN`                         |
| `confluence`   | Atlassian Confluence | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| `jira`         | Atlassian Jira       | `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`                   |
| `google-drive` | Google Drive         | OAuth credentials (see server config)                           |
| `brainstorming` | Local brainstorming workflow | `BRAINSTORMING_MCP_ROOT` pointing to a local `mcp-brainstorming` checkout |


## Installation

```bash
# Install all MCP configs for Claude Code
./scripts/install-mcp.sh --agent claude-code

# Install specific servers for Cursor
./scripts/install-mcp.sh --agent cursor --servers github,bitbucket

# Install for multiple agents
./scripts/install-mcp.sh --agent claude-code,cursor,claude-desktop
```

## Per-Agent Config Paths


| Agent          | Config Path                                                               |
| -------------- | ------------------------------------------------------------------------- |
| Claude Code    | `~/.claude/mcp.json`                                                      |
| Cursor         | `.cursor/mcp.json` (project-level)                                        |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) |
| Codex          | `~/.codex/mcp.json`                                                       |


## Adding a New Server

1. Create a JSON file in `servers/` with the server definition
2. The file name becomes the server key (e.g., `slack.json` -> `"slack": {...}`)
3. Run `./scripts/install-mcp.sh` to deploy

## Brainstorming MCP

The brainstorming server is intentionally portable and does not hardcode any machine-specific checkout path.

```bash
export BRAINSTORMING_MCP_ROOT="$HOME/path/to/mcp-brainstorming"
./scripts/install-mcp.sh --agent cursor --servers brainstorming
```

If the environment variable is missing, the installed config fails with a clear message. ADK skills still fall back to the shared manual brainstorming workflow when that server is unavailable.

