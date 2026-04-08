---
title: "docs-confluence"
description: Read, write, and sync Confluence pages with format mapping
skill_name: docs-confluence
category: task
workflow_tier: full
---

# docs-confluence

Reads, writes, and syncs Confluence pages with bidirectional format mapping between Confluence storage format and markdown.

## When to Use

- Read a Confluence page into local markdown
- Publish a local document to Confluence
- Sync changes between local files and Confluence

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<action>` | `read`, `write`, `sync` | (required) | Operation type |
| `<page-url-or-id>` | Confluence URL or page ID | (required for read/sync) | Target page |
| `--space` | space key | — | Confluence space (for write) |
| `--parent` | page title | — | Parent page (for write) |
| `--format` | `markdown`, `confluence` | `markdown` | Output format |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Workflow

Phases 2–3 only for sync conflicts or multi-page sync.

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm action and target |
| 1. Research | Fetch page content, detect format |
| 4. Execute | Read/write/sync the page |
| 5. Validate | Verify format mapping accuracy |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `interaction`, `confluence`, `docs-md`.

## Examples

```text
/adk:docs-confluence read https://company.atlassian.net/wiki/spaces/ENG/pages/12345
/adk:docs-confluence write ./docs/api-reference.md --space ENG --parent "API Docs"
/adk:docs-confluence sync https://company.atlassian.net/wiki/spaces/ENG/pages/12345
```
