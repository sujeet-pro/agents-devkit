---
name: image-convert
description: Convert rendered engineering diagrams to raster output only when a destination such as Confluence or Google Docs requires it
user_invocable: true
arguments:
  - name: input
    description: "Input diagram or rendered asset"
    required: true
  - name: format
    description: "Raster format: png, jpeg, webp (default: png)"
    required: false
  - name: quality
    description: "Quality 1-100"
    required: false
  - name: scale
    description: "Scale factor"
    required: false
---

# Image Convert

Use `skills/_references/preflight-validations.md`.

## Preflight

Before raster conversion, run:

`zsh scripts/check-skill-deps.zsh image-convert format=<format>`

This must confirm:

- global `diagramkit`
- Playwright Chromium ready through `diagramkit warmup`
- global `sharp` for the requested raster format

If any check fails, stop and show the install commands before continuing.

Keep the source diagram and the SVG render. Use raster output only for destinations that need it.
