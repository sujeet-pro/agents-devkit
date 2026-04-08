---
title: "dev-migrate"
description: Migrate frameworks, libraries, or language versions with breaking-change analysis
skill_name: dev-migrate
category: task
workflow_tier: full
---

# dev-migrate

Migrates frameworks, libraries, or language versions. Reads changelogs, identifies breaking changes, maps them to your codebase, and executes the migration.

## When to Use

- Upgrade a framework to a new major version
- Swap one library for another
- Upgrade a language runtime version

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<source> to <target>` | free text | (required) | Migration source and target (e.g., "React 17 to React 18") |
| `--scope` | path(s) | repo root | Limit migration to specific directories |
| `--dry-run` | flag | off | Analyze breaking changes without making modifications |
| `--auto` | flag | off | Skip confirmations, execute full migration |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm source and target versions, detect migration type |
| 1. Research | Read changelogs, breaking changes, migration guides |
| 2. Approach | Present migration strategy, risks, and alternatives |
| 3. Planning | Map breaking changes to codebase locations, create step-by-step plan |
| 4. Execute | Apply migration changes incrementally |
| 5. Validate | Run tests, verify compatibility, check for missed changes |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer` (always for migrations), `agentic-teams`, `interaction`.

## Examples

```text
/adk:dev-migrate React 17 to React 18
/adk:dev-migrate Node 18 to Node 22
/adk:dev-migrate moment.js to dayjs
/adk:dev-migrate Express to Fastify
/adk:dev-migrate React 17 to React 18 --dry-run
/adk:dev-migrate --scope src/frontend/ Vue 2 to Vue 3
```
