# Confluence Routing

Map the current task to the correct operation reference and script.

## Workflow Routing

### Doc Review Workflow

Reading an existing page, reviewing content, and leaving feedback.

1. **Get page content** → `scripts/pages.sh get --id <pageId>` | ref: `page-operations.md`
2. **Read body** → parse `body.storage.value` from the returned JSON
3. **Add review comments** → `scripts/comments.sh create-inline --page-id <id> --body "<comment>" --text-selection "<text>"` | ref: `comment-operations.md`
4. **Add summary comment** → `scripts/comments.sh create-footer --page-id <id> --body "<summary>"` | ref: `comment-operations.md`
5. **Upload annotated screenshots** → `scripts/attachments.sh upload --page-id <id> --file <path>` | ref: `attachment-operations.md`

### Doc Writing Workflow

Creating or updating page content.

1. **Find or create page** → `scripts/pages.sh get-by-title --title "..." --space-id <id>` or `scripts/pages.sh create --space-id <id> --title "..." --body "<html>"` | ref: `page-operations.md`
2. **Update content** → `scripts/pages.sh update --id <id> --title "..." --body "<html>"` | ref: `page-operations.md`
3. **Upload attachments** → `scripts/attachments.sh upload --page-id <id> --file <path>` | ref: `attachment-operations.md`
4. **Add labels** → `scripts/pages.sh add-label --id <id> --label "label-name"` | ref: `page-operations.md`

### Doc CRUD Workflow

General page management operations.

1. **Search** → `scripts/pages.sh search --query "..." --space-id <id>` | ref: `page-operations.md`
2. **Get** → `scripts/pages.sh get --id <pageId>` | ref: `page-operations.md`
3. **Create** → `scripts/pages.sh create --space-id <id> --title "..." --body "<html>"` | ref: `page-operations.md`
4. **Update** → `scripts/pages.sh update --id <id> --title "..." --body "<html>"` | ref: `page-operations.md`
5. **Delete** → `scripts/pages.sh delete --id <id>` | ref: `page-operations.md`

### Comment Operations

Working with page comments and replies.

1. **List comments** → `scripts/comments.sh list-footer --page-id <id>` | ref: `comment-operations.md`
2. **Add footer comment** → `scripts/comments.sh create-footer --page-id <id> --body "<html>"` | ref: `comment-operations.md`
3. **Add inline comment** → `scripts/comments.sh create-inline --page-id <id> --body "<html>" --text-selection "<text>"` | ref: `comment-operations.md`
4. **Reply to comment** → `scripts/comments.sh reply --comment-id <id> --body "<html>"` | ref: `comment-operations.md`

## Operation → Script Quick Reference

| Operation | Script | Action |
|-----------|--------|--------|
| Get page by ID | `pages.sh` | `get --id <id>` |
| Get page by title | `pages.sh` | `get-by-title --title "..." --space-id <id>` |
| Search pages | `pages.sh` | `search --query "..." --space-id <id>` |
| Create page | `pages.sh` | `create --space-id <id> --title "..." --body "<html>"` |
| Update page | `pages.sh` | `update --id <id> --title "..." --body "<html>"` |
| Delete page | `pages.sh` | `delete --id <id>` |
| List children | `pages.sh` | `children --id <id>` |
| Get labels | `pages.sh` | `labels --id <id>` |
| Add label | `pages.sh` | `add-label --id <id> --label "name"` |
| List footer comments | `comments.sh` | `list-footer --page-id <id>` |
| List inline comments | `comments.sh` | `list-inline --page-id <id>` |
| Add footer comment | `comments.sh` | `create-footer --page-id <id> --body "<html>"` |
| Add inline comment | `comments.sh` | `create-inline --page-id <id> --body "<html>" --text-selection "..."` |
| Reply to comment | `comments.sh` | `reply --comment-id <id> --body "<html>"` |
| Get comment | `comments.sh` | `get --comment-id <id> --type footer\|inline` |
| List attachments | `attachments.sh` | `list --page-id <id>` |
| Upload attachment | `attachments.sh` | `upload --page-id <id> --file <path>` |
| Update attachment | `attachments.sh` | `update --page-id <id> --attachment-id <id> --file <path>` |
| Download attachment | `attachments.sh` | `download --page-id <id> --attachment-id <id> --output <path>` |
| List spaces | `spaces.sh` | `list` |
| Get space | `spaces.sh` | `get --id <id>` or `get --key <key>` |

## MCP vs Script Decision

When an Atlassian MCP connector is available, prefer MCP for:
- **Page read**: MCP `confluence_get_page` or equivalent
- **Page update**: MCP `confluence_update_page` or equivalent
- **Search**: MCP `confluence_search` or equivalent

Always use scripts for:
- **Attachment upload/update**: MCP connectors don't support multipart file upload
- **Inline comments**: MCP connectors typically lack inline comment support
- **Comment replies**: MCP connectors typically lack reply threading
- **Page deletion**: MCP connectors may not expose delete
