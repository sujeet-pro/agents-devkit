---
name: diagram
description: Use when you need DevKit to choose the best-fit diagram engine, preferring Mermaid, Excalidraw, or draw.io and falling back to Graphviz only when appropriate
user_invocable: true
arguments:
  - name: description
    description: "What to diagram"
    required: true
  - name: type
    description: "Optional type such as architecture, sequence, flowchart, er, c4, deployment, network"
    required: false
  - name: engine
    description: "Engine: auto, mermaid, excalidraw, drawio, graphviz (default: auto)"
    required: false
  - name: format
    description: "Rendered format: svg, png, jpeg, webp (default: svg)"
    required: false
---

# Diagrams

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

## Preflight

Before selecting an engine or drafting source, run:

`zsh scripts/check-skill-deps.zsh diagram format=<format>`

If preflight fails, stop and show the exact commands needed:

- `npm install -g diagramkit`
- `diagramkit warmup`
- `npm install -g sharp` when `format` is `png`, `jpeg`, `jpg`, or `webp`

The user can run those commands manually, or approve the agent to run them automatically when the current host supports command approval.

## Required Child Agents

Run at least these child agents in parallel:

- **Structure agent**: analyzes the description to identify entities, flows, boundaries, and groupings. Produces a structured outline of elements and their relationships.
- **Notation agent**: selects the best-fit engine (Mermaid, Excalidraw, draw.io, or Graphviz) based on the engine rules below and the diagram type. Translates the structure into valid source for the chosen engine.
- **Validation agent**: verifies the generated source is syntactically valid, renders without errors, and the visual output matches the requested description.

## Engine Rules

- Mermaid for text-first flows, sequence diagrams, ERDs, and diagrams that should diff well in Git.
- Excalidraw for architecture overviews, ownership maps, and exploratory documentation.
- draw.io for precise enterprise diagrams, network layouts, and BPMN-style structures.
- Graphviz only for existing DOT-based assets or when strict graph layout control is clearly worth the extra complexity.

## Workflow

1. **Analyze requirements.** Read the description and determine the diagram's scope, entities, and relationships.
2. **Select engine.** If `engine=auto`, use the engine rules to choose the best fit. Otherwise use the specified engine.
3. **Delegate to engine skill.** Route to the engine-specific skill (`/devkit:diagram-mermaid`, `/devkit:diagram-excalidraw`, `/devkit:diagram-drawio`, or `/devkit:diagram-graphviz`) with the description and format.
4. **Launch child agents.** Run structure, notation, and validation passes in parallel.
5. **Render.** Use `diagramkit` to render the source to the requested format (SVG by default).
6. **Deliver both artifacts.** Save the editable source file and the rendered output side by side.

## Output

Produce both:

- the editable diagram source file in the chosen engine's format
- at least one rendered artifact in the requested format (SVG preferred)

Always keep both files together so the diagram remains editable for future changes.

## Adjacent Skills

- `/devkit:diagram-mermaid` for text-first diagrams
- `/devkit:diagram-excalidraw` for freeform architecture overviews
- `/devkit:diagram-drawio` for precise enterprise layouts
- `/devkit:diagram-graphviz` for existing DOT assets
- `/devkit:diagram-render` to re-render existing sources
- `/devkit:diagram-convert` for format conversion of rendered assets
