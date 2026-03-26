---
name: diagram-render
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

`zsh scripts/check-skill-deps.zsh diagram-render format=<format>`

If the check fails, stop and show the install commands instead of attempting a partial render:

- `npm install -g diagramkit`
- `diagramkit warmup`
- `npm install -g sharp` for raster output

Treat rendering as a validation step, not just a conversion step.

## Required Child Agents

Run at least these child agents in parallel:

- **Source integrity agent**: validates the diagram source file is well-formed and parseable. Checks for syntax errors, missing references, and unsupported features. Reports issues before attempting render.
- **Render agent**: executes the `diagramkit` render command with the requested format and theme. Handles both single-file and directory-level rendering. Reports render success or failure with error details.
- **Output-fit agent**: checks whether the rendered format matches the intended destination. Flags cases where SVG would be better than raster or vice versa. Verifies file sizes and image quality are acceptable.

## Workflow

1. **Validate source.** Launch the source integrity agent to check the input file or directory.
2. **Render.** Launch the render agent with the specified format and theme.
3. **Check output fit.** Launch the output-fit agent to verify the rendered output suits the destination.
4. **Report.** Present the rendering results with any warnings or quality issues.

Prefer SVG. Use PNG or JPEG only when the destination cannot reliably handle SVG.

## Output

Rendered diagram artifacts alongside the original editable source files. For directory-level rendering, produce a manifest of all rendered files with their status.

## Adjacent Skills

- `/devkit:diagram` for creating new diagrams with automatic engine selection
- `/devkit:diagram-raster` for rendering directly to raster output
- `/devkit:diagram-convert` for converting between image formats
- `/devkit:diagram-troubleshoot` for diagnosing render failures
