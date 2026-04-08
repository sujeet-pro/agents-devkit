---
title: "dev"
description: Development router — detects task type and routes to the right sub-skill
skill_name: dev
category: routing
workflow_tier: orchestrator
---

# dev

Router that detects the type of development task and forwards to the correct sub-skill.

## Routing Rules

| Signal | Routes To |
|--------|-----------|
| "implement", "build", "fix", "debug", "enhance", "tdd" | `dev-build` |
| "refactor", "extract", "rename", "restructure" | `dev-refactor` |
| "migrate", "upgrade", "convert" | `dev-migrate` |
| "commit", "PR description" | `dev-commit` |
| Ambiguous build/refactor | Prefers `dev-build` |

## Parameters

All parameters are forwarded to the target skill.

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<task>` | free text | — | Development task description |
| `--help` | flag | — | Show routing rules |

## Examples

```text
/adk:dev implement user authentication
/adk:dev refactor the payment module
/adk:dev migrate React 17 to React 18
/adk:dev commit these changes
```

## Sub-Skills

- [`dev-build`](./dev-build.md) — Implement, debug, enhance, TDD
- [`dev-refactor`](./dev-refactor.md) — Extract, rename, restructure, simplify, modernize
- [`dev-migrate`](./dev-migrate.md) — Framework/library/version migration
- [`dev-commit`](./dev-commit.md) — Smart commits and PR descriptions
