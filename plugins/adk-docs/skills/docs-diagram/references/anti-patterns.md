# `docs-diagram` — anti-patterns

## Content

- **30-node flowchart.** That's a system map, not a diagram. Split
  into overview + zoom-ins.
- **ASCII art output** when the user asked for Mermaid. Wrong
  format; no rendering path; poor rendering in Markdown viewers that
  support Mermaid natively.
- **Mixing concepts.** "Auth flow AND schema" in one diagram.
  Pick one.
- **Fabricated edges.** Under `--scope`, every edge must trace to a
  call / import / reference. "I think these two services talk" is
  speculation.
- **Unlabeled edges that need labels.** If the direction alone isn't
  clear, label the edge ("calls", "subscribes", "owns").
- **Labels that are the same as the node name.** Redundant noise.

## Type choice

- **Flowchart for a sequence.** Use `sequenceDiagram` — the
  horizontal actor lanes are load-bearing.
- **Sequence for a state machine.** Use `stateDiagram-v2` — states
  + transitions model the lifecycle cleanly.
- **Class for ER.** Use `erDiagram` — the relationships and
  multiplicity are first-class.
- **Flowchart for infrastructure.** Consider C4 (`C4Container`) —
  the container concept is more faithful to the subject.

## Node / edge style

- **Long labels (> 5 words).** Compress to a noun phrase.
- **Too many edges** (fan-out from one node > 5) — the node is
  probably a god object; split it or add a grouping layer.
- **No direction in a flow** (`A --- B` instead of `A --> B`) —
  flows usually have direction; use `--` only for undirected
  relationships.

## Process

- **Skipping validation.** Always try to render (diagramkit, or
  at least the parser). Broken Mermaid = broken diagram.
- **Writing outside `.temp/task-<slug>/`.** Diagrams live there
  until embedded / published.
- **Auto-publishing.** This skill does NOT publish; that's
  `docs-publish-*`.
- **Running diagramkit without bounding time.** If the render
  hangs, fail fast (30s timeout).

## Scope

- **Numeric charts.** Out of scope. Use a notebook or BI tool.
- **Maps / geographic data.** Out of scope.
- **Animated diagrams.** Out of scope for adk v0.1.
- **Mixed-language labels.** Pick one language for labels within a
  single diagram; follow the repo's convention.
