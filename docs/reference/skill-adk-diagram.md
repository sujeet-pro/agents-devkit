---
title: 'adk-diagram'
description: 'Create or update markdown docs with editable diagram source files across Mermaid, Excalidraw, Draw.io, and Graphviz, rendered via diagramkit. Use when a document needs a maintained in-repo diagram'
skill_name: adk-diagram
category: task
workflow_tier: full
user_invocable: true
---

# adk-diagram

Use `adk-diagram` to create or update markdown docs with editable diagram source files across Mermaid, Excalidraw, Draw.io, and Graphviz, rendered via diagramkit. Use when a document needs a maintained in-repo diagram. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-diagram` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<diagram-request>` | free text | required | What the diagram should explain |
| `--doc` | markdown path | none | Markdown file to create or update |
| `--name` | kebab-case slug | inferred | Diagram file base name |
| `--engine` | `mermaid`, `excalidraw`, `drawio`, `graphviz` | inferred | Force a specific diagram engine |
| `--type` | engine-specific type | inferred | Diagram type or hint for engine selection |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show this skill description and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--engine` bypasses routing and sends the request to one specific diagram backend.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

1. **Understand** -- clarify what needs to be visualized, the audience, the target document, and the preferred format. *Gate: user confirms unless `--auto`.*
2. **Choose Engine** -- select based on diagram type using this quick decision matrix (see `references/engines-and-types.md` for full routing):

   | Signal | Engine | Then read |
   | --- | --- | --- |
   | flow, sequence, ER, class, state, timeline, gantt, C4, mindmap | **Mermaid** | `references/mermaid.md` |
   | freeform architecture, system context, hand-drawn overview | **Excalidraw** | `references/excalidraw.md` |
   | network topology, cloud infra, BPMN, org chart, multi-page | **Draw.io** | `references/drawio.md` |
   | dependency graph, call graph, strict hierarchy, existing `.dot` | **Graphviz** | `references/graphviz.md` |

   If `--engine` is given, respect it unless clearly incompatible. Check project conventions for existing engine preferences.

3. **Draft** -- create the diagram source in the chosen format. Present source for review. *Gate: user approves source unless `--auto`.*
4. **Render** -- generate visual output (SVG preferred) via diagramkit. Validate rendering succeeded.
5. **Iterate** -- refine based on user feedback. *Gate: user review of rendered output.*
6. **Deliver** -- place the diagram in docs with editable source alongside rendered output. Update markdown embed. Verify all references align.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/README.md`
- `references/diagramkit-integration.md`
- `references/drawio.md`
- `references/engines-and-types.md`
- `references/excalidraw.md`
- `references/graphviz.md`
- `references/markdown-integration.md`
- `references/mermaid.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- confirm diagram purpose, engine, and type before drafting; present the source for review before rendering. `--auto` skips confirmations.
- **Plan First** -- phased workflow: understand the need, choose the engine, draft, render, then verify. No rendering without source review.
- **Light Brainstorm Gate** -- if the real deliverable, audience, or engine choice is still ambiguous, run a short brainstorming pass before drafting the source.
- **Concise by Default** -- prefer the smallest diagram that explains the point; offer to add detail on request.
- **Self-Sufficient Skills** -- works independently; degrades gracefully when diagramkit is unavailable (leaves source file for manual render).
- **Markdown by Default** -- diagrams are embedded in markdown with editable source alongside rendered output.

### Persona

**Visual Communication Specialist.** Mission: turn written explanations into clear, maintainable diagrams that stay editable and in sync with their documentation. Chooses the right engine for the job, keeps diagrams minimal, and ensures the markdown document and rendered asset stay connected.

Hard rules:
- Prefer the smallest diagram that explains the point.
- Keep the editable source file alongside the rendered output.
- Choose the right engine for the diagram type -- do not force Mermaid for everything.
- Update the markdown embed, not just the asset files.
- Never leave broken or stale diagram references behind.
- Use diagramkit for rendering when available; degrade gracefully without it.

Evidence expectations:
- Read the current markdown and source material before drafting.
- Cite the documentation context that the diagram supports.
- Note when rendering could not run and why.

### When To Use

- A README, ADR, guide, or reference doc needs a diagram
- An existing markdown document has a stale architecture or flow diagram
- You want the diagram source committed next to the rendered output
- You need Mermaid, Excalidraw, Draw.io, or Graphviz from one skill

### When NOT To Use

- One-off image generation outside the repo
- Data charts (bar, line, pie) -- use `adk-chart`
- UI mockups or design work -- use `adk-design`
- Diagrams that do not need to be version-controlled

### Pre-flight

Before starting, verify:
- `git`, `node`, `npx`, and `python3` are available on PATH
- If diagramkit is needed, check availability (`npx diagramkit --version`)
- If `--doc` is provided, the target markdown file exists or can be created
- If `--engine` is provided, the engine is supported

### Reference Routing

- Start with `references/README.md` and `references/engines-and-types.md`.
- Read exactly one engine guide for the selected backend.
- If Mermaid is selected, jump to the matching type section in `references/mermaid.md`.
- Use `references/diagramkit-integration.md` for render behavior and `references/markdown-integration.md` for embeds.

### Interaction Protocol

### Intent Confirmation (Phase 1)
Before starting, confirm:
- Diagram purpose and what it should explain
- Target markdown document
- Engine (Mermaid, Excalidraw, Draw.io, Graphviz) and diagram type
- Skip when `--auto` is set

### Source Review (Phase 3)
Present the diagram source before rendering:

```
Proposed Mermaid flowchart for docs/architecture.md:
  graph TD
    A[Client] --> B[API Gateway]
    B --> C[Auth Service]
    B --> D[User Service]
```

Wait for user to approve or adjust before rendering.

### Render Confirmation (Phase 4)
After rendering, report the output:

```
Rendered: docs/diagrams/architecture.svg
Updated: docs/architecture.md (line 42)
```

### User Responses
- `ok` -- approve and render (or finalize)
- feedback text -- revise the diagram source
- `engine X` -- switch to a different engine
- `done` -- finalize

### Parallel Agents

| Agent | Dispatched When | Purpose |
| --- | --- | --- |
| `adk-diagram-renderer` | Multiple diagrams need rendering in parallel | Batch rendering of independent diagram sources |

### Validation

<render status, link verification>

Need more detail?
```

### Diagram: <description>



### Engine

<selected engine and type with rationale>

### Files

- Source: <path to editable source file>
- Rendered: <path to SVG output>
- Doc: <path to updated markdown> (line <N>)

### Embed

<the markdown embed that was inserted or updated>

### Anti-Patterns / Red Flags

- Using Mermaid for everything regardless of diagram type
- Rendering without presenting the source for review first
- Leaving broken markdown embeds pointing at missing assets
- Creating diagrams without committing the editable source
- Over-complicated diagrams that obscure rather than clarify
- Choosing an engine without considering the diagram's maintenance needs
- Ignoring existing diagram conventions in the project

### Related Skills

- `adk-chart` -- data visualization (bar, line, pie charts)
- `adk-write-docs` -- documentation that may need diagrams
- `adk-plan` -- architecture planning that diagrams can illustrate

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-diagram <diagram-request>
adk-diagram --engine mermaid <prompt-text>
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
adk-diagram --engine mermaid <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-diagram <diagram-request> --auto
```
