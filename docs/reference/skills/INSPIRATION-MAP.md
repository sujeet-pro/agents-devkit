---
title: Skill Inspiration Map
description: Mapping of ADK skills to external inspirations and internal influencing skills
order: 3
---

# Skill Inspiration Map

This mapping shows:
- **External inspirations** (open-source repos, docs, ecosystems)
- **Internal influences** (shared ADK helper/guideline skills)

For external references, only sources already encoded in `manifest.json` or explicitly documented in skill metadata are listed as "direct".

## Global Internal Influence Baseline

Most full task skills are influenced by the same internal helpers:
- `workflow`
- `communication`
- `preflight-check`
- `output-format`
- `principal-engineer` (medium/large)
- `agentic-teams` (parallelizable medium/large)
- `interaction` (non-auto flows)

## External Inspiration Mapping (Direct)

| ADK skill | External inspiration(s) |
|---|---|
| `diagram` | `diagramkit` |
| `diagram-mermaid` | `diagramkit`, `mermaid-js/mermaid` |
| `diagram-excalidraw` | `diagramkit`, `coleam00/excalidraw-diagram-skill`, `whq25/agent-canvas`, `kakacoding1/mcp_excalidraw` |
| `diagram-drawio` | `diagramkit` |
| `diagram-graphviz` | `diagramkit` |
| `docs-write` | `pagesmith`, `obra/superpowers` |
| `docs-repo` | `pagesmith` |
| `docs-review` | `pagesmith` |
| `docs-crud` | `pagesmith` |
| `docs-md` | `pagesmith` |
| `dev-build` | `obra/superpowers`, `cj-ways/arcana (deep-fix, refactor-plan)` |
| `dev-refactor` | `cj-ways/arcana (refactor-plan)` |
| `plan` | `obra/superpowers` |
| `code-review-pr` | `obra/superpowers`, `cj-ways/arcana (quick-review, deep-review)` |
| `code-review-repo` | `cj-ways/arcana (agent-audit)` |
| `audit` | `cj-ways/arcana (agent-audit)` |

## Skill-by-Skill Internal Influence Mapping

## Routing Skills

| Skill | Influenced by internal ADK skills |
|---|---|
| `use` | `workflow`, `interaction`, `principal-engineer`, `preflight-check`, `output-format`, `communication` |
| `dev` | `use`, `workflow`, `interaction` |
| `docs` | `use`, `workflow`, `interaction` |
| `code-review` | `use`, `workflow`, `interaction`, `review-standards` |
| `diagram` | `use`, `workflow`, `interaction` |

## Task Skills

| Skill | Primary internal influence |
|---|---|
| `audit` | `workflow`, `principal-engineer`, `architecture`, `coding` |
| `code-review-pr` | `review-standards`, `coding`, `architecture`, `workflow` |
| `code-review-repo` | `review-standards`, `architecture`, `coding`, `workflow` |
| `code-review-fix` | `review-standards`, `coding`, `workflow` |
| `dev-build` | `coding`, `workflow`, `principal-engineer` |
| `dev-refactor` | `coding`, `architecture`, `workflow`, `principal-engineer` |
| `dev-migrate` | `coding`, `workflow`, `principal-engineer` |
| `dev-commit` | `communication`, `output-format`, `workflow` |
| `docs-write` | `docs-guidelines`, `docs-md`, `workflow`, `communication` |
| `docs-repo` | `docs-guidelines`, `docs-md`, `workflow` |
| `docs-review` | `docs-guidelines`, `docs-md`, `review-standards`, `workflow` |
| `docs-crud` | `docs-guidelines`, `docs-md`, `workflow` |
| `docs-confluence` | `docs-md`, `workflow`, `confluence` |
| `diagram-mermaid` | `workflow`, `output-format` |
| `diagram-excalidraw` | `workflow`, `output-format` |
| `diagram-drawio` | `workflow`, `output-format` |
| `diagram-graphviz` | `workflow`, `output-format` |
| `design` | `workflow`, `principal-engineer`, `communication` |
| `research` | `workflow`, `agentic-teams`, `communication` |
| `spec` | `workflow`, `principal-engineer`, `communication` |
| `plan` | `workflow`, `interaction`, `principal-engineer`, `agentic-teams` |
| `project` | `workflow`, `interaction`, `principal-engineer` |
| `team` | `agentic-teams`, `workflow`, `interaction` |
| `test` | `workflow`, `interaction`, `communication` |
| `setup` | `preflight-check`, `workflow` |
| `handoff` | `workflow`, `communication` |
| `deps-tracker` | `workflow`, `interaction`, `communication` |

## Helper Skills

| Skill | Influenced by |
|---|---|
| `workflow` | internal ADK workflow framework |
| `communication` | internal ADK output/communication standards |
| `interaction` | internal ADK human-in-the-loop protocol |
| `principal-engineer` | internal ADK senior IC heuristics |
| `agentic-teams` | internal ADK multi-agent contract |
| `output-format` | internal ADK output consistency needs |
| `preflight-check` | internal ADK reliability and tool readiness |
| `review-standards` | internal ADK review consistency |
| `coding` | internal ADK coding guideline library |
| `docs-guidelines` | internal ADK documentation guideline library |
| `docs-md` | internal ADK markdown target compatibility patterns |
| `architecture` | internal ADK architecture guideline library |
| `github` | platform API/CLI conventions |
| `bitbucket` | platform API conventions |
| `confluence` | platform API conventions |
| `jira` | platform API conventions |

## Maintenance Rule

When adding or updating any skill:

1. update this map with internal and external influences
2. if external inspiration changed, also update `manifest.json` (`sources` and/or `open_source_refs`)
3. ensure each task skill retains fallback summaries for required helper skills
