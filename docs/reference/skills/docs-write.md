---
title: "docs-write"
description: Create or update formal engineering documents with optional publishing
skill_name: docs-write
category: task
workflow_tier: full
---

# docs-write

Creates or updates formal engineering documents (ADR, RFC, TDD, HLD, runbook, API reference, and more). Auto-detects document type, loads the matching stage, and optionally publishes to Confluence or Google Docs.

## When to Use

- Write a new ADR, RFC, TDD, HLD, or other formal document
- Update an existing formal document with new content
- Publish documentation to Confluence

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--type` | `adr`, `rfc`, `tdd`, `hld`, `lld`, `prd`, `runbook`, `api-reference`, `blog`, `changelog`, `onboarding`, `release-notes`, `incident-report`, `status-report`, `erd`, `project`, `fix` | auto-detect | Document type |
| `--format` | `pagesmith`, `markdown` | auto-detect | Output format |
| `--publish` | flag | off | Publish to Confluence/Google Docs |
| `--publish-space` | space key | — | Confluence space for publishing |
| `--publish-parent` | page title | — | Parent page in Confluence |
| `--publish-update` | flag | off | Update existing published page |
| `--publish-title` | title | — | Override the published page title |
| `--output-dir` | path | `.` | Output directory for the document |
| `--frontmatter` | flag | off | Include YAML frontmatter |
| `--audience` | free text | — | Target audience (e.g., "executives", "on-call engineers") |
| `--tone` | free text | — | Writing tone (e.g., "formal", "procedural", "conversational") |
| `--depth` | `quick`, `standard`, `thorough` | `standard` | Content depth |
| `--weight` | number | — | Priority weight for content ordering |
| `--template` | path | — | Custom template file |
| `--auto-apply` | flag | off | Auto-apply template without confirmation |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Workflow

Full 6-phase for new documents. Abbreviated (phases 2–5 skipped) for `--type fix`.

| Phase | Action |
|-------|--------|
| 0. Intent | Detect document type, confirm scope and audience |
| 1. Research | Gather context from codebase, specs, or research |
| 2. Approach | Present structure and outline, user approves |
| 3. Planning | Plan sections and content |
| 4. Execute | Write the document |
| 5. Validate | Self-review for completeness, accuracy, and style |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer`, `agentic-teams`, `interaction`, `docs-guidelines`, `docs-md`, `chart` (when data visualization needed), `diagram` (when diagram assets needed).

## Examples

```text
/adk:docs-write --type adr caching strategy decision
/adk:docs-write --type rfc migration from REST to gRPC
/adk:docs-write --type tdd user authentication service design
/adk:docs-write --type hld --audience executives system architecture overview
/adk:docs-write --type runbook --tone procedural database failover
/adk:docs-write --type adr --publish --publish-space ENG caching strategy
/adk:docs-write --output-dir ./docs/designs/ --type tdd payment processing
```
