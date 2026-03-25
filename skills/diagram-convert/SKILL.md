---
name: diagram-convert
description: Convert engineering images and rendered diagrams to a destination-friendly raster format when markdown, Confluence, Google Docs, or PDF output requires it
user_invocable: true
arguments:
  - name: input
    description: "Path to the input image"
    required: true
  - name: output
    description: "Optional output path"
    required: false
  - name: quality
    description: "Output quality"
    required: false
  - name: density
    description: "Rasterization density"
    required: false
  - name: width
    description: "Optional output width"
    required: false
  - name: background
    description: "Optional background color"
    required: false
---

# Image Transform

Use `skills/_references/preflight-validations.md`.

## Preflight

Before converting a diagram or SVG asset, run:

`zsh scripts/check-skill-deps.zsh diagram-convert format=<format>`

If conversion depends on missing tooling, stop and show:

- `npm install -g diagramkit`
- `diagramkit warmup`
- `npm install -g sharp` for raster output

Prefer SVG unless the destination cannot render it reliably.

Use this for:

- Confluence
- Google Docs
- PDF export
- image-heavy delivery formats that require PNG or JPEG

Keep the original source asset alongside the converted image whenever possible.
