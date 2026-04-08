---
title: "docs-review"
description: Review documentation for accuracy, completeness, clarity, and style
skill_name: docs-review
category: task
workflow_tier: full
---

# docs-review

Reviews documentation from local files, Confluence, or Google Docs across multiple dimensions. Supports standard, interactive, and follow-up review modes.

## When to Use

- Review a document before publishing
- Audit documentation quality
- Interactive review with accept/reject per finding
- Follow-up review after fixes

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<path-or-url>` | file path, directory, or URL | (required) | Document(s) to review |
| `--mode` | `auto`, `standard`, `interactive`, `followup` | `auto` | Review interaction style |
| `--focus` | `accuracy`, `completeness`, `clarity`, `style`, `all` | `all` | Review dimension |
| `--publish` | flag | off | Post review comments to source platform |
| `--confidence` | flag | off | Show confidence ratings per finding |
| `--auto` | flag | off | Skip confirmations |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Workflow

Phases 2–3 skipped (direct review execution).

| Phase | Action |
|-------|--------|
| 0. Intent | Detect source type (local/Confluence/Google Docs), confirm scope |
| 1. Research | Read document(s), detect type, load doc guidelines |
| 4. Execute | Review across selected dimensions |
| 5. Validate | Compile findings, assign severity and confidence |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `review-standards`, `principal-engineer`, `agentic-teams`, `interaction`, `docs-guidelines`, `docs-md`, `confluence` (for Confluence URLs).

## Examples

```text
/adk:docs-review ./docs/api-reference.md
/adk:docs-review ./docs/ --focus clarity
/adk:docs-review --mode interactive ./docs/architecture.md
/adk:docs-review https://company.atlassian.net/wiki/spaces/ENG/pages/12345
/adk:docs-review ./docs/api-reference.md --confidence --verbosity detailed
```
