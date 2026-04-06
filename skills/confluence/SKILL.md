---
name: adk-confluence
description: "adk - [helper] [connector] Confluence REST API operations — page CRUD, comments, attachments, and space management"
user-invocable: false
workflow-tier: helper
dependencies:
  commands: [curl, jq]
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

## MCP Connector Detection

Before using scripts, check if an official Atlassian MCP connector is available:

1. Look for tools matching `mcp__atlassian-confluence__*` or `mcp__plugin-atlassian-atlassian__*` or `mcp__atlassian__*` pattern
2. If available, prefer MCP tools for supported operations (typically: page read, page update, search)
3. Fall back to scripts for operations NOT covered by the MCP (typically: image/attachment uploads, inline comments, comment replies)

### Known MCP Connector Limitations

The official Atlassian MCP connector typically supports:
- Page read — use MCP
- Page update — use MCP
- Page search — use MCP
- List spaces — use MCP

Operations that typically require scripts:
- Upload attachments/images — use `scripts/attachments.sh`
- Inline comments — use `scripts/comments.sh`
- Comment replies — use `scripts/comments.sh`
- Delete pages — use `scripts/pages.sh`

When a workflow needs both MCP and script operations (e.g., update page content via MCP then upload images via script), use both in sequence.

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
