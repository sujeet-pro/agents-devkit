---
name: diagrams
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

`zsh scripts/check-skill-deps.zsh diagrams format=<format>`

If preflight fails, stop and show the exact commands needed:

- `npm install -g diagramkit`
- `diagramkit warmup`
- `npm install -g sharp` when `format` is `png`, `jpeg`, `jpg`, or `webp`

The user can run those commands manually, or approve the agent to run them automatically when the current host supports command approval.

## Required Child Agents

Run at least these child agents in parallel:

- a structure pass to identify entities, flows, and boundaries
- a notation pass to choose Mermaid, Excalidraw, draw.io, or Graphviz
- a validation pass to ensure the diagram matches the requested narrative and can be rendered cleanly

## Engine Rules

- Mermaid for text-first flows, sequence diagrams, ERDs, and diagrams that should diff well in Git.
- Excalidraw for architecture overviews, ownership maps, and exploratory documentation.
- draw.io for precise enterprise diagrams, network layouts, and BPMN-style structures.
- Graphviz only for existing DOT-based assets or when strict graph layout control is clearly worth the extra complexity.

Always keep the editable source file and at least one rendered output.
