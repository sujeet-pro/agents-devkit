# Diagramkit Mermaid Quick Reference (fallback)

> Inline fallback for Mermaid authoring + rendering with diagramkit. When the package is installed, prefer:
> - `node_modules/diagramkit/skills/diagramkit-mermaid/SKILL.md`
> - `node_modules/diagramkit/skills/diagramkit-mermaid/references/diagram-types.md`
> - `node_modules/diagramkit/skills/diagramkit-mermaid/references/color-and-theming.md`
> - `node_modules/diagramkit/REFERENCE.md`

This is a **quick reference**. The full diagram-types syntax catalog (1869 lines) is intentionally not duplicated here — read the package version when authoring complex diagrams.

## Diagram type routing

Pick the smallest diagram type that fits the job.

| Type           | Directive            | Best for                                  |
| -------------- | -------------------- | ----------------------------------------- |
| `flowchart`    | `flowchart TD`       | Process flows, pipelines, decision trees  |
| `sequence`     | `sequenceDiagram`    | Message passing, API exchanges, protocols |
| `class`        | `classDiagram`       | OOP structure, inheritance, interfaces    |
| `state`        | `stateDiagram-v2`    | State machines and lifecycle transitions  |
| `er`           | `erDiagram`          | Database entities and relationships       |
| `gantt`        | `gantt`              | Timelines, schedules, rollout plans       |
| `gitgraph`     | `gitGraph`           | Branching and release histories           |
| `mindmap`      | `mindmap`            | Concept maps and brainstorming            |
| `timeline`     | `timeline`           | Milestones, roadmaps, history             |
| `c4`           | `C4Context`          | C4 architecture views                     |
| `pie`          | `pie`                | Simple categorical distribution           |
| `quadrant`     | `quadrantChart`      | Priority or evaluation matrices           |
| `sankey`       | `sankey-beta`        | Flow volumes between stages               |
| `xy`           | `xychart-beta`       | Small chart-like comparisons              |
| `block`        | `block-beta`         | Structured block layouts                  |
| `architecture` | `architecture-beta`  | Icon-driven architecture diagrams         |
| `kanban`       | `kanban`             | Board-style work status views             |
| `journey`      | `journey`            | User journey or service experience maps   |
| `packet`       | `packet-beta`        | Bit- or field-level packet layouts        |
| `radar`        | `radar-beta`         | Multi-axis comparison                     |
| `requirement`  | `requirementDiagram` | Requirements tracing                      |

## Authoring rules

1. Start with a comment header:
   ```
   %% Diagram: <title>
   %% Type: <diagram-type>
   ```
2. Pick the smallest diagram type from the routing table.
3. Use semantic IDs (`auth_service`, not `a`).
4. Use **hex colors only** — never named colors.
5. Use the WCAG-AA palette below for fills.
6. Do **NOT** hardcode `%%{init: {theme: ...}}%%` — diagramkit controls theme injection.
7. **Always add `%%{init: {'htmlLabels': false}}%%`** on every flowchart / class / state / ER diagram. The directive must come **before** the diagram keyword. Use the **flat** form (the nested `{'flowchart': {'htmlLabels': false}}` form is silently ignored on Mermaid 11). A safe combined fallback is `%%{init: {'htmlLabels': false, 'flowchart': {'htmlLabels': false}}}%%`.
8. **Prefer `\n` over `<br/>` for multi-line labels** when `htmlLabels` is off. Always **quote the label**:
   - Good: `PHYSICAL["Physical Clocks\nNTP, PTP, TrueTime"]`
   - Avoid: `PHYSICAL[Physical Clocks<br/>NTP...]`
   - Inline HTML (`<b>`, `<i>`, `<code>`) renders as literal text — strip or replace.

## Color palette (WCAG 2.2 AA-compliant)

Use these darker mid-tone fills with white text. Every (fill, `#ffffff`) pair meets WCAG 2.2 AA contrast.

| Purpose             | Fill      | Stroke    | Text      | White-text contrast |
| ------------------- | --------- | --------- | --------- | ------------------- |
| Primary / API       | `#2E5A88` | `#1F4870` | `#ffffff` | 7.1:1               |
| Secondary / Service | `#1F6E68` | `#155752` | `#ffffff` | 5.9:1               |
| Accent / Alert      | `#B43A3A` | `#8E2828` | `#ffffff` | 5.5:1               |
| Storage / Data      | `#8B5E15` | `#6E4810` | `#ffffff` | 5.4:1               |
| Success             | `#2D7A2D` | `#1E5A1E` | `#ffffff` | 5.4:1               |
| Neutral             | `#5A5A5A` | `#3D3D3D` | `#ffffff` | 7.0:1               |

**Avoid:** `#ffffff` / near-white fills, `#000000` / near-black fills, named colors, neon colors, white text on light pastels (fails AA).

**Reserved Mermaid class names** — do NOT name a `classDef` `root`, `default`, `node`, `cluster`, or any other class Mermaid uses internally. Mermaid emits `<g class="root">` / `<g class="default">` wrappers, so a same-named `classDef` will leak rules to every label.

## Example

```
%% Diagram: CI/CD Pipeline
%% Type: flowchart
%%{init: {'htmlLabels': false}}%%
flowchart LR
  subgraph build["Build Stage"]
    checkout["Checkout Code"] --> lint["Run Linter"]
    lint --> test["Run Tests"]
    test --> compile["Compile"]
  end

  subgraph deploy["Deploy Stage"]
    staging["Deploy Staging"] --> smoke["Smoke Tests"]
    smoke --> prod["Deploy Production"]
  end

  compile --> staging
  prod --> monitor["Monitor Health"]

  classDef stage fill:#2E5A88,stroke:#1F4870,color:#fff
  class checkout,lint,test,compile stage
```

## Render

```bash
# Default: both light + dark SVG variants, output to .diagramkit/ next to source
npx diagramkit render path/to/file.mermaid

# Light only
npx diagramkit render path/to/file.mermaid --theme light

# Force re-render (bypass manifest cache)
npx diagramkit render path/to/file.mermaid --force

# All mermaid files in cwd recursively
npx diagramkit render . --type mermaid
```

Output:

```
docs/
  architecture.mermaid
  .diagramkit/
    architecture-light.svg
    architecture-dark.svg
```

## Validate

```bash
npx diagramkit validate path/to/.diagramkit/
npx diagramkit validate path/to/.diagramkit/ --recursive --json
```

### Common validation codes

| Code                       | Severity | Fix                                                                                                                       |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------- |
| `CONTAINS_FOREIGN_OBJECT`  | warning  | Add **flat** `%%{init: {'htmlLabels': false}}%%`; convert `<br/>` → `\n`; quote labels.                                   |
| `NO_VISUAL_ELEMENTS`       | error    | Mermaid syntax error. Quote labels with `()`, `:`, `<`, `>`. Verify the diagram keyword is on its own line.               |
| `MISSING_SVG_CLOSE`        | error    | Render crashed mid-output. Fix syntax and re-render with `--force`.                                                       |
| `EMPTY_FILE`               | error    | Re-render; check Chromium installed (`npx diagramkit warmup`).                                                            |
| `CONTAINS_SCRIPT`          | error    | Re-render with diagramkit (it strips scripts); avoid custom Mermaid plugins.                                              |
| `EXTERNAL_RESOURCE`        | warning  | Blocked in `<img>` embeds. Re-render to inline; strip `<a xlink:href="…">` from hand-exported drawio SVGs.                |
| `LOW_CONTRAST_TEXT`        | warning  | Switch fill / text combo to the WCAG-AA palette above.                                                                    |
| `ASPECT_RATIO_EXTREME`     | warning  | Add `mermaidLayout: { mode: 'auto' }` to config; flip directive (`LR ↔ TB`); reduce nodes; split; swap engine.            |

## Iterative loop

```text
1. npx diagramkit render <file> --force --json
2. npx diagramkit validate <file's .diagramkit dir> --json
3. If errors OR LOW_CONTRAST_TEXT OR ASPECT_RATIO_EXTREME:
   apply matching fix; goto 1 (cap 8 iterations per file)
4. Else: done.
```

## Aspect-ratio escalation ladder

When `ASPECT_RATIO_EXTREME` persists:

1. **Engine-local rebalance** — flip `LR ↔ TB`; rely on `mermaidLayout: { mode: 'auto' }`.
2. **Reduce / restructure** — collapse intermediate nodes; group with `subgraph`; tighten labels.
3. **Split into multiple diagrams** — one story per diagram (≤ 90 s comprehension).
4. **Swap engine** — Graphviz with `ratio=` for pure DAGs; Drawio for icon-heavy / precision; Mermaid (with auto layout) for text-first authoring.

## For Pagesmith embedding

After rendering both light + dark variants, embed in markdown using the consecutive image pair pattern (Pagesmith auto-merges into a themed `<picture>`):

```md
![CI/CD pipeline showing build, deploy, and monitor stages](./diagrams/architecture-light.svg "CI/CD Pipeline")
![CI/CD pipeline showing build, deploy, and monitor stages](./diagrams/architecture-dark.svg)
```

Or use raw HTML for explicit control:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./diagrams/architecture-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="./diagrams/architecture-light.svg" />
  <img alt="CI/CD pipeline showing build, deploy, and monitor stages" src="./diagrams/architecture-light.svg" />
</picture>
```
