---
title: "diagram-mermaid"
description: Create Mermaid diagrams with full syntax reference for all 21 diagram types, with light/dark mode rendering via diagramkit
skill_name: diagram-mermaid
category: task
workflow_tier: full
user_invocable: true
---

# diagram-mermaid

Create diagrams using Mermaid v11 syntax. Supports 21 diagram types with a full syntax reference for each. Writes a `.mermaid` source file and renders to SVG/PNG with automatic light/dark mode variants via `diagramkit render`.

Can be invoked directly or via `/adk:diagram --engine mermaid`. Accepted file extensions: `.mermaid`, `.mmd`, `.mmdc`.

## When to Use

- Create flowcharts, sequence diagrams, class diagrams, state machines, or ER diagrams
- Generate Gantt charts, timelines, mindmaps, or journey maps
- Build C4 architecture diagrams or gitgraph visualizations
- Create any of the 21 supported Mermaid diagram types
- Produce text-based diagrams that render consistently across platforms
- Add diagrams to documentation with both light and dark mode support

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<description>` | text | — | What to diagram. Natural language description |
| `--type` | `flowchart` \| `sequence` \| `class` \| `state` \| `er` \| `gantt` \| `gitgraph` \| `mindmap` \| `timeline` \| `c4` \| `architecture` \| `kanban` \| `quadrant` \| `sankey` \| `xy` \| `packet` \| `radar` \| `journey` \| `pie` \| `requirement` \| `block` | auto-detect | Diagram type. Auto-detected from description if omitted |
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg` \| `png` | `svg` | Output image format |
| `--theme` | `both` \| `light` \| `dark` | `both` | Theme variants to render |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| `--type` provided | Uses the specified diagram type directly |
| No `--type` | Auto-detects type from the description (e.g., "process flow" → flowchart, "API calls" → sequence) |
| `--render` | Generates source then renders via diagramkit; falls back to `mmdc` CLI if diagramkit unavailable |
| Invoked by `/adk:diagram` | Receives forwarded parameters, runs in `--auto` mode |

## Priorities

The skill focuses on producing correct, readable Mermaid diagrams:

1. **Syntax correctness** — valid Mermaid v11 syntax that renders without errors
2. **Readability** — clear flow direction, semantic node IDs, descriptive labels
3. **Styling** — consistent use of `classDef` for repeated styles, hex-only colors
4. **Scope** — max ~15 nodes per diagram; complex systems split into focused diagrams
5. **Theming** — colors designed to work with diagramkit's dark mode post-processing

## Key Behaviors

- **Type auto-detection**: infers diagram type from description keywords when `--type` is omitted
- **Type-specific reference loading**: loads only the matching type reference file for correct syntax
- **Semantic IDs**: uses `api_gateway` not `A`, for readable and maintainable source
- **Subgraph grouping**: groups 3+ related nodes with subgraphs
- **Edge styling conventions**: solid for sync, dotted for async, thick for critical path
- **File header comment**: every file starts with `%% Diagram: <title>` and `%% Type: <diagram-type>`
- **Reserved word handling**: quotes Mermaid reserved words (`end`, `default`) to prevent parse errors

## Supported Diagram Types

| Type | Best For |
|------|----------|
| `flowchart` | Process flows, workflows, pipelines, decision trees |
| `sequence` | Message passing, API calls, protocol exchanges |
| `class` | OOP class hierarchies, interfaces, relationships |
| `state` | State machines, status transitions |
| `er` | Database entity relationships |
| `gantt` | Project timelines, task scheduling |
| `mindmap` | Concept maps, brainstorming |
| `timeline` | Historical events, release timelines |
| `c4` | C4 architecture diagrams |
| `pie` | Pie/donut charts |
| `quadrant` | Priority/evaluation matrices |
| `sankey` | Flow/resource distribution |
| `xy` | XY scatter/line/bar charts |
| `block` | Block diagrams |
| `architecture` | Architecture icon diagrams |
| `gitgraph` | Git branch visualization |
| `journey` | User journey maps |
| `kanban` | Kanban boards |
| `packet` | Network packet diagrams |
| `radar` | Radar/spider charts |
| `requirement` | Requirement diagrams |

## Workflow

Follows the 6-phase workflow with complexity-adaptive phase skipping.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm diagram type, scope, and audience |
| 1. Research & Options | yes | Analyze requirements, determine structure and layout direction |
| 2. Approach Selection | skip | Direct execution after confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Generate `.mermaid` source file using type-specific syntax reference |
| 5. Validate & Learn | yes | Render to SVG/PNG (light+dark), verify renderability, naming, consistency |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before rendering | Run preflight.py, validate diagramkit and npm packages |
| `output-format` | producing output | short/standard/detailed verbosity; keep source + rendered files |
| `workspace-conventions` | always | Diagrams in `diagrams/`, both light+dark SVG and PNG, respect `diagramkit.config.json` |

## Output Format

All output includes:

- `.mermaid` source file with header comments (`%% Diagram:` and `%% Type:`)
- Rendered images (when `--render` is used):
  - `<name>-light.svg` and `<name>-dark.svg`
  - `<name>-light.png` and `<name>-dark.png`
- Completion report listing all generated files

Rendering uses `diagramkit render` (primary) or `mmdc` from `@mermaid-js/mermaid-cli` (fallback). Dark mode uses diagramkit's `postProcessDarkSvg` for WCAG-compliant contrast.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:diagram` | Let the router auto-detect the best engine |
| `/adk:diagram-excalidraw` | Hand-drawn architecture overviews and freeform layouts |
| `/adk:diagram-drawio` | Precise layout with rich icon library (AWS, Azure, GCP shapes) |
| `/adk:diagram-graphviz` | Strict algorithmic layout for dependency graphs |
| `/adk:docs-write` | Documentation that may embed diagrams |

## Examples

```
/adk:diagram-mermaid "user registration flow"
/adk:diagram-mermaid --type sequence "OAuth2 authorization code flow"
/adk:diagram-mermaid --type er "e-commerce database schema"
/adk:diagram-mermaid --type gantt "Q2 release schedule"
/adk:diagram-mermaid --type c4 "payment service context"
/adk:diagram-mermaid --type state "order lifecycle"
/adk:diagram-mermaid --type mindmap "frontend architecture decisions"
/adk:diagram-mermaid --type gitgraph "release branching strategy"
/adk:diagram-mermaid --render --format png "CI/CD pipeline"
/adk:diagram-mermaid --help
```
