---
name: adk-diagram
description: "adk - [routing] [diagram] Diagram router — auto-detects the best engine and routes to the right diagram skill"
user-invocable: true
argument-hint: "<description> [--engine mermaid|excalidraw|drawio|graphviz] [--type flowchart|sequence|class|...] [--help]"
allowed-tools: [Glob, Grep, Read]
workflow-tier: orchestrator
dependencies:
  npm-packages: [diagramkit]
---

# Diagram Router

Unified entry point for diagram creation. Auto-detects the best engine from context and routes to the engine-specific skill, or accepts an explicit `--engine`.

## Routing

If `--engine` is explicitly provided, route directly to the matching engine skill. Otherwise, auto-detect:

| Signal | Engine | Route To |
|--------|--------|----------|
| `--type=freeform`, "architecture overview", "system context", "codebase map" | Excalidraw | `/adk:diagram-excalidraw` |
| `--type=network` with "topology", "rack", "physical"; BPMN, org chart, multi-page | Draw.io | `/adk:diagram-drawio` |
| Existing `.dot` files, "dependency graph", strict graph layout | Graphviz | `/adk:diagram-graphviz` |
| All other types: flowchart, sequence, class, state, ER, gantt, mindmap, timeline, C4, etc. | Mermaid | `/adk:diagram-mermaid` |

### Engine Selection Rules

1. `--type=freeform` -> Excalidraw
2. `--type=network` with "topology", "rack", "physical" -> Draw.io
3. `--type=architecture` with "overview", "high-level", "system context" -> Excalidraw
4. `--type=architecture` with "AWS", "Azure", "GCP" + "detailed" -> Draw.io
5. `--type` is `sequence`, `class`, `state`, `er`, `gantt`, `gitgraph`, `mindmap`, `timeline`, `kanban`, `quadrant`, `sankey`, `xy`, `packet`, `radar`, `journey`, `c4` -> Mermaid
6. "BPMN", "business process", "org chart", "multi-page" -> Draw.io
7. "codebase", "project structure", "repo overview" -> Excalidraw
8. "flowchart", "process", "workflow", "pipeline", "decision tree" -> Mermaid
9. Default -> Mermaid

### Context Signals

Check for existing diagram files in the project (`.mmd`, `.mermaid`, `.excalidraw`, `.drawio`, `.dot`) and prefer that engine for consistency.

### Default Preference Order

Mermaid > Excalidraw > Draw.io > Graphviz

### Parameter Forwarding

Pass all parameters to the target engine skill. The router does not consume parameters except `--engine` and `--help`.

## Help

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--engine` | `mermaid`, `excalidraw`, `drawio`, `graphviz` | auto-detect | Force a specific engine |
| `--type` | `flowchart`, `sequence`, etc. | auto-detect | Diagram type hint |
| `--render` | flag | off | Render to image |
| `--format` | `svg`, `png`, `jpeg`, `webp` | `svg` | Output format |
| `--help` | flag | off | Show help |

## Sub-Skills

| Skill | Description |
|-------|-------------|
| `/adk:diagram-mermaid` | Text-based diagrams. Best for flowcharts, sequence, ER, class, state, timeline, mindmap, Gantt, C4. |
| `/adk:diagram-excalidraw` | Hand-drawn feel. Best for architecture overviews, system context, freeform layouts. |
| `/adk:diagram-drawio` | Precise layout with rich icon library. Best for network topology, enterprise architecture, BPMN. |
| `/adk:diagram-graphviz` | Strict DOT layout. Best for dependency graphs, strict graph layout, existing `.dot` assets. |

## Adjacent Skills

- `/adk:docs-write` — documentation that may embed diagrams
- `/adk:plan` — planning workflows that may need architecture diagrams
- `/adk:spec` — specifications that may need visual documentation
