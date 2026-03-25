---
name: diagram-graphviz
description: Use when you need to create or maintain Graphviz DOT diagrams, usually for existing `.dot` assets or layouts that Mermaid, Excalidraw, or draw.io cannot express cleanly
user_invocable: true
arguments:
  - name: target
    description: "Existing .dot file, SKILL.md directory with ```dot blocks, or output location"
    required: false
  - name: description
    description: "What to diagram when creating a new Graphviz asset"
    required: false
  - name: format
    description: "Rendered format: svg, png, jpeg, webp (default: svg)"
    required: false
---

# Graphviz Diagram

Prefer `/devkit:diagram`, `/devkit:diagram-mermaid`, `/devkit:diagram-excalidraw`, or `/devkit:diagram-drawio` for new documentation work. Use this skill when the repository already uses Graphviz or when strict DOT layout control is clearly the best fit.

## Preflight

Before drafting or rendering Graphviz assets, run:

`zsh scripts/check-skill-deps.zsh diagram-graphviz format=<format>`

If rendering is required, ensure `dot` is available. Prefer SVG unless the destination requires a raster format.

## Included Helpers

- `scripts/render-graphs.js` extracts `dot` blocks from a skill and renders them
- `references/graphviz-conventions.dot` captures the Graphviz style guide used by this repo

## Rules

- Keep Graphviz usage intentional and limited.
- Do not choose Graphviz by default when Mermaid, Excalidraw, or draw.io would be easier to maintain.
- When updating existing `.dot` assets, preserve their current conventions unless the caller asks for a cleanup.
