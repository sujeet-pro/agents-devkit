---
name: confluence
description: "adk - [helper] [connector] Confluence REST API operations — page CRUD, comments, attachments, and space management"
user-invocable: false
workflow-tier: helper
maturity: stable
dependencies:
  commands: [curl, jq, python3]
allowed-tools: [Read, Bash]
allowed-mcps: [atlassian-confluence]
---

# Confluence

Platform connector for Confluence Cloud. Uses the Confluence REST API v2 (with v1 fallback for attachments) via `curl`.

## Auth

Requires environment variables in `~/.zshenv`:

```bash
export CONFLUENCE_URL="https://your-domain.atlassian.net"
export CONFLUENCE_USERNAME="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-api-token"
```

Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

### Validation

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/auth.sh
```

If auth fails or token is expired:
> Add or update your Confluence credentials in `~/.zshenv`:
> ```bash
> export CONFLUENCE_URL="https://your-domain.atlassian.net"
> export CONFLUENCE_USERNAME="your-email@example.com"
> export CONFLUENCE_API_TOKEN="your-api-token"
> ```
> Then run `source ~/.zshenv` and retry.

## MCP Server Setup

To configure the MCP server for this connector, see `mcp-config.json` in the ADK root directory for the server definition. Copy the relevant entry to your IDE's MCP configuration file (e.g., `~/.claude.json` for Claude Code).

## API-First Approach

Always prefer direct REST API calls (via `curl`) over MCP tools. The bundled scripts under `scripts/` wrap the Confluence REST API and work in any environment (Claude Code, Codex, etc.) without MCP dependencies. If the scripts are not accessible via `${CLAUDE_SKILL_DIR}`, construct `curl` commands directly from the reference docs below — do NOT create new shell scripts.

MCP tools (`mcp__atlassian-confluence__*`, `mcp__plugin-atlassian-atlassian__*`, `mcp__plugin-adk-atlassian__*`, `mcp__atlassian__*`) may be used as a secondary option when available, but fall back to direct API calls for any operation not covered or if MCP fails.

### MCP Connector Limitations

The official Atlassian MCP connector typically supports page read, update, search, and list spaces. Operations that always require direct API calls:

- Upload attachments/images — use `scripts/attachments.sh` or REST API
- Inline comments — use `scripts/comments.sh` or REST API
- Comment replies — use `scripts/comments.sh` or REST API
- Delete pages — use `scripts/pages.sh` or REST API

## Comments

By default, "comments" means **inline comments** — comments anchored to specific text in a page. Use `comments.sh create-inline` with `--text-selection` to anchor a comment to exact text in the page body. Footer (page-level) comments are used only for general page feedback.

## API Base

- v2 API: `${CONFLUENCE_URL}/wiki/api/v2`
- v1 API (attachments): `${CONFLUENCE_URL}/wiki/rest/api`

## Routing

Load `${CLAUDE_SKILL_DIR}/references/routing.md` to determine which reference and script to use.

## Operation References

| Domain | Reference | Script | Common Use Cases |
|--------|-----------|--------|-----------------|
| Pages | `${CLAUDE_SKILL_DIR}/references/page-operations.md` | `scripts/pages.sh` | Get, create, update, delete, search, children |
| Comments | `${CLAUDE_SKILL_DIR}/references/comment-operations.md` | `scripts/comments.sh` | Footer comments, inline comments, replies |
| Attachments | `${CLAUDE_SKILL_DIR}/references/attachment-operations.md` | `scripts/attachments.sh` | Upload, list, download images and files |
| Spaces | `${CLAUDE_SKILL_DIR}/references/space-operations.md` | `scripts/spaces.sh` | List, get space details |

## Script Usage

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/pages.sh <action> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/comments.sh <action> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/attachments.sh <action> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/spaces.sh <action> [args...]
```

Scripts output JSON to stdout. Errors go to stderr. Non-zero exit on failure.
