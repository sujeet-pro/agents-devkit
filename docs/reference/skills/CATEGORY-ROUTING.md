---
title: Category Routing Map
description: Category-first routing model and current ADK category coverage
order: 4
---

# Category Routing Map

This file defines category-level routing so users can invoke either:
- a **specific skill** directly, or
- a **category router** that selects the right skill.

## Current Categories and Routers

| Category | Router skill | Direct skills |
|---|---|---|
| code-review | `code-review` | `code-review-pr`, `code-review-repo`, `code-review-fix` |
| dev | `dev` | `dev-build`, `dev-refactor`, `dev-migrate`, `dev-commit` |
| docs | `docs` | `docs-write`, `docs-review`, `docs-repo`, `docs-crud`, `docs-confluence` |
| diagram | `diagram` | `diagram-mermaid`, `diagram-excalidraw`, `diagram-drawio`, `diagram-graphviz` |

## Single-Skill or Mixed Categories (No Dedicated Router Yet)

| Category | Current direct skills | Recommendation |
|---|---|---|
| quality | `audit`, `test`, `research` | Add `quality` router |
| project | `project`, `setup`, `handoff`, `deps-tracker` | Keep as-is or add `platform` router |
| design | `design` | Keep direct unless more design variants are added |
| planning/spec | `plan`, `spec` | Optionally add `solutioning` router |

## Proposed New Categories (Based on Current Industry Usage)

| Category | Proposed router | Proposed task skills |
|---|---|---|
| delivery | `delivery` | `ci`, `release` |
| quality | `quality` | `audit`, `test`, `incident`, `deps-remediate` |
| platform | `platform` | `setup`, `db`, `infra` |

## Routing Decision Contract

Every category router should:

1. run intent expansion first
2. present 2-3 options and call out the simplest path
3. ask user to pick one or a mix
4. produce an execution plan
5. execute only after approval (unless `--auto`)

## Connector and Tool Priority Contract

For any task involving external systems, category routers should choose integrations in this order:

1. standard in-repo connectors (`github`, `bitbucket`, `confluence`, `jira`)
2. first-party CLI
3. first-party MCP
4. first-party API
5. third-party MCP/CLI/API

This should be treated as a shared policy and propagated to all skills that load `source-routing`.
