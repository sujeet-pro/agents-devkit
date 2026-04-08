---
title: "docs-crud"
description: Manage documentation lifecycle — create, update, improve, respond to comments
skill_name: docs-crud
category: task
workflow_tier: full
---

# docs-crud

Manages the per-page documentation lifecycle: create new documents, update existing ones, improve quality, and respond to comments.

## When to Use

- Create a new document from a template
- Update an existing document with new content
- Improve document clarity and structure
- Respond to document comments

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<action>` | `create`, `update`, `improve`, `comment-reply` | (required) | Lifecycle action |
| `<path>` | file path | (required) | Target document |
| `--type` | `adr`, `api-reference`, `erd`, `hld`, `incident-report`, `lld`, `onboarding`, `prd`, `project`, `release-notes`, `rfc`, `runbook`, `status-report`, `tdd` | auto-detect | Document type (loads matching template) |
| `--template` | file path | — | Custom template file |
| `--format` | `pagesmith`, `markdown` | auto-detect | Output format |
| `--auto` | flag | off | Skip confirmations |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Workflow

Phases 2–3 conditional on `create` complexity. Abbreviated for `update`, `improve`, `comment-reply`.

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm action, detect document type |
| 1. Research | Read existing doc (for update/improve), load type-specific template |
| 2. Approach | (create only) Present structure options |
| 3. Planning | (create only) Plan sections |
| 4. Execute | Create/update/improve the document or reply to comments |
| 5. Validate | Self-review for completeness |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer`, `agentic-teams`, `interaction`, `docs-guidelines`, `docs-md`, `confluence` (when applicable), `jira` (for context), `diagram` (when needed), `chart` (when needed).

## Examples

```text
/adk:docs-crud create ./docs/decisions/caching.md --type adr
/adk:docs-crud create ./docs/specs/auth.md --type tdd
/adk:docs-crud update ./docs/api-reference.md
/adk:docs-crud improve ./docs/architecture/overview.md
/adk:docs-crud comment-reply ./docs/api-reference.md
/adk:docs-crud create ./docs/new-doc.md --template ./templates/custom.md
```
