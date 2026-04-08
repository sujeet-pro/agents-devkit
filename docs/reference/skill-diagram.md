---
title: "diagram"
description: Diagram router — auto-detects the best engine and routes to the right diagram skill
skill_name: diagram
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# diagram

Unified entry point for diagram creation. Auto-detects the best rendering engine from context signals and routes to the engine-specific skill, or accepts an explicit `--engine` override. Passes all parameters through to the target skill.

## When to Use

- Create any type of diagram without knowing which engine is best
- Let the router pick the optimal engine based on diagram type and project context
- Generate flowcharts, sequence diagrams, architecture overviews, network topologies, or dependency graphs
- Maintain consistency with existing diagram formats in the project

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<description>` | text | — | What to diagram. Natural language description of the desired diagram |
| `--engine` | `mermaid` \| `excalidraw` \| `drawio` \| `graphviz` | auto-detect | Force a specific rendering engine. Bypasses auto-detection |
| `--type` | `flowchart`, `sequence`, `class`, `state`, `er`, `gantt`, `mindmap`, `timeline`, `c4`, `freeform`, `network`, `architecture`, etc. | auto-detect | Diagram type hint used for engine selection and forwarded to the target skill |
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg` \| `png` | `svg` | Output image format (both SVG and PNG produced by default) |
| `--theme` | `both` \| `light` \| `dark` | `both` | Theme variants to render |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| `--engine` provided | Routes directly to the specified engine skill, no auto-detection |
| `--type=freeform` or "architecture overview" | Routes to `/adk:diagram-excalidraw` |
| `--type=network` with "topology", "rack", "physical" | Routes to `/adk:diagram-drawio` |
| BPMN, org chart, or multi-page requested | Routes to `/adk:diagram-drawio` |
| Existing `.dot` files in project or "dependency graph" | Routes to `/adk:diagram-graphviz` |
| Flowchart, sequence, class, ER, Gantt, C4, or other standard types | Routes to `/adk:diagram-mermaid` |
| No clear signal | Defaults to Mermaid (highest preference) |

## Routing Logic

The router uses a priority-ordered set of signals to select the best engine.

### Engine Selection Rules

| Priority | Signal | Engine |
|----------|--------|--------|
| 1 | `--type=freeform` | Excalidraw |
| 2 | `--type=network` with "topology", "rack", "physical" | Draw.io |
| 3 | `--type=architecture` with "overview", "high-level", "system context" | Excalidraw |
| 4 | `--type=architecture` with "AWS", "Azure", "GCP" + "detailed" | Draw.io |
| 5 | `--type` is `sequence`, `class`, `state`, `er`, `gantt`, `gitgraph`, `mindmap`, `timeline`, `kanban`, `quadrant`, `sankey`, `xy`, `packet`, `radar`, `journey`, `c4` | Mermaid |
| 6 | "BPMN", "business process", "org chart", "multi-page" | Draw.io |
| 7 | "codebase", "project structure", "repo overview" | Excalidraw |
| 8 | "flowchart", "process", "workflow", "pipeline", "decision tree" | Mermaid |
| 9 | Default (no signal matches) | Mermaid |

### Context Signals

The router checks for existing diagram files in the project (`.mmd`, `.mermaid`, `.excalidraw`, `.drawio`, `.dot`) and prefers that engine for consistency with the existing codebase.

### Default Preference Order

Mermaid > Excalidraw > Draw.io > Graphviz

### Parameter Forwarding

The router does not consume parameters except `--engine` and `--help`. All other parameters are forwarded to the target engine skill.

## Downstream Skills

| Skill | Engine | Best For |
|-------|--------|----------|
| `/adk:diagram-mermaid` | Mermaid | Flowcharts, sequence, ER, class, state, timeline, mindmap, Gantt, C4. Text-based, 21 diagram types |
| `/adk:diagram-excalidraw` | Excalidraw | Architecture overviews, system context, freeform layouts. Hand-drawn style |
| `/adk:diagram-drawio` | Draw.io | Network topology, enterprise architecture, BPMN, multi-page. Rich icon library with precise layout |
| `/adk:diagram-graphviz` | Graphviz | Dependency graphs, call trees, strict graph layout. WASM-based rendering, existing `.dot` assets |

## Workspace Conventions

- **Output location**: `diagrams/` folder sibling to the document (if doc-related), or `./diagrams/` at project root
- **diagramkit.config.json**: If present at project root, use its settings for output directory, format, and theme
- **Theme**: Both light and dark variants produced by default (`--theme both`)
- **Formats**: SVG (vector) and PNG (raster) output
- **Temp files**: `.temp/<task-slug>/` for intermediary artifacts (gitignored)
- **Source files**: Always committed alongside rendered output

## Output Format

The router itself produces no output — it delegates entirely to the selected engine skill. Each engine skill produces:

- Editable source file (`.mermaid`, `.excalidraw`, `.drawio`, `.dot`)
- Rendered images: `<name>-light.svg`, `<name>-dark.svg`, `<name>-light.png`, `<name>-dark.png`

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:diagram-mermaid` | When you know you want a Mermaid diagram |
| `/adk:diagram-excalidraw` | When you know you want an Excalidraw diagram |
| `/adk:diagram-drawio` | When you know you want a draw.io diagram |
| `/adk:diagram-graphviz` | When you know you want a Graphviz diagram |
| `/adk:docs-write` | Documentation that may embed diagrams |
| `/adk:plan` | Planning workflows that may need architecture diagrams |
| `/adk:spec` | Specifications that may need visual documentation |

## Examples

```
/adk:diagram "user authentication flow"
/adk:diagram "microservices architecture overview"
/adk:diagram --engine mermaid "CI/CD pipeline"
/adk:diagram --engine excalidraw "system context diagram"
/adk:diagram --engine drawio "AWS network topology"
/adk:diagram --engine graphviz "module dependency graph"
/adk:diagram --type sequence "API request lifecycle"
/adk:diagram --type c4 "system context"
/adk:diagram --render --format png "deployment architecture"
/adk:diagram --help
```
