---
name: diagram-raster
description: Use when you need to render a diagram source file to raster output (PNG, JPEG, WebP) for destinations that cannot handle SVG
user_invocable: true
arguments:
  - name: input
    description: "Input diagram source file (.mmd, .mermaid, .excalidraw, .drawio, .dot)"
    required: true
  - name: format
    description: "Raster format: png, jpeg, webp (default: png)"
    required: false
  - name: quality
    description: "Output quality 1-100 (default: 90)"
    required: false
  - name: scale
    description: "Scale factor (default: 2)"
    required: false
---

# Diagram Raster Render

Use `skills/_references/preflight-validations.md` and `skills/_references/output-formats.md`.

Use this skill to render a diagram source file directly to raster output. This bypasses SVG and produces PNG, JPEG, or WebP for destinations that cannot reliably render SVG. For converting between already-rendered image formats, use `/devkit:diagram-convert`.

## Preflight

Before raster rendering, run:

`zsh scripts/check-skill-deps.zsh diagram-raster format=<format>`

This must confirm:

- global `diagramkit` installed
- Playwright Chromium ready via `diagramkit warmup`
- global `sharp` for the requested raster format

If any check fails, stop and show the install commands before continuing.

## Workflow

1. **Validate input.** Confirm the input file exists and is a supported diagram source format.
2. **Render to raster.** Use `diagramkit` with the `--format` flag to render directly to the requested raster format with the specified quality and scale.
3. **Verify output.** Confirm the rendered file was created and is a valid image.
4. **Preserve source.** Keep the original diagram source file alongside the rendered output.

## Output

The rendered raster image alongside the original editable source file. Always keep both so the diagram remains editable for future changes.

Use this for:

- Confluence pages that need PNG/JPEG attachments
- Google Docs that require raster images
- PDF export where SVG rendering is unreliable
- Delivery pipelines with specific raster requirements

## Adjacent Skills

- `/devkit:diagram-convert` for converting between already-rendered image formats
- `/devkit:diagram-render` for rendering to any format (SVG preferred)
- `/devkit:diagram` for creating new diagrams from descriptions
