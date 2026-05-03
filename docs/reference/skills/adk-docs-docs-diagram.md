---
title: 'adk-docs:docs-diagram'
description: '  Author a Mermaid diagram (.mermaid / .mmd) from a description OR from real code / config evidence. Supports flowchart, sequence, class, state, ER, gantt, gitgraph, mindmap, timeline, and C4. Keeps every diagram under 15 nodes (per references/node-budget.md) — splits larger concepts into paired diagrams. Renders to SVG (light + dark pair) via the diagramkit npx tool when available; otherwise leaves rendering to downstream tooling. Use when the deliverable is a diagram (a .mermaid file, or a mermaid code fence inside a doc). Do NOT use for numeric charts / plots of real data (out of scope for adk; use a notebook or BI tool), or for ASCII art when Mermaid was requested.'
plugin: 'adk-docs'
skill: 'docs-diagram'
source: 'plugins/adk-docs/skills/docs-diagram/SKILL.md'
group: 'docs-skills'
order: 3103
---
# adk-docs:docs-diagram

## Source

`plugins/adk-docs/skills/docs-diagram/SKILL.md`

## Skill Body

# docs-diagram — author a Mermaid diagram

One diagram per concept. Under 15 nodes per diagram. No ASCII art when
Mermaid is asked.

## When to use

- "diagram of the auth flow" (sequence)
- "ER for the orders schema" (ER)
- "state machine for export jobs" (state)
- "C4 container diagram for checkout service"
- "timeline of the incident"

## When NOT to use

| Not this → | Use this |
| --- | --- |
| numeric chart of real data | out of scope for adk (use a notebook / BI tool) |
| ASCII art | out of scope (when Mermaid is asked, produce Mermaid) |
| author a full doc | `/adk-docs:docs-write` (which may embed a diagram) |
| review an existing diagram | `/adk-docs:docs-review` |

## Common prompts

- "diagram of the auth flow"
- "sequence for checkout"
- "state machine for export jobs"
- "ER for the orders schema"
- "C4 container diagram for checkout"
- "gitgraph of the release branching model"
- "timeline of the 2026-05-02 incident"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<diagram-type>` | yes | one of: flowchart, sequence, class, state, ER, gantt, gitgraph, mindmap, timeline, C4 |
| `<subject>` | yes | free-form description |
| `--scope <path>` | no | repo path to read evidence from |
| `-i` / `--interactive` | no | off |

## Workflow

```
Phase 0 — prompt expansion
  - Classify diagram type (or accept explicit arg).
  - Resolve repo + scope; pick slug (e.g. diagram-<type>-<subject>).
  - Create .temp/task-<slug>/.

Phase 1 — preflight
  - adk-info --check.
  - If --scope path given, verify it exists.
  - Check diagramkit availability (npx @adk/diagramkit --version).

Phase 2 — gather evidence (if scope given)
  - Read the scope: source files, schema files, workflow YAML, etc.
  - Build a node/edge list in .temp/task-<slug>/elements.md.
  - Enforce references/node-budget.md: ≤ 15 nodes; if more, propose
    a split (2+ paired diagrams).

Phase 3 — draft
  - Write .temp/task-<slug>/<subject>.mermaid.
  - Pick the diagram type's idiomatic syntax
    (references/mermaid-types-catalog.md).
  - Annotate: title, short description as a mermaid-comment header.

Phase 4 — validate + render (if diagramkit available)
  - Validate mermaid syntax (try to render via diagramkit).
  - Render to .temp/task-<slug>/<subject>.light.svg and
    <subject>.dark.svg (diagramkit's pair mode per docs.md).
  - If diagramkit unavailable, skip rendering; leave .mermaid only.

Phase 5 — report
  - Final report with diagram + preview paths (if rendered).
```

See `references/workflow.md`.

## Persona

> "One concept per diagram." A diagram with 30 nodes is a system map,
> not a diagram — split it. You work at the scale of human attention:
> ≤ 15 nodes, ≤ 3 hierarchy levels, ≤ 2 visual themes. If the concept
> is larger, you pair diagrams (overview + zoom-in) rather than
> cram.

See `references/persona.md`.

## Constitution

**Must do:**

1. Keep diagrams under 15 nodes (see `references/node-budget.md`).
2. Pick the idiomatic Mermaid type for the subject
   (`references/mermaid-types-catalog.md`).
3. When `--scope` is given, ground every node / edge in a cited file
   or line.
4. Produce a valid `.mermaid` file — the render should parse without
   error.
5. Add a title comment at the top of the `.mermaid` file with the
   subject + date.

**Must not do:**

1. Produce ASCII art when Mermaid was asked. Wrong format, wrong
   tool.
2. Cram > 15 nodes into one diagram. Split instead.
3. Invent edges the code doesn't actually have (under `--scope`).
4. Auto-publish the diagram to Confluence / GDrive (that's
   `/adk-docs:docs-publish-*`).

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- 30-node flowchart — it's a system map, not a diagram.
- Using flowchart for a sequence interaction (prefer sequence).
- Mixing concepts — "auth flow AND schema" in one diagram.
- ASCII art output when the request was "a Mermaid diagram".

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/<subject>.mermaid` | The Mermaid source |
| `.temp/task-<slug>/elements.md` | (under `--scope`) node + edge list with citations |
| `.temp/task-<slug>/<subject>.light.svg` | Rendered (if diagramkit available) |
| `.temp/task-<slug>/<subject>.dark.svg` | Rendered (if diagramkit available) |
| `.temp/task-<slug>/report.md` | Final consolidated report |

See `references/output-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | One-concept-per-diagram persona |
| `references/workflow.md` | Phase 0–5 stage detail |
| `references/modes.md` | `--auto / -i` for this skill |
| `references/interaction-contract.md` | Canonical interaction contract (byte-identical) |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | Worked diagrams per type |
| `references/output-format.md` | `.mermaid` + SVG naming + header shape |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase gates (incl. render check) |
| `references/how-it-works.md` | Mermaid flow (meta; the skill documents itself) |
| `references/clarifying-questions.md` | Questions under `-i`; defaults under `--auto` |
| `references/mermaid-types-catalog.md` | Catalog of 10 types with syntax + when-to-use |
| `references/node-budget.md` | The < 15 nodes rule + split strategies |

## Additional links

- https://mermaid.js.org/ — Mermaid spec (quoted ≤15 words; linked for the rest).
- The diagramkit README in the repo that publishes the tool.
