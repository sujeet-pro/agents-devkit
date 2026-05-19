# mcp/ — MCP server configs

Each `adk-mcp-*.json` is a single, env-var-driven config. **No tokens stored**; every secret comes from your shell's environment.

`install.sh` translates each file into the right shape per agent:

- Claude Code: merged into `~/.claude/settings.json` `mcpServers` block.
- Cursor: merged into `~/.cursor/mcp.json`.
- Codex CLI: appended as `[[mcp_servers]]` blocks in `~/.codex/config.toml`.
- Junie: where MCP is supported, configured per IDE; otherwise not installed.

## Catalog

| MCP | Status | Env vars consumed | Skills that use it |
|---|---|---|---|
| `adk-mcp-github` | required for code skills | `GITHUB_TOKEN_CRED` | `/adk-implement`, `/adk-review`, `/adk-sync` |
| `adk-mcp-datadog` | required for investigate | `DATADOG_API_KEY_CRED`, `DATADOG_APP_KEY_CRED`, `DD_SITE` | `/adk-investigate` |
| `adk-mcp-statsig` | required for investigate | `STATSIG_CONSOLE_API_KEY_CRED` | `/adk-investigate` |
| `adk-mcp-atlassian` | required for docs / Jira | `ATLASSIAN_SITE`, `ATLASSIAN_USERNAME`, `ATLASSIAN_API_TOKEN_CRED` | `/adk-implement` (Jira context), `/adk-document`, `/adk-sync` |
| `adk-mcp-mixpanel` | optional | none (OAuth) | `/adk-investigate` (product-analytics sub-flow) |
| `adk-mcp-slack` | optional | `SLACK_CREDENTIALS_FILE` → sources `SLACK_BOT_TOKEN`/`SLACK_USER_TOKEN` | `/adk-investigate` (incident / RCA), `/adk-sync` (post) |
| `adk-mcp-snowflake` | optional | `SNOWFLAKE_*` (see config) | `/adk-investigate` (data sub-flow) |
| `adk-mcp-looker` | optional | `LOOKER_*` (see config) | `/adk-investigate` (data sub-flow) |
| `adk-mcp-rag` | optional | `RAG_MCP_URL`, `RAG_MCP_TOKEN_CRED` | All skills (auto-merge into context-gather when enabled) |

## Required vs optional

- **Required** MCPs must be reachable for the consuming skill to proceed. Skills stop in Phase 1 with a named gap if not.
- **Optional** MCPs degrade gracefully: skills mark `[<mcp>: skipped]` in `context.md` and report the gap in the final summary.

## Read-only by default

Per `shared/constitution.md`:
- Datadog: never modify monitors / dashboards / alerts.
- Statsig: never toggle gates / start experiments.
- Snowflake: never DML/DDL/GRANT.
- Looker: read-only.
- GitHub / Atlassian / Slack: writes require explicit per-invocation user confirmation.

## Adding a new MCP

1. Drop `adk-mcp-<name>.json` here.
2. Add a row to the catalog table above.
3. If used by a skill, add `needs_mcp: [adk-mcp-<name>]` to that skill's `SKILL.md` frontmatter.
4. Re-run `./install.sh --target <agent>` (or `--target all`).

## Verifiers

See `SETUP.md §6` for the per-MCP smoke-test curl commands.
