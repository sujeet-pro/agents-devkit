---
title: "diagram-excalidraw"
description: Create Excalidraw diagrams — hand-drawn style architecture overviews and freeform diagrams with light/dark mode
skill_name: diagram-excalidraw
category: task
workflow_tier: full
user_invocable: true
---

# diagram-excalidraw

Generate architecture diagrams, system overviews, and freeform diagrams as `.excalidraw` JSON files with a hand-drawn aesthetic. Writes a `.excalidraw` source file and renders to SVG/PNG with automatic light/dark mode variants via `diagramkit render`.

Can be invoked directly or via `/adk:diagram --engine excalidraw`.

## When to Use

- Create architecture overviews and system context diagrams
- Build freeform diagrams with a hand-drawn, whiteboard-like style
- Generate codebase or project structure visualizations
- Produce hub-and-spoke or hierarchical layout diagrams
- Create diagrams editable in the Excalidraw web app or VS Code extension
- Visualize cloud infrastructure with AWS, Azure, GCP, or Kubernetes color palettes

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<description>` | text or `analyze` | — | What to diagram. Use `analyze` to auto-discover components from the codebase |
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg` \| `png` | `svg` | Output image format |
| `--theme` | `both` \| `light` \| `dark` | `both` | Theme variants to render |
| `--palette` | `default` \| `aws` \| `azure` \| `gcp` \| `k8s` | `default` | Color palette for component types |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| `description=analyze` | Scans codebase to discover components (monorepo packages, microservices, IaC resources, API routes) and generates a diagram automatically |
| Description provided | Parses description to identify components, relationships, groupings, and selects the best layout pattern |
| `--palette aws` | Uses AWS service category colors (Compute orange, Storage green, Database blue, etc.) |
| `--palette k8s` | Uses Kubernetes component colors (Pod blue, Ingress teal, Namespace gray, etc.) |
| Invoked by `/adk:diagram` | Receives forwarded parameters, runs in `--auto` mode |

## Priorities

The skill focuses on producing correct, visually clean Excalidraw JSON:

1. **JSON validity** — well-formed `.excalidraw` JSON that loads in any Excalidraw viewer
2. **Label rendering** — every labeled shape uses two elements (shape + text with `containerId`), never the `label` property
3. **Arrow routing** — elbow arrows with correct edge calculations, no floating endpoints
4. **Layout clarity** — consistent spacing, aligned elements, logical grouping with dashed rectangles
5. **Palette consistency** — same colors for same component types throughout the diagram

## Key Behaviors

- **Codebase analysis mode**: scans for `package.json`, `Dockerfile`, Terraform resources, route definitions, and component hierarchies to auto-discover architecture
- **Three layout patterns**: vertical flow (hierarchies), horizontal flow (pipelines), hub-and-spoke (event-driven)
- **No diamond shapes**: diamonds have broken arrow connections in raw JSON; uses styled rectangles instead
- **Two-element labels**: shape element with `boundElements` + separate text element with `containerId` (the `label` property does not work in raw JSON)
- **Elbow arrows**: requires all three properties (`elbowed: true`, `roundness: null`, `roughness: 0`) for 90-degree corners
- **Arrow staggering**: when multiple arrows leave the same edge, spreads them evenly across 20%-80% of the edge
- **Semantic IDs**: `express-api` not `node-1`, with text elements using `{shape-id}-text` convention

## Workflow

Follows the 6-phase workflow with complexity-adaptive phase skipping.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm components, scope, layout pattern, palette, output location |
| 1. Research & Options | yes | Analyze requirements or scan codebase; determine structure and layout |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Generate `.excalidraw` JSON file with all elements, arrows, and groups |
| 5. Validate & Learn | yes | Render to SVG/PNG (light+dark), verify renderability, naming, consistency |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before rendering | Run preflight.py, validate diagramkit and npm packages |
| `output-format` | producing output | short/standard/detailed verbosity; keep source + rendered files |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | complexity >= medium AND parallel work | Launch 2+ child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |
| `workspace-conventions` | always | Diagrams in `diagrams/`, both light+dark SVG and PNG, respect `diagramkit.config.json` |

## Output Format

All output includes:

- `.excalidraw` JSON source file (editable in Excalidraw web app or VS Code extension)
- Rendered images (when `--render` is used):
  - `<name>-light.svg` and `<name>-dark.svg`
  - `<name>-light.png` and `<name>-dark.png`
- Completion report with file paths and instructions to open in Excalidraw

Rendering uses `diagramkit render` (primary) or `@excalidraw/utils` with a Node.js script (fallback). Dark mode uses diagramkit's `postProcessDarkSvg` for WCAG-compliant contrast on dark surfaces.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:diagram` | Let the router auto-detect the best engine |
| `/adk:diagram-mermaid` | Text-based diagrams (flowcharts, sequence, ER, Gantt, C4) |
| `/adk:diagram-drawio` | Precise layout with rich icon library (AWS, Azure, GCP shapes) |
| `/adk:diagram-graphviz` | Strict algorithmic layout for dependency graphs |
| `/adk:docs-write` | Documentation that may embed diagrams |

## Examples

```
/adk:diagram-excalidraw "microservices architecture overview"
/adk:diagram-excalidraw analyze
/adk:diagram-excalidraw "system context diagram for payment service"
/adk:diagram-excalidraw --palette aws "AWS infrastructure layout"
/adk:diagram-excalidraw --palette k8s "Kubernetes cluster topology"
/adk:diagram-excalidraw --render --format png "data pipeline architecture"
/adk:diagram-excalidraw --theme dark "event-driven architecture"
/adk:diagram-excalidraw --help
```
