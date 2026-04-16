---
title: Category Routing Map
description: Current public ADK category coverage without legacy router-era duplication
order: 4
---

# Category Routing Map

The public ADK catalog now prefers direct, specialist task skills over a second layer of public routers.

## Current Public Categories

| Category | Public Skills |
| --- | --- |
| planning-and-research | `adk-plan`, `adk-research` |
| development-and-delivery | `adk-build`, `adk-refactor`, `adk-migrate`, `adk-commit` |
| review | `adk-review-pr`, `adk-review-local-changes`, `adk-address-review-feedback`, `adk-review-docs` |
| documentation | `adk-write-docs` |
| visuals-and-design | `adk-diagram`, `adk-chart`, `adk-design` |
| audits-and-testing | `adk-audit-repo`, `adk-audit-site`, `adk-test` |

## Why There Are No Public Routers

Router-era skills were removed from the default public surface because they created duplication without owning a distinct expert job.

The refactor keeps these rules:

1. one public skill should correspond to one specialist job
2. helper behavior belongs in shared guidance, not as a user-facing public skill
3. repo-maintenance wrappers belong in repo-only surfaces, not in the installable pack

## Choosing A Skill

Use the direct skill whose main deliverable matches the work:

- need a plan first: `adk-plan`
- need evidence first: `adk-research`
- need code changed: `adk-build`, `adk-refactor`, or `adk-migrate`
- need review findings: one of the `adk-review-*` skills
- need docs authored or published: `adk-write-docs`
- need docs reviewed: `adk-review-docs`
- need visuals: `adk-diagram`, `adk-chart`, or `adk-design`
- need audits or validation: `adk-audit-repo`, `adk-audit-site`, or `adk-test`

## Shared Routing Policy

When a skill needs an external system or a runtime-specific capability, use this priority order:

1. runtime MCP server or native runtime tool directly
2. first-party CLI
3. first-party API
4. repo-specific wrapper only when it adds real task logic beyond basic connectivity
5. third-party fallback
