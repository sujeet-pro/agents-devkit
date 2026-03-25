---
name: diagramkit
description: Render Mermaid, Excalidraw, and draw.io sources to images while preserving editable sources and destination-appropriate formats
user_invocable: true
arguments:
  - name: command
    description: "Command: render, warmup, init"
    required: true
  - name: target
    description: "File or directory to render"
    required: false
  - name: format
    description: "Rendered format: svg, png, jpeg, webp (default: svg)"
    required: false
  - name: theme
    description: "Theme: light, dark, both (default: both)"
    required: false
---

# Diagram Render

Use `skills/_references/preflight-validations.md`.

## Preflight

Before any render, run:

`zsh scripts/check-skill-deps.zsh diagramkit format=<format>`

If the check fails, stop and show the install commands instead of attempting a partial render:

- `npm install -g diagramkit`
- `diagramkit warmup`
- `npm install -g sharp` for raster output

Treat rendering as a validation step, not just a conversion step.

Run in parallel:

- a source integrity pass
- a render pass
- an output-fit pass that checks whether the chosen format matches the destination

Prefer SVG. Use PNG or JPEG only when the destination cannot reliably handle SVG.
