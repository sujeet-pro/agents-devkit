---
title: "confluence"
description: Confluence REST API operations — page CRUD, comments, attachments, and space management
skill_name: confluence
category: connector
workflow_tier: helper
user_invocable: false
---

# confluence

Platform connector for Confluence Cloud. Wraps the Confluence REST API v2 (with v1 fallback for attachments) via `curl`, providing page CRUD, inline and footer comments, attachment management, and space operations to task skills that need Confluence integration.

## Purpose

- Provide Confluence Cloud API access to task skills like `docs-confluence`, `docs-crud`, and `docs-review`
- Read, create, update, and delete Confluence pages with Confluence storage format (HTML)
- Post inline comments anchored to specific text and footer comments for general page feedback
- Upload, update, list, and download file attachments and images
- Search pages and list spaces for discovery workflows

## Authentication & Setup

### Requirements

| Dependency | Check | Install |
|------------|-------|---------|
| `curl` | `command -v curl` | Pre-installed on macOS/Linux |
| `jq` | `command -v jq` | `brew install jq` (macOS) |
| Confluence credentials | `bash scripts/auth.sh` | Set env vars in `~/.zshenv` |

### Environment Variables

Add to `~/.zshenv`:

```bash
export CONFLUENCE_URL="https://your-domain.atlassian.net"
export CONFLUENCE_USERNAME="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-api-token"
```

Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

### Validation

Run `bash scripts/auth.sh` to verify credentials. If auth fails, the skill stops and prompts the user to add or update credentials in `~/.zshenv`, then `source ~/.zshenv`.

## Available Operations

### Page Operations

| Operation | Script Command |
|-----------|----------------|
| Get page by ID | `pages.sh get --id <id>` |
| Get page by title | `pages.sh get-by-title --title "..." --space-id <id>` |
| Search pages | `pages.sh search --query "..." --space-id <id>` |
| Create page | `pages.sh create --space-id <id> --title "..." --body "<html>"` |
| Update page | `pages.sh update --id <id> --title "..." --body "<html>"` |
| Delete page | `pages.sh delete --id <id>` |
| List children | `pages.sh children --id <id>` |
| Get labels | `pages.sh labels --id <id>` |
| Add label | `pages.sh add-label --id <id> --label "name"` |

### Comment Operations

| Operation | Script Command |
|-----------|----------------|
| List footer comments | `comments.sh list-footer --page-id <id>` |
| List inline comments | `comments.sh list-inline --page-id <id>` |
| Add footer comment | `comments.sh create-footer --page-id <id> --body "<html>"` |
| Add inline comment | `comments.sh create-inline --page-id <id> --body "<html>" --text-selection "..."` |
| Reply to comment | `comments.sh reply --comment-id <id> --body "<html>"` |
| Get comment | `comments.sh get --comment-id <id> --type footer\|inline` |

### Attachment Operations

| Operation | Script Command |
|-----------|----------------|
| List attachments | `attachments.sh list --page-id <id>` |
| Upload attachment | `attachments.sh upload --page-id <id> --file <path>` |
| Update attachment | `attachments.sh update --page-id <id> --attachment-id <id> --file <path>` |
| Download attachment | `attachments.sh download --page-id <id> --attachment-id <id> --output <path>` |

### Space Operations

| Operation | Script Command |
|-----------|----------------|
| List spaces | `spaces.sh list` |
| Get space by ID | `spaces.sh get --id <id>` |
| Get space by key | `spaces.sh get --key <key>` |

## MCP vs API Fallback Behavior

| Priority | Method | When Used |
|----------|--------|-----------|
| **Primary** | REST API via `curl` (bundled scripts) | Always preferred. Works in any environment without MCP dependencies |
| **Secondary** | MCP tools (`mcp__atlassian-confluence__*`, `mcp__plugin-atlassian-atlassian__*`, `mcp__atlassian__*`) | Used when available, for supported operations (page read, update, search, list spaces) |
| **Fallback** | Direct `curl` commands | When scripts are not accessible via `${CLAUDE_SKILL_DIR}` |

### MCP Connector Limitations

The official Atlassian MCP connector supports a subset of operations. These **always require direct API calls**:

| Operation | Reason |
|-----------|--------|
| Upload/update attachments | MCP connectors don't support multipart file upload |
| Inline comments | MCP connectors typically lack inline comment support |
| Comment replies | MCP connectors typically lack reply threading |
| Delete pages | MCP connectors may not expose delete |

### MCP-Eligible Operations

When an Atlassian MCP connector is available, prefer MCP for:

- **Page read** — `confluence_get_page` or equivalent
- **Page update** — `confluence_update_page` or equivalent
- **Search** — `confluence_search` or equivalent

## Key Behaviors

- **API-first**: direct REST API calls via bundled `scripts/` always preferred over MCP tools
- **Dual API versions**: uses REST API v2 for most operations, falls back to v1 API for attachment operations
- **Inline comments default**: "comments" means inline comments anchored to specific text; footer (page-level) comments are only for general feedback
- **Confluence storage format**: page bodies use Confluence storage format (HTML), not markdown — consuming skills handle format conversion
- **JSON output**: scripts output JSON to stdout, errors to stderr, non-zero exit on failure
- **API base**: v2 at `${CONFLUENCE_URL}/wiki/api/v2`, v1 at `${CONFLUENCE_URL}/wiki/rest/api`

## Invoked By

| Skill | When |
|-------|------|
| `/adk:docs-confluence` | Always — primary connector for Confluence-specific doc workflows (read, write, format mapping) |
| `/adk:docs-crud` | Target is Confluence — page CRUD, comments, attachments for doc lifecycle management |
| `/adk:docs-review` | Target is Confluence — reads page content and posts review feedback as comments |
