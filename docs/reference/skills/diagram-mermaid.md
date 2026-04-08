---
title: "diagram-mermaid"
description: Create Mermaid diagrams with full syntax reference for all 21 diagram types
skill_name: diagram-mermaid
category: task
workflow_tier: full
---

# diagram-mermaid

Creates Mermaid diagram source files with full syntax reference for all 21 supported diagram types. Supports light/dark mode rendering via diagramkit.

## When to Use

- Create diagrams that render inline in GitHub, Confluence, and markdown platforms
- Flowcharts, sequence diagrams, ER diagrams, class diagrams, Gantt charts, state machines
- Any of the 21 Mermaid diagram types

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--type` | `flowchart`, `sequence`, `classDiagram`, `stateDiagram`, `erDiagram`, `gantt`, `pie`, `quadrantChart`, `requirementDiagram`, `gitgraph`, `mindmap`, `timeline`, `sankey`, `journey`, `xychart`, `block`, `packet`, `kanban`, `architecture`, `c4`, `zenuml` | auto-detect | Mermaid diagram type |
| `--render` | flag | auto (if diagramkit available) | Render to image |
| `--format` | `svg`, `png` | `svg` | Render output format |
| `--theme` | `light`, `dark` | `light` | Color theme |
| `--help` | flag | — | Show parameters |

## Workflow

Phases 2–3 skipped (direct creation).

| Phase | Action |
|-------|--------|
| 0. Intent | Detect diagram type, confirm scope |
| 1. Research | Load type-specific syntax reference |
| 4. Execute | Generate Mermaid source, render if requested |
| 5. Validate | Verify syntax is valid |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `workspace-conventions`.

## Examples

```text
/adk:diagram-mermaid auth flow sequence diagram
/adk:diagram-mermaid --type flowchart CI/CD pipeline
/adk:diagram-mermaid --type erDiagram e-commerce database schema
/adk:diagram-mermaid --type classDiagram payment module class hierarchy
/adk:diagram-mermaid --render --format png --theme dark system architecture
```
