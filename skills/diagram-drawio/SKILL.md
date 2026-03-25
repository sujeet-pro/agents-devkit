---
name: diagram-drawio
description: Use when draw.io is the best fit for a precise engineering, infrastructure, or process diagram
user_invocable: true
arguments:
  - name: description
    description: "What to diagram"
    required: true
  - name: style
    description: "Style: default, sketch, minimal (default: default)"
    required: false
---

# draw.io Diagram

Use `/devkit:diagram` with `engine=drawio`. Inherit the `/devkit:diagram` preflight before generating source, then run structure, notation, and validation passes in parallel before finalizing the `.drawio` source.

## Reference Loading

Load references from `skills/_references/drawio/`: `shapes.md` for available shapes and stencils, `styles.md` for styling conventions.
