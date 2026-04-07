---
name: adk-docs-confluence
description: "adk - [full] [docs] Confluence-specific documentation — read/write Confluence pages with format mapping between Confluence storage format and markdown"
user-invocable: true
argument-hint: "<action: read|write|sync> <page-url-or-id> [--space <key>] [--parent <page-id>] [--format markdown|confluence] [--auto] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [curl, jq]
  mcp-servers: [detect-from-input]
workflow-tier: full
---

# Confluence Documentation

Manage Confluence pages with intelligent format mapping between Confluence storage format and local markdown. Read pages as markdown for local editing, write markdown back as properly formatted Confluence pages.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent -> research -> approach -> plan -> execute -> validate. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. |
| `/adk:preflight-check` | before work | Run preflight.py for tool/MCP validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |
| `/adk:confluence` | always | Confluence REST API connector — page CRUD, comments, attachments via curl. |
| `/adk:docs-md` | when converting to/from markdown | Markdown/pagesmith features and formatting rules. |

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/adk-<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<action>` | `read`, `write`, `sync` | required | The operation to perform |
| `<page-url-or-id>` | Confluence URL or page ID | required | Target page |
| `--space` | space key | auto-detect | Confluence space |
| `--parent` | page ID | none | Parent page for new pages |
| `--format` | `markdown`, `confluence` | `markdown` | Local file format |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | off | Show help |

### Actions

| Action | Purpose | Input | Output |
|--------|---------|-------|--------|
| `read` | Download Confluence page as local markdown | Page URL/ID | Local .md file with frontmatter |
| `write` | Publish local markdown to Confluence | Local .md file + page URL/ID | Updated Confluence page |
| `sync` | Bi-directional sync between local and Confluence | Directory + space | Updated files and pages |

### Examples

```
/adk:docs-confluence read https://company.atlassian.net/wiki/spaces/ENG/pages/12345
/adk:docs-confluence write docs/architecture.md --space ENG --parent 12345
/adk:docs-confluence sync docs/ --space ENG
```

## Preflight

Check for Confluence connectivity:
1. Verify `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` in environment
2. Check for MCP connector: `mcp__atlassian-confluence__*` or `mcp__plugin-atlassian-atlassian__*`
3. Prefer MCP for supported operations, fall back to curl scripts

## Format Mapping

### Confluence -> Markdown

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

### Markdown -> Confluence

Reverse mapping. Additionally:
- Frontmatter `title` becomes the page title
- Frontmatter `labels` become Confluence labels
- Images referenced as local paths are uploaded as attachments first
- Internal links (`[text](./other-page.md)`) are converted to Confluence page links

### Frontmatter Convention

When reading from Confluence, generate frontmatter:
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

When writing to Confluence, read frontmatter to determine target page.

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent | yes | Confirm action, target, format |
| 1. Research | yes | Read page/file, detect format, check sync state |
| 2. Approach | conditional | Only for sync when conflicts detected |
| 3. Planning | conditional | Only for sync with multiple pages |
| 4. Execute | yes | Perform read/write/sync |
| 5. Validate | yes | Verify content matches, links work |

## Adjacent Skills

- `/adk:docs-crud` — general doc lifecycle management
- `/adk:docs-review` — review Confluence pages for quality
- `/adk:docs-write` — write formal documents, optionally publish to Confluence
- `/adk:confluence` — low-level Confluence API connector (used internally)
