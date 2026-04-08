---
title: "diagram-graphviz"
description: Create Graphviz DOT diagrams — strict algorithmic layout for dependency graphs and existing .dot assets
skill_name: diagram-graphviz
category: task
workflow_tier: full
user_invocable: true
---

# diagram-graphviz

Create diagrams using Graphviz DOT language with strict algorithmic layout control. Best for dependency graphs, call trees, and working with existing `.dot` assets. Uses WASM-based rendering — no browser or local Graphviz install required.

Can be invoked directly or via `/adk:diagram --engine graphviz`. Accepted file extensions: `.dot`, `.gv`.

## When to Use

- Generate dependency graphs or module relationship diagrams
- Create call trees or data flow graphs with automatic layout
- Work with existing `.dot` files in the repository
- Need strict algorithmic layout control (rank constraints, ports, record nodes)
- Build state machine or automata diagrams
- Produce graphs where automatic layout excels over manual positioning

Prefer Mermaid, Excalidraw, or draw.io for new documentation work. Use Graphviz specifically when the repository already uses `.dot` files, you need strict layout control, or the diagram is a pure dependency/call graph.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<description>` | text | — | What to diagram. Natural language description |
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg` \| `png` | `svg` | Output image format |
| `--theme` | `both` \| `light` \| `dark` | `both` | Theme variants to render |
| `--layout` | `dot` \| `neato` \| `fdp` \| `sfdp` \| `circo` \| `twopi` | `dot` | Layout engine algorithm |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| Existing `.dot` files in project | Reads and preserves existing conventions unless cleanup is requested |
| `--layout dot` (default) | Hierarchical/directed layout via Sugiyama algorithm. Best for DAGs and call trees |
| `--layout neato` | Spring model layout for undirected graphs and network topologies |
| `--layout fdp` | Force-directed placement for large undirected graphs |
| `--layout sfdp` | Scalable force-directed for very large graphs (1000+ nodes) |
| `--layout circo` | Circular layout for ring topologies |
| `--layout twopi` | Radial layout for hub-and-spoke patterns |
| Invoked by `/adk:diagram` | Receives forwarded parameters, runs in `--auto` mode |

## Priorities

The skill focuses on producing correct, well-structured DOT source:

1. **Layout correctness** — proper use of rank constraints, edge weights, and layout engine for the graph type
2. **Readability** — semantic node IDs, descriptive labels, consistent styling
3. **Dark mode compatibility** — mid-tone fills, `fontcolor="#333333"`, `bgcolor="transparent"`
4. **Cluster organization** — related nodes grouped in `cluster_` subgraphs
5. **Graph-level defaults** — `node` and `edge` defaults set at graph level to reduce repetition

## Key Behaviors

- **Six layout engines**: `dot` (hierarchical), `neato` (spring), `fdp` (force-directed), `sfdp` (scalable), `circo` (circular), `twopi` (radial)
- **WASM rendering**: diagramkit uses WASM-based Graphviz — no browser, no local `dot` binary required
- **Dark mode adaptation**: `adaptGraphvizSvgForDarkMode` swaps default black strokes/text for dark-surface colors, adjusts fill luminance using WCAG threshold of 0.4
- **Rank constraints**: `rank=same`, `rank=min`, `rank=max` for precise vertical alignment
- **Record and port nodes**: structured data nodes with named ports for precise edge connections
- **Subgraph clusters**: names starting with `cluster_` render as grouped boxes
- **Invisible edges**: `style=invis` edges for layout control without visual clutter

## Layout Engines

| Engine | Best For | Algorithm |
|--------|----------|-----------|
| `dot` | Hierarchical/directed graphs, DAGs, call trees | Sugiyama layered layout |
| `neato` | Undirected graphs, network topologies | Spring model (Kamada-Kawai) |
| `fdp` | Large undirected graphs | Force-directed placement |
| `sfdp` | Very large graphs (1000+ nodes) | Scalable force-directed |
| `circo` | Circular layouts, ring topologies | Circular layout |
| `twopi` | Radial layouts, hub-and-spoke | Radial layout |

## Workflow

Follows the 6-phase workflow with complexity-adaptive phase skipping.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm graph type, nodes, edges, layout engine, whether updating existing files |
| 1. Research & Options | yes | Read existing `.dot` files; determine nodes, edges, clusters, best layout engine |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Generate `.dot` source file with proper attributes and layout |
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

- `.dot` source file with graph-level defaults and semantic node IDs
- Rendered images (when `--render` is used):
  - `<name>-light.svg` and `<name>-dark.svg`
  - `<name>-light.png` and `<name>-dark.png`
- Completion report listing all generated files

Rendering uses `diagramkit render` (primary, WASM-based) or the Graphviz `dot` CLI (fallback, requires local install via `brew install graphviz` or `apt-get install graphviz`). Dark mode uses `adaptGraphvizSvgForDarkMode` with WCAG luminance threshold adjustments.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:diagram` | Let the router auto-detect the best engine |
| `/adk:diagram-mermaid` | Text-based diagrams (flowcharts, sequence, ER, Gantt, C4) |
| `/adk:diagram-excalidraw` | Hand-drawn architecture overviews and freeform layouts |
| `/adk:diagram-drawio` | Precise layout with rich icon library (AWS, Azure, GCP shapes) |
| `/adk:docs-write` | Documentation that may embed diagrams |

## Examples

```
/adk:diagram-graphviz "module dependency graph"
/adk:diagram-graphviz --layout neato "network topology"
/adk:diagram-graphviz --layout circo "ring protocol participants"
/adk:diagram-graphviz --layout twopi "event hub with consumers"
/adk:diagram-graphviz --layout sfdp "large-scale dependency graph"
/adk:diagram-graphviz --render --format png "call tree for auth module"
/adk:diagram-graphviz --theme dark "state machine for order lifecycle"
/adk:diagram-graphviz --help
```
