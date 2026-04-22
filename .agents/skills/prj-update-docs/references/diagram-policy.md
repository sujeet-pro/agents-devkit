# Diagram policy

When the skill produces or refreshes a diagram, the rules in this file are non-negotiable.
They aggregate the upstream guidance from:

- `node_modules/@pagesmith/docs/ai-guidelines/docs-guidelines.md` — Diagram Guidance
- `node_modules/diagramkit/skills/diagramkit-auto/SKILL.md` — engine selection + iterative loop
- `node_modules/diagramkit/skills/diagramkit-review/SKILL.md` — audit + repair workflow
- `node_modules/diagramkit/ai-guidelines/diagram-authoring.md` — per-engine authoring details

If anything in this file disagrees with the upstream files, the upstream files win — they
are version-pinned to the installed package. Update this file in that case.

## When to add a diagram

Only when prose, a list, or a table would be unclear. Triggers that justify a diagram:

- A flow with **branching** (decision tree, state machine, lifecycle).
- A **dependency graph** of more than ~5 nodes.
- An **architecture overview** showing component boundaries.
- A **sequence** of message exchanges between systems.

Do **not** add a diagram for:

- A linear list of steps with no branching (use a numbered list).
- A small table of options (use a Markdown table).
- Decoration on a page that already explains the concept clearly.

## Engine selection

Default to **Mermaid**. Apply the tie-break rules from `diagramkit-auto`:

| Need                                                                                     | Engine     |
| ---------------------------------------------------------------------------------------- | ---------- |
| Process flow, sequence, ER, class, state, gantt, timeline, C4                            | Mermaid    |
| Architecture overview / hand-drawn aesthetic / freeform layout                           | Excalidraw |
| Cloud vendor icons (AWS / Azure / GCP), BPMN, swimlanes, multi-page, precise positioning | Draw.io    |
| Pure dependency / call graph with strict algorithmic layout                              | Graphviz   |

When two engines could work, follow the tie-break order in `diagramkit-auto`:

1. Default to Mermaid.
2. Excalidraw over Draw.io for explanation overviews.
3. Draw.io over Excalidraw when vendor icons / precision / multi-page matters.
4. Graphviz over Mermaid for pure DAGs with no Mermaid-specific type.
5. Mermaid over Graphviz when a structured Mermaid type matches.

## File layout

```
docs/<section>/<slug>/
  README.md
  diagrams/
    <slug>-overview.mermaid     # editable source (committed)
    .diagramkit/                # rendered output (committed)
      <slug>-overview-light.svg
      <slug>-overview-dark.svg
```

The diagram source lives **inside** `docs/` so the pagesmith content-relative asset
transform publishes the rendered SVGs under the page's path automatically.

`diagramkit.config.json5` controls whether output lands in a `.diagramkit/` subfolder or
beside the source (`sameFolder: true`). This skill leaves the project's existing setting
unchanged.

## Mermaid embed-safety

Every Mermaid source meant to be embedded as `<img>` (or `<picture>`) **must** start with:

```mermaid
%%{init: {'htmlLabels': false}}%%
```

Without this, the rendered SVG uses `<foreignObject>` for labels, which silently degrades
in `<img>`-based Markdown embeds. Confirmed by `diagramkit validate`'s
`CONTAINS_FOREIGN_OBJECT` warning.

For multi-line labels, prefer `\n` over `<br/>`.

## Embed pattern

Use the theme-aware `<picture>` block, lifted from `diagramkit-setup`:

```html
<figure>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./diagrams/.diagramkit/<slug>-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="./diagrams/.diagramkit/<slug>-light.svg" />
    <img alt="<descriptive alt that explains the point of the diagram>" src="./diagrams/.diagramkit/<slug>-light.svg" />
  </picture>
  <figcaption><i>Optional caption.</i></figcaption>
</figure>
```

Pagesmith's `rehype-local-images` plus the docs asset transform rewrite the `srcset` /
`src` paths to `/assets/<content-relative-path>` at build time. Keep the assets inside
the page directory so they stay scoped.

For light/dark variants where the renderer uses one file per theme, the `.only-light` /
`.only-dark` classes from the docs-guidelines also work:

```html
<figure>
  <img src="./diagrams/.diagramkit/<slug>-light.svg" class="only-light" alt="..." />
  <img src="./diagrams/.diagramkit/<slug>-dark.svg"  class="only-dark"  alt="..." />
</figure>
```

## Render + validate loop (per file)

```bash
# Always anchor on the local install.
DK="npx diagramkit"

$DK render <page-dir>/diagrams --force --json
$DK validate <page-dir>/diagrams --recursive --json
```

Always-fix codes:

| Code                     | Severity | Fix tactic                                                              |
| ------------------------ | -------- | ----------------------------------------------------------------------- |
| any `severity: "error"`  | error    | Source-level fix per the engine SKILL's Review Mode.                    |
| `LOW_CONTRAST_TEXT`      | warning  | Palette swap to a mid-tone hex (`#3A6FB4`-style), per `diagram-authoring.md`. |
| `ASPECT_RATIO_EXTREME`   | warning  | Engine-local rebalance → reduce/restructure → split → swap engine.      |
| `CONTAINS_FOREIGN_OBJECT` | warning | Add `%%{init: {'htmlLabels': false}}%%` (Mermaid) or strip from drawio. |
| `EXTERNAL_RESOURCE`      | warning  | Inline the resource or remove it.                                       |

Cap the loop at **8 iterations per source**. Anything still failing after 8 is a residual
finding (recorded in the report), not a silent skip.

## When to use upstream `diagramkit-review` wholesale

For phase 6 of `prj-update-docs` (the global audit), do **not** roll your own loop —
delegate fully to:

```
node_modules/diagramkit/skills/diagramkit-review/SKILL.md
```

It already encapsulates phase 1 (per-engine source audit) → phase 5 (summary report)
exactly as needed.

## Anti-patterns

- Adding a diagram because the page "feels short". Diagrams must earn their slot.
- Hand-editing rendered SVGs. They are derived; re-render instead.
- Hardcoding theme colours in source. Let `diagramkit` control theme selection.
- Using named CSS colours (`red`, `blue`). Hex only.
- Skipping the `--force` flag when re-rendering after a fix — the manifest cache will
  short-circuit the new source.
- Falling back to a globally installed `diagramkit`. Always `npx diagramkit ...` against
  `node_modules/`.
