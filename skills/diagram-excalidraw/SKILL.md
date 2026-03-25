---
name: diagram-excalidraw
description: Use when Excalidraw is the best fit for a software architecture, ownership, or freeform engineering diagram
user_invocable: true
arguments:
  - name: description
    description: "What to diagram"
    required: true
  - name: palette
    description: "Palette: default, aws, azure, gcp, kubernetes"
    required: false
  - name: style
    description: "Style: hand-drawn, clean (default: hand-drawn)"
    required: false
---

# Excalidraw Diagram

Use `/devkit:diagram` with `engine=excalidraw`. Inherit the `/devkit:diagram` preflight before generating source, then run structure, notation, and validation passes in parallel before finalizing the `.excalidraw` source.

## Reference Loading

Load references from `skills/_references/excalidraw/`: `json-format.md` for element structure, `arrows.md` for connection types, `colors.md` for palette conventions, `examples.md` for common patterns, `validation.md` for pre-render checks.
