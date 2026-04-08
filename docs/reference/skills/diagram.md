---
title: "diagram"
description: Diagram router — auto-detects engine and routes to the right diagram skill
skill_name: diagram
category: routing
workflow_tier: orchestrator
---

# diagram

Router that detects the best diagramming engine from your request and forwards to the engine-specific skill. Prefers engines matching existing diagram files in the project.

## Routing Rules

| Signal | Routes To |
|--------|-----------|
| "sequence", "flowchart", "ER diagram", "class diagram", "gantt", inline markdown | `diagram-mermaid` |
| "hand-drawn", "whiteboard", "excalidraw", architecture overview | `diagram-excalidraw` |
| "network topology", "BPMN", "enterprise", AWS/Azure/GCP icons, "draw.io" | `diagram-drawio` |
| "dependency graph", "call graph", "dot", `.dot` file | `diagram-graphviz` |
| Existing `.mmd` files in project | Prefers `diagram-mermaid` |
| Existing `.excalidraw` files | Prefers `diagram-excalidraw` |
| Existing `.drawio` files | Prefers `diagram-drawio` |
| Existing `.dot` files | Prefers `diagram-graphviz` |

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--engine` | `mermaid`, `excalidraw`, `drawio`, `graphviz` | auto-detect | Override engine selection |
| `--type` | diagram type | — | Diagram type (forwarded to engine) |
| `--render` | flag | auto | Render to image |
| `--format` | `svg`, `png` | `svg` | Render format |
| `--theme` | `light`, `dark` | `light` | Color theme |
| `--help` | flag | — | Show routing rules |

## Examples

```text
/adk:diagram auth flow sequence diagram
/adk:diagram --engine excalidraw system architecture overview
/adk:diagram --engine drawio AWS infrastructure
/adk:diagram dependency graph for Python packages
```

## Sub-Skills

- [`diagram-mermaid`](./diagram-mermaid.md) — 21 Mermaid diagram types
- [`diagram-excalidraw`](./diagram-excalidraw.md) — Hand-drawn style
- [`diagram-drawio`](./diagram-drawio.md) — Precise layout with rich icons
- [`diagram-graphviz`](./diagram-graphviz.md) — DOT graphs with strict layout
