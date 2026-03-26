---
name: diagram-mermaid
description: Use when Mermaid is the best fit for a text-first engineering diagram that should diff well in Git
user_invocable: true
arguments:
  - name: description
    description: "What to diagram"
    required: true
  - name: type
    description: "Mermaid diagram type: flowchart, sequence, class, state, er, gantt, journey, mindmap, timeline, c4, architecture, quadrant, sankey, block, pie, radar, xy, gitgraph, kanban, packet, requirement"
    required: false
  - name: theme
    description: "Theme: default, neutral, forest, dark, base (default: default)"
    required: false
  - name: format
    description: "Rendered format: svg, png, jpeg, webp (default: svg)"
    required: false
---

# Mermaid Diagram

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill for flowcharts, sequence diagrams, ERDs, class diagrams, state machines, and any text-first diagram that should diff well in Git. For freeform architecture overviews, use `/devkit:diagram-excalidraw`. For precise enterprise layouts, use `/devkit:diagram-drawio`.

## Preflight

Before generating source or rendering, run:

`zsh scripts/check-skill-deps.zsh diagram-mermaid format=<format>`

This must confirm:

- global `diagramkit` installed
- Playwright Chromium ready via `diagramkit warmup`
- global `sharp` when `format` is `png`, `jpeg`, `jpg`, or `webp`

If any check fails, stop and show the install commands before continuing.

## Reference Loading

Load the appropriate diagram type reference from `skills/diagram-mermaid/references/` based on the requested or inferred diagram type:

- `flowchart.md` for flowcharts and decision trees
- `sequence.md` for sequence diagrams
- `class.md` for class diagrams
- `state.md` for state machines
- `er.md` for entity-relationship diagrams
- `c4.md` for C4 model diagrams
- `architecture.md` for architecture diagrams
- `gantt.md` for Gantt charts
- `journey.md` for user journey maps
- `mindmap.md` for mind maps
- `timeline.md` for timelines
- `block.md` for block diagrams
- `quadrant.md` for quadrant charts
- `sankey.md` for Sankey diagrams
- `pie.md` for pie charts
- `radar.md` for radar charts
- `xy.md` for XY charts
- `gitgraph.md` for git graph diagrams
- `kanban.md` for Kanban boards
- `packet.md` for packet diagrams
- `requirement.md` for requirement diagrams

For theming, always load `skills/diagram-mermaid/references/theming.md`.

## Required Child Agents

Run at least these child agents in parallel:

- **Structure agent**: analyzes the description to identify entities, relationships, flows, and groupings. Determines the best Mermaid diagram type if not specified. Produces a structured outline of nodes, edges, and subgraphs.
- **Notation agent**: translates the structure into valid Mermaid syntax. Applies the requested theme. Uses the correct diagram type syntax from the loaded reference file. Ensures node IDs are clean, labels are readable, and the diagram follows Mermaid best practices.
- **Validation agent**: verifies the generated Mermaid source parses without errors, the diagram renders cleanly, labels do not overlap or truncate, and the visual output matches the requested description.

## Workflow

1. **Analyze requirements.** Read the description and determine the diagram type, entities, and relationships.
2. **Select diagram type.** If `type` is not specified, infer the best Mermaid diagram type from the description.
3. **Load references.** Read the matching diagram type reference and `theming.md` from `skills/diagram-mermaid/references/`.
4. **Launch child agents.** Run structure, notation, and validation passes in parallel.
5. **Merge and resolve.** Combine child-agent outputs, resolve syntax issues, and produce the final Mermaid source file.
6. **Render.** Use `diagramkit` to render the Mermaid source to the requested format (SVG by default) with the requested theme.
7. **Deliver both artifacts.** Save the editable Mermaid source (`.mmd` or `.mermaid`) and the rendered output side by side.

## Output

Produce both:

- the editable Mermaid source file (`.mmd` or `.mermaid`)
- at least one rendered artifact in the requested format (SVG preferred)

Keep both files together so the diagram remains editable for future changes.

## Adjacent Skills

- `/devkit:diagram` for automatic engine selection
- `/devkit:diagram-excalidraw` for freeform architecture overviews
- `/devkit:diagram-drawio` for precise enterprise and infrastructure layouts
- `/devkit:diagram-render` to re-render existing sources
- `/devkit:diagram-convert` for format conversion of rendered assets
