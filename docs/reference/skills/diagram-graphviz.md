---
title: "diagram-graphviz"
description: Create Graphviz DOT diagrams — WASM-based rendering for dependency graphs
skill_name: diagram-graphviz
category: task
workflow_tier: full
---

# diagram-graphviz

Creates Graphviz DOT source files with strict layout algorithms for dependency graphs, call graphs, and hierarchical visualizations. Renders via WASM (no browser needed).

## When to Use

- Module or package dependency graphs
- Function call graphs
- Hierarchical or radial layouts
- Existing `.dot` files that need updating

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--render` | flag | auto | Render to image |
| `--format` | `svg`, `png` | `svg` | Render output format |
| `--theme` | `light`, `dark` | `light` | Color theme |
| `--layout` | `dot`, `neato`, `fdp`, `sfdp`, `circo`, `twopi` | `dot` | Layout algorithm |
| `--help` | flag | — | Show parameters |

### Layout Algorithms

| Algorithm | Best For |
|-----------|----------|
| `dot` | Hierarchical (top-to-bottom trees, DAGs) |
| `neato` | Force-directed (small to medium graphs) |
| `fdp` | Force-directed (alternative, handles clusters) |
| `sfdp` | Scalable force-directed (large graphs) |
| `circo` | Circular layout |
| `twopi` | Radial layout from a root node |

## Workflow

Phases 2–3 skipped.

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm diagram scope |
| 1. Research | Load DOT syntax reference |
| 4. Execute | Generate `.dot` source, render if requested |
| 5. Validate | Verify DOT syntax is valid |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `workspace-conventions`.

## Examples

```text
/adk:diagram-graphviz module dependency graph for the Python packages
/adk:diagram-graphviz --layout neato network topology with force-directed layout
/adk:diagram-graphviz --layout circo circular dependency visualization
/adk:diagram-graphviz --render --format png --theme dark call graph
```
