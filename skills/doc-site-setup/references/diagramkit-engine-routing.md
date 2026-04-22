# Diagramkit Engine Routing Reference (fallback)

> Inline fallback for picking the right diagramkit engine for a new diagram. When the package is installed, prefer:
> - `node_modules/diagramkit/skills/diagramkit-auto/SKILL.md`
> - `node_modules/diagramkit/skills/diagramkit-mermaid/SKILL.md`
> - `node_modules/diagramkit/skills/diagramkit-graphviz/SKILL.md`
> - `node_modules/diagramkit/skills/diagramkit-draw-io/SKILL.md`
> - `node_modules/diagramkit/skills/diagramkit-excalidraw/SKILL.md`
> - `node_modules/diagramkit/skills/diagramkit-review/SKILL.md`

## Engine selection table

| Signal                                                                                                                                                                        | Engine     | Skill                   | Extension     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ----------------------- | ------------- |
| Process flow, pipeline, sequence, ER, class, state, timeline, gantt, C4, mindmap, pie, quadrant, sankey, XY, block, architecture, kanban, journey, packet, radar, requirement | Mermaid    | `diagramkit-mermaid`    | `.mermaid`    |
| Architecture overview, system context, codebase map, freeform layout, hand-drawn aesthetic, concept map, whiteboard visual                                                    | Excalidraw | `diagramkit-excalidraw` | `.excalidraw` |
| Network topology, cloud deployment (AWS / Azure / GCP icons), BPMN, org chart, enterprise system map, multi-page, swimlanes, precise positioning                              | Draw.io    | `diagramkit-draw-io`    | `.drawio`     |
| Dependency graph, call graph, strict algorithmic layout, rank-constrained DAGs, existing `.dot` / `.gv` source                                                                | Graphviz   | `diagramkit-graphviz`   | `.dot`        |

## Tie-breaking rules

When multiple engines could work, apply in order:

1. **Default to Mermaid** — text-first, diffs cleanly in Git, fastest to revise, widest type support (21+).
2. **Prefer Excalidraw over Draw.io** when the diagram is an explanation or overview that benefits from a hand-drawn feel, not precise positioning.
3. **Prefer Draw.io over Excalidraw** when the diagram needs cloud vendor icons (AWS / Azure / GCP), precise manual positioning, containers / swimlanes, or multi-page support.
4. **Prefer Graphviz over Mermaid** when the graph structure is primary and no Mermaid-specific type (sequence, ER, gantt, etc.) applies — pure node / edge dependency or call graphs.
5. **Prefer Mermaid over Graphviz** when a specific Mermaid type matches (sequence, ER, gantt, gitgraph, C4, pie, etc.) rather than a generic directed graph.

### Engine-swap signal during iteration

If post-render validation surfaces `ASPECT_RATIO_EXTREME` and engine-local fixes (flip / reflow / `ratio=`) plus splitting into multiple diagrams **still** can't bring the SVG inside `[1:1.9, 3.3:1]`, swap the engine:

| Currently using   | Aspect ratio still wrong because…                                             | Swap to                                                                                          |
| :---------------- | :---------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------- |
| Mermaid (Dagre)   | Layout engine has no aspect-ratio knob and the diagram is irreducibly complex | Graphviz (`ratio="0.75"` is direct) — pure DAGs; or Drawio for icon-heavy / precision layouts    |
| Drawio            | The shape catalog isn't the value — the diagram is mostly nodes + edges       | Graphviz for algorithmic layout with `ratio=`; or Mermaid (with `mermaidLayout: { mode: 'auto' }`) |
| Graphviz          | The structure is naturally a structured Mermaid type (sequence, ER, gantt)    | Mermaid for the matching diagram type                                                            |
| Excalidraw        | The hand-drawn aesthetic isn't the value                                      | Mermaid (structured types) or Graphviz (pure graphs)                                             |

Engine swaps are textual rewrites, so they cost agent time. Try splitting first; only swap when the diagram fights its current engine.

## Universal authoring rules

These apply regardless of engine.

1. **Source alongside output** — commit the editable source file next to rendered assets.
2. **Smallest diagram** — prefer the minimal diagram that explains the point.
3. **Semantic IDs** — use descriptive IDs (`auth_service`), not single letters (`a`).
4. **One story per diagram** — comprehension target ≤ 90 s.
5. **No hardcoded themes** — let diagramkit control theme selection (no `%%{init: {theme: ...}}%%` in source).
6. **Hex colors only** — no named colors (`red`, `blue`).
7. **Mid-tone palette** — avoid near-white or near-black fills.
8. **Re-render after edits** — never hand-edit generated SVGs.
9. **Image-embed safety** — when the SVG will be referenced via Markdown `![](foo.svg)`, `<picture>`, or any `<img>`:
   - Start Mermaid sources with `%%{init: {'htmlLabels': false}}%%`.
   - Prefer `\n` over `<br/>` for multi-line labels.
   - Strip `<a xlink:href="…">` wrappers from hand-exported drawio SVGs.

## Readability budget

- ≤ 50 nodes (dense) / ≤ 100 (sparse). Target ≤ 15 in routine diagrams.
- ≤ 100 connections per diagram.
- ≤ 8 parallel branches out of any single node.
- Aspect ratio inside `[1:1.9, 3.3:1]` against a 4:3 target.

## Visual encoding

- **Consistent shape semantics** (mixing meaning slows interpretation ~4×):
  - rectangle = process / service
  - rounded rectangle = external boundary or actor
  - diamond = decision (only — never decoration)
  - cylinder = persistent storage
  - hexagon = external system / queue / event
  - parallelogram = input / output / payload
  - circle = start / end terminator
- **Never rely on colour alone for meaning.** Pair every colour with a shape, label, or position. ~8% of male engineers have red-green colour-vision deficiency.
- **Reserve red (`#B43A3A`) for errors / alerts.** Don't use it for "primary" or generic emphasis.

## Iterative render → validate loop

```text
1. Render --force --json
2. Validate --json
3. If errors OR LOW_CONTRAST_TEXT OR ASPECT_RATIO_EXTREME:
   apply fix per the engine SKILL.md; goto 1 (cap 8 iterations)
4. Else: done.
```

For `ASPECT_RATIO_EXTREME` specifically, the fix ladder is:
**engine-local rebalance → reduce / restructure → split into multiple diagrams → swap engine (last resort)**.

Always-fix codes: every `severity: "error"`, plus `LOW_CONTRAST_TEXT` (accessibility) and `ASPECT_RATIO_EXTREME` (readability). Treat the other warnings (`CONTAINS_FOREIGN_OBJECT`, `EXTERNAL_RESOURCE`) as fix-unless-we-truly-only-render-for-SVG-viewers, since both silently degrade in `<img>`-based Markdown embeds.

## Force re-render

To regenerate all diagrams regardless of cache:

```bash
npx diagramkit render . --force
```

The manifest caches on source hash so unchanged files are skipped without `--force`.

## Resolve diagramkit (always prefer the local install)

```bash
if [ ! -x ./node_modules/.bin/diagramkit ]; then
  npm add diagramkit
fi

DK="npx diagramkit"
$DK warmup     # skip if Graphviz-only
```

> Read `node_modules/diagramkit/REFERENCE.md` (and `node_modules/diagramkit/llms.txt`) before running render commands. They are version-pinned to the installed package.
