---
name: diagram-mermaid
description: Use when Mermaid is the best fit for a text-first engineering diagram that should diff well in Git
user_invocable: true
arguments:
  - name: description
    description: "What to diagram"
    required: true
  - name: type
    description: "Optional Mermaid diagram type"
    required: false
  - name: theme
    description: "Theme: default, neutral, forest, dark, base"
    required: false
---

# Mermaid Diagram

Use `/devkit:diagram` with `engine=mermaid`. Inherit the `/devkit:diagram` preflight before generating source, then run structure, notation, and validation passes in parallel before finalizing the Mermaid source.

## Reference Loading

Load the appropriate diagram type reference from `skills/_references/mermaid/` based on the requested diagram type (e.g., `flowchart.md` for flowcharts, `sequence.md` for sequence diagrams, `er.md` for ERDs, `class.md` for class diagrams, `state.md` for state diagrams, `gantt.md` for Gantt charts, etc.).

For theming, load `skills/_references/mermaid/theming.md`.
