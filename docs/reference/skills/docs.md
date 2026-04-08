---
title: "docs"
description: Documentation router — detects task type and routes to the right sub-skill
skill_name: docs
category: routing
workflow_tier: orchestrator
---

# docs

Router that detects the type of documentation task and forwards to the correct sub-skill.

## Routing Rules

| Signal | Routes To |
|--------|-----------|
| Confluence URL | `docs-confluence` or `docs-review` |
| Formal doc types (ADR, RFC, TDD, etc.) | `docs-write` |
| "create", "update", "improve" | `docs-crud` |
| "review", "audit" | `docs-review` |
| "repo docs", "generate docs" | `docs-repo` |
| "markdown format", "pagesmith" | `docs-md` |

## Parameters

All parameters are forwarded to the target skill.

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<task>` | free text | — | Documentation task description |
| `--help` | flag | — | Show routing rules |

## Examples

```text
/adk:docs write an ADR for the caching decision
/adk:docs review ./docs/api-reference.md
/adk:docs create onboarding documentation
/adk:docs generate repository documentation
```

## Sub-Skills

- [`docs-write`](./docs-write.md) — Formal engineering documents
- [`docs-crud`](./docs-crud.md) — Per-page create/update/improve
- [`docs-review`](./docs-review.md) — Document quality review
- [`docs-repo`](./docs-repo.md) — Repository documentation
- [`docs-confluence`](./docs-confluence.md) — Confluence read/write/sync
