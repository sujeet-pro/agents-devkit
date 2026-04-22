---
name: adk-visualize
description: Category router for producing diagrams and charts from text descriptions or data - sequence/flow/architecture diagrams via mermaid/drawio/excalidraw/graphviz, and bar/line/pie/scatter charts from CSV/JSON/inline data. Use when the deliverable is a visual (image, SVG, or markdown-embedded diagram), not prose. Picks one of adk-visualize-diagram, adk-visualize-chart.
---

# ADK Visualize (Category Router)

Routes any "make a picture from this" intent to the right visualization task. Activate one of the listed task skills below; do not draft directly from this router.

## When to use this category

- A diagram is needed: sequence, flow, state, ER, architecture, dependency, class, deployment.
- A data chart is needed: bar, line, pie, scatter, histogram, stacked area, heatmap.
- An existing diagram or chart needs to be regenerated, restyled, or converted to a different format (PNG, SVG, embeddable mermaid).

## When NOT to use this category

- UI mockup or component design -> `adk-frontend-design`
- Architectural design write-up (text-heavy) -> `adk-plan-design` (which may then call this category for one diagram)
- Audit visualizations as part of a report -> let the audit task call this category for specific charts

## Shared workflow

Every task in this category honors the same five steps. The task skills tailor the content of each step.

1. **Confirm intent** - identify visual type, source data or domain, destination format (markdown-embedded mermaid is the default), and whether an editable source must be kept.
2. **Gather** - pull the source-of-truth: data file, schema, code paths to diagram, or interview questions if the picture is conceptual.
3. **Draft** - produce the editable source first (mermaid / drawio XML / excalidraw JSON / graphviz dot / chart spec). Render only after the source is approved.
4. **Validate** - render to the destination format and visually sanity check (no overlapping nodes, axes labeled, legend present, colors readable).
5. **Report** - show the rendered output and the editable source path; offer to tweak.

## Task selection

| Task skill | Use when | Do NOT use when |
| --- | --- | --- |
| `adk-visualize-diagram` | Sequence, flow, state, ER, architecture, dependency, class, deployment, or any structural picture | Numeric / categorical data plot - use chart |
| `adk-visualize-chart` | Bar, line, pie, scatter, histogram, stacked area, heatmap from numeric or categorical data | Structural / relationship picture - use diagram |

## Format defaults

| Destination | Diagram default | Chart default |
| --- | --- | --- |
| Markdown (README, PR, issue) | Embedded mermaid block | SVG file linked from markdown |
| Confluence / GitHub wiki | Embedded mermaid (both support) | PNG attached + linked |
| Slide deck | Exported SVG | Exported SVG |
| Print / handoff PDF | PNG (300 dpi) | PNG (300 dpi) |

Always keep the editable source alongside the rendered output (e.g. `architecture.mmd` next to `architecture.svg`).

## Activation

Once you have picked a task, load `adk-visualize-<task>` and follow it. Each task skill is fully standalone - everything it needs is in its own folder.

## Anti-patterns

- Drawing inside this router. Always hand off to a task skill.
- Rendering a binary without keeping the editable source.
- Charts without labeled axes or units.
- Diagrams with more than ~12 nodes per view; split into layered diagrams instead.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/visualize-clarifying-questions.md`) and reports the choices.

1. **Is the goal a structural diagram (boxes + arrows showing relationships) or a data chart (numeric values plotted)?** — _How to pick:_ Diagram → adk-visualize-diagram. Chart → adk-visualize-chart.

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** (n/a — small router)

**Artifact:** `visualize-routing-decision` — Inline message.

**Artifact path:** (none)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/visualize-clarifying-questions.md`) and reports the choices.

1. **Is the goal a structural diagram (boxes + arrows showing relationships) or a data chart (numeric values plotted)?** — _How to pick:_ Diagram → adk-visualize-diagram. Chart → adk-visualize-chart.

## Default vs detailed output

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** (n/a — small router)

**Artifact:** `visualize-routing-decision` — Inline message.

**Artifact path:** (none)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/visualize-anti-patterns.md` | Things to avoid when running this skill. |
| `references/visualize-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/visualize-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/visualize-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/visualize-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/visualize-persona.md` | The agent persona that drives this skill. |
| `references/visualize-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
