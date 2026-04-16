# adk-confluence

Manage Confluence pages, spaces, comments, labels, and attachments via the Atlassian Confluence MCP server.

## Quick Start

```bash
npx adk-confluence "create a new architecture overview page" --space ENG --parent "Technical Docs"
```

## What This Skill Does

Bridges local documentation workflows with hosted Confluence spaces. Handles page lifecycle operations (create, read, update, delete), content publishing from local markdown, search, page hierarchy management, comments, labels, and attachments. All operations go through the Atlassian Confluence MCP server -- no direct REST API calls needed.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What Confluence operation to perform |
| `--action` | `create`, `update`, `search`, `publish`, `manage` | inferred | Explicit action when the task is ambiguous |
| `--space` | space key (e.g. `ENG`, `DOCS`) | none | Target Confluence space key |
| `--page` | page ID or exact title | none | Target page identifier |
| `--parent` | page ID or title | none | Parent page for creation or moves |
| `--labels` | comma-separated labels | none | Labels to add after create or update |
| `--format` | `markdown`, `storage` | `markdown` | Input format when publishing local content |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | command | yes |
| `python3` | command | yes |
| `atlassian-confluence` | MCP server | yes |

### MCP Server Setup

The skill requires the Atlassian Confluence MCP server to be configured in your IDE settings.

**Claude Code** -- add to `~/.claude.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "atlassian-confluence": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-atlassian", "--confluence"],
      "env": {
        "CONFLUENCE_URL": "https://your-domain.atlassian.net",
        "CONFLUENCE_USERNAME": "you@example.com",
        "CONFLUENCE_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

**Cursor** -- add to `.cursor/mcp.json`:

```json
{
  "mcp": {
    "servers": {
      "atlassian-confluence": {
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-atlassian", "--confluence"],
        "env": {
          "CONFLUENCE_URL": "https://your-domain.atlassian.net",
          "CONFLUENCE_USERNAME": "you@example.com",
          "CONFLUENCE_API_TOKEN": "<your-api-token>"
        }
      }
    }
  }
}
```

Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

## Skill Layout

```
adk-confluence/
  SKILL.md
  README.md
  scripts/
    preflight.py
  references/
    workflow.md
    persona.md
    _shared/
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
```

## Workflow

1. Run preflight to verify the Atlassian Confluence MCP server is configured.
2. Confirm the task, target space, target page, and intended action.
3. Identify the correct MCP tool(s) for the operation.
4. For destructive actions (delete, overwrite), confirm with the user before executing.
5. Execute the operation via MCP tools.
6. Validate the result by fetching the page or checking the response.
7. Report the outcome with page URL, page ID, and a summary of what changed.

## Interaction Protocol

Unless `--auto` is set, the skill follows an interactive workflow:

1. **Intent confirmation** -- confirms the target space, page, and action. Destructive actions always require explicit confirmation.
2. **Content preview** -- before publishing or updating, presents a content preview with target, action, content summary, and labels.
3. **Result report** -- after execution, reports the page URL, page ID, and what changed.
4. **User response** -- `ok` to approve, feedback text to adjust, `cancel` to abort.

## Output Format

Each run produces:
- Action performed (created, updated, deleted, published, searched, etc.)
- Page URL and page ID when applicable
- Content summary or search result count
- Labels and attachments affected
- Remaining risk or follow-up actions

## Examples

### Create a page
```bash
npx adk-confluence "create a new architecture overview page" --space ENG --parent "Technical Docs"
```
Confirms the space and parent, presents content preview, creates the page, reports the URL.

### Update a page
```bash
npx adk-confluence "update the runbook with new deploy steps" --page "Deploy Runbook" --space OPS
```
Fetches the current page, shows a diff preview, updates after approval.

### Search a space
```bash
npx adk-confluence "find all pages labeled api-reference" --space DOCS --action search
```
Runs a CQL search, presents matching pages with IDs and URLs.

### Publish local markdown
```bash
npx adk-confluence "publish docs/architecture.md to Confluence" --space ENG --action publish --auto
```
Skips confirmations, converts markdown to Confluence storage format, creates or updates the page, reports the URL.

## What Success Looks Like

- [ ] Every page create or update is confirmed by fetching the resulting page
- [ ] Every delete is confirmed by verifying the page is no longer accessible
- [ ] Attachment uploads are confirmed by listing page attachments after upload
- [ ] Search results include page IDs and URLs for verification
- [ ] The MCP server is configured and preflight passes before any operation
- [ ] The skill reports action, page URL, page ID, and remaining risk
