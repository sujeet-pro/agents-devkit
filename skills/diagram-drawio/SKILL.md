---
name: diagram-drawio
description: Use when draw.io is the best fit for a precise engineering, infrastructure, or process diagram
user_invocable: true
arguments:
  - name: description
    description: "What to diagram"
    required: true
  - name: style
    description: "Style: default, sketch, minimal (default: default)"
    required: false
  - name: format
    description: "Rendered format: svg, png, jpeg, webp (default: svg)"
    required: false
---

# draw.io Diagram

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the diagram needs precise positioning, enterprise layouts, network topologies, or BPMN-style process flows. For text-first diagrams that should diff well in Git, use `/devkit:diagram-mermaid`. For freeform architecture overviews, use `/devkit:diagram-excalidraw`.

## Preflight

Before generating source or rendering, run:

`zsh scripts/check-skill-deps.zsh diagram-drawio format=<format>`

This must confirm:

- global `diagramkit` installed
- Playwright Chromium ready via `diagramkit warmup`
- global `sharp` when `format` is `png`, `jpeg`, `jpg`, or `webp`

If any check fails, stop and show the install commands before continuing.

## Reference Loading

Load references from `skills/diagram-drawio/references/`:

- `shapes.md` for available shapes, stencils, and container patterns
- `styles.md` for styling conventions, colors, and line weights

## Required Child Agents

Run at least these child agents in parallel:

- **Structure agent**: analyzes the description to identify entities, relationships, groupings, and flow direction. Determines which draw.io shapes, containers, and connectors to use. Produces a structured outline of elements and their connections.
- **Notation agent**: translates the structure into valid draw.io XML. Applies the requested style (default, sketch, or minimal). Sets positioning, sizing, and connector routing. References `shapes.md` and `styles.md` for correct element types.
- **Validation agent**: verifies the generated `.drawio` XML is well-formed, all connectors reference valid elements, the diagram renders without errors, and the visual layout matches the requested description.

## Workflow

1. **Analyze requirements.** Read the description and determine the diagram's scope, entities, and relationships.
2. **Load references.** Read `shapes.md` and `styles.md` from `skills/diagram-drawio/references/`.
3. **Launch child agents.** Run structure, notation, and validation passes in parallel.
4. **Merge and resolve.** Combine child-agent outputs, resolve conflicts, and produce the final `.drawio` source file.
5. **Render.** Use `diagramkit` to render the `.drawio` source to the requested format (SVG by default).
6. **Deliver both artifacts.** Save the editable `.drawio` source and the rendered output side by side.

## Output

Produce both:

- the editable `.drawio` source file
- at least one rendered artifact in the requested format (SVG preferred)

Keep both files together so the diagram remains editable for future changes.

## Adjacent Skills

- `/devkit:diagram` for automatic engine selection
- `/devkit:diagram-mermaid` for text-first diagrams that diff well in Git
- `/devkit:diagram-excalidraw` for freeform architecture overviews
- `/devkit:diagram-render` to re-render existing sources
- `/devkit:diagram-convert` for format conversion of rendered assets
