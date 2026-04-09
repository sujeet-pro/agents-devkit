# Stage: MCP Server Setup & Validation

This stage idempotently configures, validates, and updates MCP servers used by DevKit skills. It supports multiple AI tools and writes to the correct user-level config path for each.

## IDE / Tool Config Paths

| Tool | User-level config path | Config key |
|---|---|---|
| Claude Code | `~/.claude.json` | `mcpServers` |
| Cursor | `~/.cursor/mcp.json` | `mcpServers` |
| Windsurf | `~/.windsurf/mcp.json` | `mcpServers` |
| Codex | `~/.codex/mcp.json` | `mcpServers` |

The script auto-detects the current tool when possible (via env vars like `CLAUDE_CODE`, `CURSOR_SESSION`, etc.). If detection fails, it prompts the user to specify `--ide <tool>`. Use `--ide all` to configure every detected tool at once.

## Per-Server Steps

1. **Check** — Is the server configured in the target tool's config?
2. **Configure** — If not, add the config using tokens from `~/.zshenv`
3. **Update packages** — Pull latest Docker images, npm packages, or Python packages
4. **Sync tokens** — Compare `~/.zshenv` values against config; update if they differ

## Execution

Run the setup script:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/setup-mcps.sh <args>
```

Where `<args>` are the arguments passed to this skill (e.g. `--check-only`, `--server github`, `--ide cursor`).

## Supported Servers

| Server | Key in config | Transport | Env vars from `~/.zshenv` |
|---|---|---|---|
| GitHub | `github` | stdio | `GITHUB_PAT` (mapped to `GITHUB_PERSONAL_ACCESS_TOKEN` for Docker) |
| Bitbucket | `bitbucket` | stdio | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| Confluence | `atlassian-confluence` | stdio | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Atlassian | `atlassian` | HTTP | — none — (OAuth, browser-based) |
| Google Drive | `google-drive` | stdio | `GOOGLE_DRIVE_OAUTH_CREDENTIALS` |

All stdio servers use `zsh -c` wrappers to auto-source `~/.zshenv`, ensuring env vars are available regardless of how the IDE was launched.

## Post-Setup Validation

After the script completes, report the results to the user. If any servers were skipped due to missing env vars, list what needs to be added to `~/.zshenv`.

If the script exits with code 2 and outputs `PROMPT_USER:` lines, the agent should read the message and ask the user which IDE to target, then re-run with `--ide <chosen>`.

If the user asks to validate a specific skill's MCP dependencies, run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py <skill-dir>
```
