---
name: prj-doc-site-add-diagram
description: Author and render a diagram with diagramkit (Mermaid / Excalidraw / Draw.io / Graphviz) for a page in this repo's @pagesmith/docs site, then embed it as a theme-aware light/dark image pair. Use when adding a new diagram to a doc page or refreshing an existing one. Reads node_modules/diagramkit/skills/diagramkit-auto/SKILL.md plus the per-engine SKILL.md when present, falls back to the inline guidance below otherwise.
---

# Project: Add a Doc-Site Diagram

## Read the source skills (locally installed first, fallback to inline)

1. **Try first**: `node_modules/diagramkit/skills/diagramkit-auto/SKILL.md`
   - Plus the per-engine SKILL.md (`diagramkit-mermaid`, `diagramkit-graphviz`, `diagramkit-draw-io`, `diagramkit-excalidraw`) and its `references/` folder.
   - Plus `node_modules/diagramkit/skills/diagramkit-review/SKILL.md` for validation.
   - Plus `node_modules/diagramkit/REFERENCE.md` and `node_modules/diagramkit/llms.txt`.
2. **Also**: `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/references/markdown-guidelines.md` for the embedding rules.
3. **Fallback (inline below)**: only when one or both packages are not installed.

When the locally installed files exist, **they win over this inline body** on any conflict.

## When to use

- A doc page would be clearer with a flowchart, sequence, architecture, dependency graph, etc.
- An existing diagram drifted from the code and needs to be regenerated.
- A page needs both light and dark variants of a diagram for theme-aware rendering.

## When NOT to use

- The diagram doesn't add clarity — write prose / a list / a table instead. (Diagrams are for flow / architecture / lifecycle / dependency visualization.)
- Only the diagram **source code** is being shown to the reader (a syntax-highlighted ` ```mermaid ` fence is fine for that — no rendering needed).

## Workflow

### 1. Pick the engine

| Signal                                                                                                                                                                        | Engine     | Skill                   | Extension     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ----------------------- | ------------- |
| Process flow, pipeline, sequence, ER, class, state, timeline, gantt, C4, mindmap, pie, quadrant, sankey, XY, block, architecture, kanban, journey, packet, radar, requirement | Mermaid    | `diagramkit-mermaid`    | `.mermaid`    |
| Architecture overview, system context, codebase map, freeform layout, hand-drawn aesthetic                                                                                    | Excalidraw | `diagramkit-excalidraw` | `.excalidraw` |
| Network topology, cloud deployment (AWS / Azure / GCP icons), BPMN, swimlanes, multi-page                                                                                     | Draw.io    | `diagramkit-draw-io`    | `.drawio`     |
| Dependency graph, call graph, strict algorithmic layout                                                                                                                       | Graphviz   | `diagramkit-graphviz`   | `.dot`        |

Tie-breakers: default to Mermaid; prefer Mermaid over Graphviz when a structured type (sequence, ER, gantt, …) matches; prefer Drawio over Excalidraw when vendor icons or precision matter.

### 2. Place the source file beside the page

```
<contentDir>/<section>/<slug>/
  README.md
  diagrams/
    <semantic-name>.mermaid    # source
```

Use a semantic file name (`request-flow.mermaid`, not `diagram1.mermaid`).

### 3. Author the source

Universal rules:

- Use semantic IDs (`auth_service`, not `a`).
- **Hex colors only.** No named colors.
- **Do not hardcode `%%{init: {theme: ...}}%%`** — diagramkit owns theme injection.
- For Mermaid flowchart / class / state / ER, **always** start with `%%{init: {'htmlLabels': false}}%%` (flat top-level form) and use `\n` instead of `<br/>` for multi-line labels — `<img>` embeds drop `<foreignObject>`.
- Use the WCAG-AA palette (Mermaid):
  - Primary: `#2E5A88` / stroke `#1F4870` / text `#ffffff`
  - Secondary: `#1F6E68` / `#155752` / `#ffffff`
  - Alert: `#B43A3A` / `#8E2828` / `#ffffff`
  - Storage: `#8B5E15` / `#6E4810` / `#ffffff`
- Respect the readability budget: ≤ 50 nodes (dense) / ≤ 100 (sparse), ≤ 100 connections, ≤ 8 parallel branches, comprehension target ≤ 90 s.

### 4. Render

```bash
# Default: both light + dark SVG variants
npx diagramkit render <contentDir>/<section>/<slug>/diagrams/<name>.mermaid

# Force re-render (bypass manifest cache after edits)
npx diagramkit render <contentDir>/<section>/<slug>/diagrams/<name>.mermaid --force
```

Output goes to `<contentDir>/<section>/<slug>/diagrams/.diagramkit/` by default. Set `sameFolder: true` in `diagramkit.config.json5` if you prefer outputs sit directly beside the source.

### 5. Validate

```bash
npx diagramkit validate <contentDir>/<section>/<slug>/diagrams/.diagramkit/ --recursive --json
```

**Always-fix codes**: every `severity: "error"`, plus `LOW_CONTRAST_TEXT` (accessibility) and `ASPECT_RATIO_EXTREME` (readability). Apply fixes per the engine SKILL.md and re-render with `--force`. Cap at 8 iterations per file.

For `ASPECT_RATIO_EXTREME`, escalation ladder:
1. Engine-local rebalance (flip `LR ↔ TB`; rely on `mermaidLayout: { mode: 'auto' }` in config).
2. Reduce / restructure (collapse intermediate nodes, group with `subgraph`).
3. Split into multiple diagrams.
4. Swap engine.

### 6. Embed in the page

In `<contentDir>/<section>/<slug>/README.md`, use the consecutive `-light` / `-dark` markdown image pair (Pagesmith auto-merges into a themed `<figure><picture>`):

```md
![Request flow showing CLI command reaching the API layer and returning a rendered response](./diagrams/request-flow-light.svg "Request lifecycle")
![Request flow showing CLI command reaching the API layer and returning a rendered response](./diagrams/request-flow-dark.svg)
```

For manual control, raw HTML works too:

```html
<figure>
  <img src="./diagrams/request-flow-light.svg" class="only-light" alt="Request flow showing CLI command reaching the API layer" />
  <img src="./diagrams/request-flow-dark.svg" class="only-dark" alt="Request flow showing CLI command reaching the API layer" />
  <figcaption>Request lifecycle</figcaption>
</figure>
```

**Both variants must be present** as consecutive images. A lone `-light` or `-dark` throws an error.

### 7. Verify in dev

```bash
npx pagesmith-docs dev
```

Open the page, toggle the theme, confirm both variants render correctly.

### 8. Report

- Diagram source path, rendered output paths.
- Engine chosen + reasoning.
- Validation result (zero errors / `LOW_CONTRAST_TEXT` / `ASPECT_RATIO_EXTREME`).
- Embed location in the page.

## Inline fallback — minimal Mermaid example

```
%% Diagram: Request flow
%% Type: flowchart
%%{init: {'htmlLabels': false}}%%
flowchart LR
  cli["CLI command"] --> api["API layer"]
  api --> store[("Storage")]
  store --> api
  api --> cli

  classDef primary fill:#2E5A88,stroke:#1F4870,color:#fff
  classDef storage fill:#8B5E15,stroke:#6E4810,color:#fff
  class cli,api primary
  class store storage
```

Render → validate → embed using the consecutive image pair pattern above.

## Anti-patterns

- Hand-editing rendered SVGs in `.diagramkit/` instead of editing the source and re-rendering.
- Hardcoding `%%{init: {theme: ...}}%%` in Mermaid sources.
- Using named colors (`red`, `blue`) — behavior varies by renderer.
- Embedding only the light variant and trusting CSS `filter: invert()` to handle dark mode (it doesn't preserve color semantics).
- Missing `htmlLabels: false` on flowcharts intended for `<img>` embeds — labels silently disappear.
- Ignoring `ASPECT_RATIO_EXTREME` — diagrams scale down ~39% beyond the readable band and lose legibility.
- Missing alt text on the `<img>` (or markdown `![alt]`). Alt text is a description, not the title.
