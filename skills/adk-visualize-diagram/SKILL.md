---
name: adk-visualize-diagram
description: Produce a structural diagram - sequence, flow, state, ER, architecture, dependency, class, deployment - by drafting an editable source file (mermaid, drawio, excalidraw, graphviz dot) and then rendering to the destination format. Use when the deliverable is a structural picture, not a data chart. Do not use for numeric/categorical plots (use adk-visualize-chart) or UI mockups (use adk-frontend-design).
---

# ADK Visualize / Diagram

Standalone task skill under the `adk-visualize` category router. Produces an editable diagram source first, then renders to the destination format. Editable source is always kept alongside the rendered output.

## When to use

- Sequence, flow, state, ER, architecture, dependency, class, or deployment diagrams.
- Existing diagram needs regeneration, restyling, or format conversion.
- Diagram must be embedded in a markdown doc, a wiki page, or a slide.

## When NOT to use

- Numeric / categorical data plot -> `adk-visualize-chart`
- UI mockup or component design -> `adk-frontend-design`
- Architecture write-up (text + one diagram) -> `adk-plan-design`, which can call this skill for the diagram

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<diagram type>` | yes | `sequence` / `flow` / `state` / `er` / `architecture` / `dependency` / `class` / `deployment` |
| `<source description or data>` | yes | Free-text description, code paths to diagram, or a structured spec |
| `<format>` | optional | `mermaid` (default for markdown) / `drawio` / `excalidraw` / `graphviz` |
| `<render>` | optional | `none` (default - just source) / `svg` / `png` |
| `<output path>` | optional | Defaults to `.temp/drafts/diagram-<slug>.<ext>` |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate diagram type, source, format, render target, destination. Approval gate unless `--auto`.
2. **Gather** - read the source-of-truth: code, schema, sequence of API calls, deployment manifest. For conceptual diagrams, capture the user's mental model in a short list of nodes + edges.
3. **Draft source** - write the editable source first (mermaid `.mmd`, drawio `.drawio`, excalidraw `.excalidraw`, graphviz `.dot`).
4. **Sanity check** - count nodes (cap ~12 per single-view diagram); verify every edge has both endpoints; confirm no node names collide.
5. **Render** - if `<render>` is requested, produce the SVG / PNG and place it next to the source file with the same basename.
6. **Validate** - visually scan: no overlapping nodes, no disconnected fragments unless intentional, legend / labels present.
7. **Report** - editable source path, render path (if any), node/edge counts; offer to tweak.

## Format defaults

| Destination | Default format |
| --- | --- |
| Markdown (README, PR) | mermaid (embedded fenced block) |
| GitHub wiki / Confluence | mermaid (both render natively in 2026) |
| drawio canvas / advanced layouts | drawio |
| Hand-drawn aesthetic / brainstorm | excalidraw |
| Complex graph layout | graphviz |
| Slide deck or print | render to SVG (vector) or PNG @ 300dpi |

## Mermaid quick reference

This skill produces mermaid by default for markdown destinations. Honor the syntax constraints below to avoid breakage.

- Do NOT use spaces in node ids; use camelCase or snake_case (`userService` / `user_service`).
- Quote labels with parentheses, brackets, colons, or commas: `A["Process (main)"]`.
- Avoid reserved keywords as ids (`end`, `subgraph`, `graph`, `flowchart`).
- For subgraphs, use explicit ids with bracketed labels: `subgraph auth [Authentication Flow]`.
- Do not set explicit colors or `classDef fill:` - let the renderer apply theme colors.
- Click events are disabled in many renderers; do not use `click`.

## Diagram-type templates

### Sequence

```mermaid
sequenceDiagram
    actor User
    participant API
    participant DB
    User->>API: POST /login
    API->>DB: SELECT user
    DB-->>API: row
    API-->>User: 200 + token
```

### Flow

```mermaid
flowchart LR
    start[Start] --> check{Valid?}
    check -->|yes| ok[Process]
    check -->|no| err[Reject]
    ok --> done[Done]
    err --> done
```

### State

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Loading: fetch
    Loading --> Ready: ok
    Loading --> Error: fail
    Ready --> [*]
```

### ER

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : included
```

### Class

```mermaid
classDiagram
    class Cache {
      +get(key): Value
      +set(key, value): void
    }
    class RedisCache
    Cache <|-- RedisCache
```

## Output format

```
## Diagram: <type>
- Source: `<path>`
- Render: `<path or none>`
- Format: <mermaid | drawio | excalidraw | graphviz>
- Nodes: <N>
- Edges: <M>

## Preview
<embed the rendered diagram inline if mermaid + markdown destination>

## Notes
- <any layering / readability tradeoffs>

Want a tweak (split, restyle, alternate layout)?
```

## Hard rules

- Always keep the editable source file alongside any binary render.
- Cap a single-view diagram at ~12 nodes; split into layered diagrams beyond that.
- Sequence diagrams: 1 actor / participant per swim lane; do not stack roles.
- Flow / state diagrams: every decision node has labeled edges.
- ER diagrams: every relationship has a cardinality.

## Anti-patterns

- Producing a binary without the source ("source of truth lives in the .png").
- Cramming 30 nodes into one view; nobody reads it.
- Mermaid syntax errors from spaces in node ids - they are silent failures in some renderers.
- Color-coding that breaks in dark mode (do not set explicit colors).
- Using `click` syntax that is disabled in your destination.

## Examples

```
adk-visualize-diagram sequence "user login flow with API and Redis"
```

```
adk-visualize-diagram architecture --format drawio --render svg --output docs/diagrams/system.drawio
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/visualize-diagram-clarifying-questions.md`) and reports the choices.

1. **Diagram type: sequence / flowchart / class / state / entity-relationship / architecture / dependency-graph / mind-map / freeform UX?** — _How to pick:_ Sequence/flowchart/class/state/ER/mind → mermaid. Large dependency graph → graphviz. Architecture with rich shapes → drawio. UX sketch → excalidraw.
2. **Source-of-truth for the diagram content (code path, spec, ticket, manual description)?** — _How to pick:_ Code/spec for engineering diagrams (must verify). Manual description for UX sketches.
3. **Where does it live (page README, dedicated docs page, slide deck)?** — _How to pick:_ Page README → keep simple. Docs page → can be detailed. Slide → simplify; one idea per diagram.

**Default report:** Path to source file + path to rendered light/dark SVGs + the markdown snippet to embed.

**Detailed report (on request or `--verbose`):** Add: alt text suggestions, complexity check (node/edge count), recommended further diagrams to break things up.

**Artifact:** `diagram-source-and-renders` — Source file (`*.mermaid` / `*.dot` / `*.drawio` / `*.excalidraw`) + rendered `*-light.svg` and `*-dark.svg`.

**Artifact path:** Lives next to the page that embeds it: `<page-dir>/diagrams/<name>.<ext>` and `<page-dir>/diagrams/<name>-light.svg` / `-dark.svg`. Working drafts in `.temp/drafts/diagrams/`.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/visualize-diagram-clarifying-questions.md`) and reports the choices.

1. **Diagram type: sequence / flowchart / class / state / entity-relationship / architecture / dependency-graph / mind-map / freeform UX?** — _How to pick:_ Sequence/flowchart/class/state/ER/mind → mermaid. Large dependency graph → graphviz. Architecture with rich shapes → drawio. UX sketch → excalidraw.
2. **Source-of-truth for the diagram content (code path, spec, ticket, manual description)?** — _How to pick:_ Code/spec for engineering diagrams (must verify). Manual description for UX sketches.
3. **Where does it live (page README, dedicated docs page, slide deck)?** — _How to pick:_ Page README → keep simple. Docs page → can be detailed. Slide → simplify; one idea per diagram.

## Default vs detailed output

**Default report:** Path to source file + path to rendered light/dark SVGs + the markdown snippet to embed.

**Detailed report (on request or `--verbose`):** Add: alt text suggestions, complexity check (node/edge count), recommended further diagrams to break things up.

**Artifact:** `diagram-source-and-renders` — Source file (`*.mermaid` / `*.dot` / `*.drawio` / `*.excalidraw`) + rendered `*-light.svg` and `*-dark.svg`.

**Artifact path:** Lives next to the page that embeds it: `<page-dir>/diagrams/<name>.<ext>` and `<page-dir>/diagrams/<name>-light.svg` / `-dark.svg`. Working drafts in `.temp/drafts/diagrams/`.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/visualize-diagram-anti-patterns.md` | Things to avoid when running this skill. |
| `references/visualize-diagram-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/visualize-diagram-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/visualize-diagram-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/visualize-diagram-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/visualize-diagram-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/visualize-diagram-persona.md` | The agent persona that drives this skill. |
| `references/visualize-diagram-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/visualize-diagram-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
