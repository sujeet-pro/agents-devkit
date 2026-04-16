# Diagram References

Use this folder when `adk-diagram` needs more than routing hints.

## Read Order

1. Start with `engines-and-types.md` to pick the engine and Mermaid type.
2. Read the matching engine guide:
   - `mermaid.md`
   - `excalidraw.md`
   - `drawio.md`
   - `graphviz.md`
3. Use `diagramkit-integration.md` for rendering details.
4. Use `markdown-integration.md` for doc embedding patterns.

## Engine Guides

| Engine | Guide | Use when |
| --- | --- | --- |
| Mermaid | `mermaid.md` | Text-first flow, sequence, state, ER, timeline, C4, chart-like, or other syntax-driven diagrams |
| Excalidraw | `excalidraw.md` | Freeform architecture overviews, hand-drawn explanation diagrams, and system-context visuals |
| Draw.io | `drawio.md` | Network topology, cloud infrastructure, BPMN, org charts, and layout-heavy enterprise diagrams |
| Graphviz | `graphviz.md` | Dependency graphs, call graphs, rank-constrained graphs, and existing `.dot` assets |

## Mermaid Types

The Mermaid guide includes build instructions for these types:

- `flowchart`
- `sequence`
- `class`
- `state`
- `er`
- `gantt`
- `gitgraph`
- `mindmap`
- `timeline`
- `c4`
- `pie`
- `quadrant`
- `sankey`
- `xy`
- `block`
- `architecture`
- `kanban`
- `journey`
- `packet`
- `radar`
- `requirement`

## Scope

These guides focus on how to build the source files correctly. Do not duplicate rendering commands here unless the engine has a source-format-specific caveat. Use `diagramkit-integration.md` for render behavior and `markdown-integration.md` for embeds.
