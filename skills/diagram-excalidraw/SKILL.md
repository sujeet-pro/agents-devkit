---
name: diagram-excalidraw
description: Use when Excalidraw is the best fit for a software architecture, ownership, or freeform engineering diagram
user_invocable: true
arguments:
  - name: description
    description: "What to diagram"
    required: true
  - name: palette
    description: "Palette: default, aws, azure, gcp, kubernetes (default: default)"
    required: false
  - name: style
    description: "Style: hand-drawn, clean (default: hand-drawn)"
    required: false
  - name: format
    description: "Rendered format: svg, png, jpeg, webp (default: svg)"
    required: false
---

# Excalidraw Diagram

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill for architecture overviews, ownership maps, system context diagrams, and exploratory documentation where a hand-drawn aesthetic aids readability. For precise enterprise layouts, use `/devkit:diagram-drawio`. For text-first diagrams, use `/devkit:diagram-mermaid`.

## Preflight

Before generating source or rendering, run:

`zsh scripts/check-skill-deps.zsh diagram-excalidraw format=<format>`

This must confirm:

- global `diagramkit` installed
- Playwright Chromium ready via `diagramkit warmup`
- global `sharp` when `format` is `png`, `jpeg`, `jpg`, or `webp`

If any check fails, stop and show the install commands before continuing.

## Reference Loading

Load references from `skills/diagram-excalidraw/references/`:

- `json-format.md` for the Excalidraw JSON element structure
- `arrows.md` for connection and arrow types
- `colors.md` for palette conventions and cloud-provider color schemes
- `examples.md` for common architecture and flow patterns
- `validation.md` for pre-render validation checks

When `palette` is set to a cloud provider (aws, azure, gcp, kubernetes), use the corresponding color scheme from `colors.md`.

## Required Child Agents

Run at least these child agents in parallel:

- **Structure agent**: analyzes the description to identify components, services, boundaries, ownership zones, and data flows. Determines grouping and spatial layout. Produces a structured outline of elements and their relationships.
- **Notation agent**: translates the structure into valid Excalidraw JSON. Applies the requested style (hand-drawn or clean) and palette. Uses appropriate shapes (rectangles for services, ellipses for data stores, arrows for flows). References `json-format.md`, `arrows.md`, and `colors.md`.
- **Validation agent**: verifies the generated `.excalidraw` JSON is valid, all arrows reference existing elements, the layout is readable without overlapping labels, and the diagram matches the requested description. Uses `validation.md` checks.

## Workflow

1. **Analyze requirements.** Read the description and determine the diagram's scope, components, and relationships.
2. **Load references.** Read the appropriate reference files from `skills/diagram-excalidraw/references/`.
3. **Launch child agents.** Run structure, notation, and validation passes in parallel.
4. **Merge and resolve.** Combine child-agent outputs, resolve layout conflicts, and produce the final `.excalidraw` source file.
5. **Render.** Use `diagramkit` to render the `.excalidraw` source to the requested format (SVG by default).
6. **Deliver both artifacts.** Save the editable `.excalidraw` source and the rendered output side by side.

## Output

Produce both:

- the editable `.excalidraw` source file
- at least one rendered artifact in the requested format (SVG preferred)

Keep both files together so the diagram remains editable for future changes.

## Adjacent Skills

- `/devkit:diagram` for automatic engine selection
- `/devkit:diagram-mermaid` for text-first diagrams that diff well in Git
- `/devkit:diagram-drawio` for precise enterprise and infrastructure layouts
- `/devkit:diagram-render` to re-render existing sources
- `/devkit:diagram-convert` for format conversion of rendered assets
