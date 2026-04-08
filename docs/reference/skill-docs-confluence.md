---
title: "docs-confluence"
description: Confluence-specific documentation — read/write Confluence pages with format mapping between Confluence storage format and markdown
skill_name: docs-confluence
category: task
workflow_tier: full
user_invocable: true
---

# docs-confluence

Manage Confluence pages with intelligent format mapping between Confluence storage format and local markdown. Read pages as markdown for local editing, write markdown back as properly formatted Confluence pages, or sync bidirectionally between local files and a Confluence space.

## When to Use

- Download a Confluence page as local markdown for editing
- Publish a local markdown document to Confluence
- Sync documentation bidirectionally between local files and Confluence
- Convert between Confluence storage format and markdown

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<action>` | `read` \| `write` \| `sync` | required | The operation to perform |
| `<page-url-or-id>` | Confluence URL or page ID | required | Target Confluence page |
| `--space` | space key | auto-detect | Confluence space |
| `--parent` | page ID | none | Parent page for new pages |
| `--format` | `markdown` \| `confluence` | `markdown` | Local file format |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameter reference and exit |

## Actions

| Action | Purpose | Input | Output |
|--------|---------|-------|--------|
| `read` | Download Confluence page as local markdown | Page URL/ID | Local `.md` file with frontmatter |
| `write` | Publish local markdown to Confluence | Local `.md` file + page URL/ID | Updated Confluence page |
| `sync` | Bi-directional sync between local and Confluence | Directory + space | Updated files and pages |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **`read`** | Downloads page content, converts Confluence storage format to markdown, generates frontmatter with page metadata (ID, URL, space, labels, sync timestamp) |
| **`write`** | Reads local markdown, converts to Confluence storage format (XHTML), uploads local images as attachments, converts internal links to Confluence page links |
| **`sync`** | Compares local files with Confluence pages using frontmatter metadata. Detects conflicts when both sides changed since last sync |

## Format Mapping

### Confluence → Markdown

| Confluence Element | Markdown Equivalent |
|---|---|
| `<h1>` through `<h6>` | `#` through `######` |
| `<p>` | Paragraph text |
| `<ac:structured-macro ac:name="code">` | Fenced code block with language |
| `<ac:structured-macro ac:name="info">` | `> [!NOTE]` alert |
| `<ac:structured-macro ac:name="warning">` | `> [!WARNING]` alert |
| `<ac:structured-macro ac:name="tip">` | `> [!TIP]` alert |
| `<ac:structured-macro ac:name="note">` | `> [!IMPORTANT]` alert |
| `<table>` | GFM table |
| `<ac:image>` | `![alt](attachment-url)` |
| `<ac:link>` | `[text](url)` |
| `<ac:task-list>` | `- [ ]` / `- [x]` task list |
| `<ac:structured-macro ac:name="expand">` | `<details><summary>` |
| `<ac:structured-macro ac:name="toc">` | (omitted, auto-generated) |

### Markdown → Confluence

Reverse mapping. Additionally:

- Frontmatter `title` becomes the page title
- Frontmatter `labels` become Confluence labels
- Local image paths are uploaded as attachments first
- Internal links (`[text](./other-page.md)`) are converted to Confluence page links

### Frontmatter Convention

When reading from Confluence, generates frontmatter:

```yaml
---
confluence_id: "12345"
confluence_url: "https://..."
space: "ENG"
title: "Page Title"
labels: [architecture, api]
last_synced: "2026-04-06T00:00:00Z"
---
```

## Key Behaviors

- **Bidirectional format mapping**: converts between Confluence storage format (XHTML) and markdown with high fidelity
- **Attachment handling**: automatically uploads local images as Confluence attachments on write, downloads them on read
- **Link conversion**: maps internal markdown links to Confluence page links and vice versa
- **Sync conflict detection**: detects when both local and Confluence content changed since the last sync
- **Frontmatter tracking**: stores Confluence metadata (page ID, URL, space, labels, sync timestamp) in YAML frontmatter

## Workflow

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm action, target, format |
| 1. Research & Options | yes | Read page/file, detect format, check sync state |
| 2. Approach Selection | conditional | Only for sync when conflicts detected |
| 3. Planning | conditional | Only for sync with multiple pages |
| 4. Execute | yes | Perform read/write/sync |
| 5. Validate & Learn | yes | Verify content matches, links work |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py for tool/MCP validation |
| `output-format` | producing output | short/standard/detailed verbosity |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |
| `confluence` | always | Confluence REST API connector — page CRUD, comments, attachments |
| `docs-md` | converting to/from markdown | Markdown/pagesmith features and formatting rules |

## Output Format

All output is markdown by default. After each operation, prints a summary:

- **read**: file path written, page title, section count
- **write**: Confluence page URL, action taken (created/updated), attachment count
- **sync**: files synced, conflicts found, resolution actions

## Adjacent Skills

| Skill | When to use instead |
|-------|---------------------|
| `/adk:docs-crud` | General doc lifecycle management (not Confluence-specific) |
| `/adk:docs-review` | Review Confluence pages for quality |
| `/adk:docs-write` | Write formal documents, optionally publish to Confluence |
| `/adk:confluence` | Low-level Confluence API connector (used internally) |

## Examples

```
/adk:docs-confluence read https://company.atlassian.net/wiki/spaces/ENG/pages/12345
/adk:docs-confluence write docs/architecture.md --space ENG --parent 12345
/adk:docs-confluence sync docs/ --space ENG
```
