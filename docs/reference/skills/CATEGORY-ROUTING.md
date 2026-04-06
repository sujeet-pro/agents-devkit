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
| code-review | `adk-code-review` | `adk-code-review-pr`, `adk-code-review-repo`, `adk-code-review-fix` |
| dev | `adk-dev` | `adk-dev-build`, `adk-dev-refactor`, `adk-dev-migrate`, `adk-dev-commit` |
| docs | `adk-docs` | `adk-docs-write`, `adk-docs-review`, `adk-docs-repo`, `adk-docs-crud`, `adk-docs-confluence` |
| diagram | `adk-diagram` | `adk-diagram-mermaid`, `adk-diagram-excalidraw`, `adk-diagram-drawio`, `adk-diagram-graphviz` |

## Single-Skill or Mixed Categories (No Dedicated Router Yet)

| Category | Current direct skills | Recommendation |
|---|---|---|
| quality | `adk-audit`, `adk-test`, `adk-research` | Add `adk-quality` router |
| project | `adk-project`, `adk-setup`, `adk-handoff`, `adk-deps-tracker` | Keep as-is or add `adk-platform` router |
| design | `adk-design` | Keep direct unless more design variants are added |
| planning/spec | `adk-plan`, `adk-spec` | Optionally add `adk-solutioning` router |

## Proposed New Categories (Based on Current Industry Usage)

| Category | Proposed router | Proposed task skills |
|---|---|---|
| delivery | `adk-delivery` | `adk-ci`, `adk-release` |
| quality | `adk-quality` | `adk-audit`, `adk-test`, `adk-incident`, `adk-deps-remediate` |
| platform | `adk-platform` | `adk-setup`, `adk-db`, `adk-infra` |

## Routing Decision Contract

Every category router should:

1. run intent expansion first
2. present 2-3 options and call out the simplest path
3. ask user to pick one or a mix
4. produce an execution plan
5. execute only after approval (unless `--auto`)

## Connector and Tool Priority Contract

For any task involving external systems, category routers should choose integrations in this order:

1. standard in-repo connectors (`adk-github`, `adk-bitbucket`, `adk-confluence`, `adk-jira`)
2. first-party CLI
3. first-party MCP
4. first-party API
5. third-party MCP/CLI/API

This should be treated as a shared policy and propagated to all skills that load `source-routing`.
