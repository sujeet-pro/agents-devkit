---
name: diagram-convert
description: Use when you need to convert an existing rendered diagram image to a different raster format for destinations like Confluence, Google Docs, or PDF
user_invocable: true
arguments:
  - name: input
    description: "Path to the input image (SVG, PNG, JPEG, or WebP)"
    required: true
  - name: output
    description: "Optional output path"
    required: false
  - name: format
    description: "Target format: png, jpeg, webp (default: png)"
    required: false
  - name: quality
    description: "Output quality 1-100 (default: 90)"
    required: false
  - name: density
    description: "Rasterization density in DPI for SVG input (default: 150)"
    required: false
  - name: width
    description: "Optional output width in pixels"
    required: false
  - name: background
    description: "Optional background color (e.g., white, #ffffff)"
    required: false
---

# Diagram Image Convert

Use `skills/_references/preflight-validations.md` and `skills/_references/output-formats.md`.

Use this skill to convert an already-rendered diagram image (SVG, PNG, JPEG) to a different raster format suitable for a specific destination. This does NOT generate diagrams from source — use `/devkit:diagram-raster` to render source files (`.mmd`, `.excalidraw`, `.drawio`) to raster output.

## Preflight

Before converting, run:

`zsh scripts/check-skill-deps.zsh diagram-convert format=<format>`

This must confirm:

- global `diagramkit` installed
- Playwright Chromium ready via `diagramkit warmup`
- global `sharp` for raster conversion

If any check fails, stop and show the install commands before continuing.

## Workflow

1. **Validate input.** Confirm the input file exists and is a supported image format (SVG, PNG, JPEG, WebP).
2. **Determine output path.** Use the provided `output` path, or derive it from the input path with the new extension.
3. **Convert.** Use `sharp` or `diagramkit` to convert the image with the requested quality, density, width, and background options.
4. **Verify output.** Confirm the output file was created and is a valid image.
5. **Preserve source.** Keep the original input file alongside the converted output.

## Output

The converted image file at the output path. Always preserve the original source alongside the conversion.

Use this skill for:

- Confluence pages that need PNG attachments instead of SVG
- Google Docs that require raster images
- PDF export pipelines that need specific image formats
- Delivery formats that require a particular resolution or background color

## Adjacent Skills

- `/devkit:diagram-raster` for rendering diagram source files to raster (different from converting between image formats)
- `/devkit:diagram-render` for rendering diagram sources to any format
- `/devkit:diagram` for creating new diagrams
- `/devkit:publish-confluence` for publishing to Confluence with attachments
