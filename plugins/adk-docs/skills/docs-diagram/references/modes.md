# `docs-diagram` — modes

Supports `--auto` (default) and `-i`. Does NOT support `--fix`:
there's no canonical write-back for a diagram — it lands in
`.temp/task-<slug>/` and the user embeds it into a doc (via
`docs-write`) or publishes it (via `docs-publish-*`) separately.

## `--auto` (default)

- All phases run without approval gates.
- Produces `<subject>.mermaid` + SVG pair (if diagramkit available).
- On > 15 nodes, auto-selects "overview + zoom-in" split.

## `-i` / `--interactive`

- Per-phase approval gates.
- Useful when:
  - The split strategy matters (different splits serve different
    readers).
  - The scope is wide and the node-count is on the boundary of the
    budget.
  - The diagram type detection is ambiguous (flowchart vs sequence
    for a request flow).

## Why no `--fix`

- The `.mermaid` file and SVG pair are drafts; they go into a doc
  or get published downstream.
- There's no "canonical path" for a diagram alone — it lives inside
  a doc or a Confluence page.
- If the user wants the diagram embedded into a doc,
  `/adk-docs:docs-write` (with a reference to the diagram artifact)
  does that.

## Guardrails (all modes)

1. Never writes outside `.temp/task-<slug>/`.
2. Never invokes `docs-publish-*` from this skill.
3. Never runs more than one diagramkit render per `.mermaid` file
   per phase.
4. Hard-caps generated diagrams at 3 per run (one overview + two
   zoom-ins at most); beyond that, surface to the user.

## Flag combinations

| Combination | Effect |
| --- | --- |
| (no flags) | draft `.mermaid` + attempt render |
| `-i` | per-phase approval; draft + attempt render |
| `--scope <path>` | ground nodes / edges in the scope; composable with any mode |
