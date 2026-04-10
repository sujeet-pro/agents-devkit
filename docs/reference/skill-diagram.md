---
title: 'diagram'
description: 'Diagram router — auto-detects the best engine and routes to the right diagram skill'
skill_name: diagram
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# diagram

Use `diagram` when you want DevKit to route diagram work to the right downstream skill. Its job is classification and parameter forwarding, not doing the downstream work itself.

## Overview

`diagram` belongs to the `routing` layer and is declared at the `orchestrator` tier with the `quick-action` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--engine` | `mermaid`, `excalidraw`, `drawio`, `graphviz` | auto-detect | Force a specific engine |
| `--type` | `flowchart`, `sequence`, etc. | auto-detect | Diagram type hint |
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg`, `png` | `svg` | Output format (both SVG and PNG produced by default) |
| `--theme` | `both`, `light`, `dark` | `both` | Theme variants to render |
| `--help` | flag | off | Show help |

### Parameter Notes

- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--engine` bypasses routing and sends the request to one specific diagram backend.
- `--render` changes the deliverable from source-only generation to source plus rendered assets.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Routing begins by resolving intent. Explicit override flags take priority; otherwise the detection rules below choose a downstream skill, stage, or engine based on the prompt and repository context.

Once the route is fixed, the router keeps parameter forwarding narrow and predictable so the downstream skill receives the same important selectors the user provided.

### Shared Skills

| Helper skill | Invoke (Claude plugin) | Invoke (Codex / skills.sh) | When | Inline fallback |
|--------------|------------------------|------------------------------|------|-----------------|
| preflight-check | `/adk:preflight-check` | `/preflight-check` | before work | Run preflight.py for tool dependencies. |

### Preflight

```
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}
```

### Workspace Conventions

Invoke `/adk:workspace-conventions` to determine output paths. Key rules:

- **Output location**: `diagrams/` folder sibling to the document (if doc-related), or `./diagrams/` at project root
- **diagramkit.config.json**: If present at project root, use its settings for output directory, format, and theme
- **Theme**: Always produce both light and dark variants by default (`--theme both`)
- **Formats**: Produce SVG (vector) and PNG (raster) output
- **Temp files**: Use `.temp/<task-slug>/` for intermediary artifacts; gitignore `.temp/` on first use
- **Source files**: Always commit alongside rendered output

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Routing

If `--engine` is explicitly provided, route directly to the matching engine skill. Otherwise, auto-detect:

| Signal | Engine | Route To |
|--------|--------|----------|
| `--type=freeform`, "architecture overview", "system context", "codebase map" | Excalidraw | `/adk:diagram-excalidraw` |
| `--type=network` with "topology", "rack", "physical"; BPMN, org chart, multi-page | Draw.io | `/adk:diagram-drawio` |
| Existing `.dot` files, "dependency graph", strict graph layout | Graphviz | `/adk:diagram-graphviz` |
| All other types: flowchart, sequence, class, state, ER, gantt, mindmap, timeline, C4, etc. | Mermaid | `/adk:diagram-mermaid` |

### Engine Selection Rules

1. `--type=freeform` -> Excalidraw
2. `--type=network` with "topology", "rack", "physical" -> Draw.io
3. `--type=architecture` with "overview", "high-level", "system context" -> Excalidraw
4. `--type=architecture` with "AWS", "Azure", "GCP" + "detailed" -> Draw.io
5. `--type` is `sequence`, `class`, `state`, `er`, `gantt`, `gitgraph`, `mindmap`, `timeline`, `kanban`, `quadrant`, `sankey`, `xy`, `packet`, `radar`, `journey`, `c4` -> Mermaid
6. "BPMN", "business process", "org chart", "multi-page" -> Draw.io
7. "codebase", "project structure", "repo overview" -> Excalidraw
8. "flowchart", "process", "workflow", "pipeline", "decision tree" -> Mermaid
9. Default -> Mermaid

### Context Signals

Check for existing diagram files in the project (`.mmd`, `.mermaid`, `.excalidraw`, `.drawio`, `.dot`) and prefer that engine for consistency.

### Default Preference Order

Mermaid > Excalidraw > Draw.io > Graphviz

### Parameter Forwarding

Pass all parameters to the target engine skill. The router does not consume parameters except `--engine` and `--help`.

### Sub-Skills

| Skill | Description |
|-------|-------------|
| `/adk:diagram-mermaid` | Text-based diagrams. Best for flowcharts, sequence, ER, class, state, timeline, mindmap, Gantt, C4. |
| `/adk:diagram-excalidraw` | Hand-drawn feel. Best for architecture overviews, system context, freeform layouts. |
| `/adk:diagram-drawio` | Precise layout with rich icon library. Best for network topology, enterprise architecture, BPMN. |
| `/adk:diagram-graphviz` | Strict DOT layout. Best for dependency graphs, strict graph layout, existing `.dot` assets. |

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


## Related Skills

### Adjacent Skills

- `/adk:docs-write` — documentation that may embed diagrams
- `/adk:plan` — planning workflows that may need architecture diagrams
- `/adk:spec` — specifications that may need visual documentation

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:diagram
/adk:diagram --engine mermaid <prompt-text>
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:diagram --engine mermaid <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:diagram --render --format png <prompt-text>
```
