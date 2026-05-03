# Node budget

The hard cap: **no single `.mermaid` file has more than 15 nodes.**
If the concept needs more, the skill splits.

## Why 15

- Human working memory for a visual structure tops out around
  7±2 chunks; 15 is a generous upper bound that still renders in
  a single screen at typical Markdown viewer widths.
- Past 15 nodes, the rendered SVG's text becomes hard to read
  without pan/zoom; the diagram stops being a *diagram* and starts
  being a *system map*.
- System maps have their place — but they're a different
  deliverable. `docs-diagram` produces diagrams.

## What counts as a node

- **flowchart:** every box (`A["..."]`) and every decision diamond
  (`B{"..."}`). Arrows don't count.
- **sequenceDiagram:** every `participant` and `actor`. Messages
  don't count toward the budget directly, but a sequence with > 20
  messages between 3 actors is still too busy — cap at ~15 messages
  as well.
- **classDiagram:** every `class`. Inheritance arrows don't count.
- **stateDiagram-v2:** every state (including `[*]` start/end).
  Transitions don't count.
- **erDiagram:** every entity. Relationship arrows don't count.
- **gantt:** every task. Sections don't count.
- **gitgraph:** every commit. Branches count as nodes too.
- **mindmap:** every node at every level.
- **timeline:** every event. Sections don't count.
- **C4:** every `Person`, `System`, `System_Boundary` header,
  `Container`, `ContainerDb`, `System_Ext`. Rels don't count.

## Secondary limits

- **Arrows / messages / relations per node:** ≤ 5. Beyond that, the
  node is a god-object; factor out an intermediate or split.
- **Hierarchy depth:** ≤ 3 nested subgraphs / system boundaries.
- **Overall text length in labels:** ≤ 5 words per label.

## Split strategies

### A — Overview + zoom-in (default)

```
<subject>.overview.mermaid           (5-7 nodes; top-level)
<subject>.<subsystem-a>.mermaid      (up to 15 nodes; zoom)
<subject>.<subsystem-b>.mermaid      (up to 15 nodes; zoom)
```

The overview shows subsystems as big boxes with one arrow per major
relation; each zoom shows the inside of one subsystem.

### B — Lifecycle phase split

For state diagrams: split by phase.

```
<subject>.creation.mermaid           (states in creation phase)
<subject>.active.mermaid             (states in active phase)
<subject>.cleanup.mermaid            (states in cleanup phase)
```

Link them in the report: "after `Ready`, lifecycle continues in
`active.mermaid`".

### C — Actor-view split

For busy sequences: one diagram per actor's perspective.

```
<subject>.user-view.mermaid          (messages user participates in)
<subject>.system-view.mermaid        (messages between backend systems)
```

Reader picks the view that matches their question.

### D — Side-by-side pairs

For comparisons (before/after, system-A/system-B): two
`.mermaid` files named `<subject>.a.mermaid` and
`<subject>.b.mermaid`. The report presents them side-by-side.

## When even the split doesn't fit

If the skill can't split into ≤ 15-node pieces (e.g. a hundred
tables in a schema), it stops with:

```
The <scope> has <N> nodes, which exceeds the 15-node budget even
after splitting by <strategy>. Pick a narrower scope:
  - Limit --scope to <suggested sub-path>.
  - Or group the <N> nodes into functional clusters first, then
    diagram each cluster separately.
```

## Split cap per run

Max 3 diagrams per run (one overview + up to two zoom-ins). If the
user wants more, re-invoke the skill with a narrower `--scope`.

## Why these limits

- A PR that brings 5 new diagrams is unreviewable.
- Maintaining 10 diagrams that overlap is worse than maintaining
  3 diagrams that don't.
- Readers click "next" at most twice before giving up; 3 paired
  diagrams is the attention cap.
