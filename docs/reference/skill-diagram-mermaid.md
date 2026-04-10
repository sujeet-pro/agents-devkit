---
title: 'diagram-mermaid'
description: 'Create Mermaid diagrams with full syntax reference for all 21 diagram types. Supports light/dark mode via diagramkit'
skill_name: diagram-mermaid
category: task
workflow_tier: full
user_invocable: true
---

# diagram-mermaid

Use `diagram-mermaid` to create Mermaid diagrams with full syntax reference for all 21 diagram types. Supports light/dark mode via diagramkit. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`diagram-mermaid` belongs to the `task` layer and is declared at the `full` tier with the `quick-action` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--type` | `flowchart`, `sequence`, `class`, `state`, `er`, `gantt`, `gitgraph`, `mindmap`, `timeline`, `c4`, `architecture`, `kanban`, `quadrant`, `sankey`, `xy`, `packet`, `radar`, `journey`, `pie`, `requirement`, `block` | auto-detect | Diagram type |
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg`, `png` | `svg` | Output image format |
| `--theme` | `both`, `light`, `dark` | `both` | Theme variants to render |
| `--help` | flag | off | Show help |

### Parameter Notes

- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--render` changes the deliverable from source-only generation to source plus rendered assets.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family quick-action` | always | Quick Action workflow: confirm → execute → verify. For narrow tasks with single execution path. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before rendering | Run preflight.py for diagramkit and MCP validation. Ensure npm packages are installed. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Keep both editable source file and rendered SVG. |
| `/adk:workspace-conventions` | always | All work inside the project repo. Temp files in `.temp/<task-slug>/` (gitignored). Diagrams in `diagrams/` (sibling to doc, or project root). Both light+dark SVG and PNG. Respect `diagramkit.config.json` when present. Always commit source files with rendered output. |

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

### Workflow

### 1. Confirm

Confirm: diagram type, components to include, audience, output location. Invoke `/adk:workspace-conventions` to determine output location. For Trivial requests, 1-line inline confirm.

### 2. Execute

If `--type` is not specified, auto-detect from the description. Analyze requirements, identify components, relationships, and the best layout direction.

Write a `.mermaid` file to the determined output location following the type reference loaded below. Apply quality standards. Ensure `.temp/` is gitignored if using temp files.

File header:

```
%% Diagram: <title>
%% Type: <diagram-type>
```

### 3. Verify

Run the rendering pipeline (see Rendering Pipeline below). Validate syntax, check for reserved word conflicts, verify renderability.

```
Mermaid diagram complete:
  Source: ./diagrams/<name>.mermaid
  Output:
    ./diagrams/<name>-light.svg
    ./diagrams/<name>-dark.svg
    ./diagrams/<name>-light.png
    ./diagrams/<name>-dark.png
```

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


## Related Skills

### Adjacent Skills

- `/adk:diagram` — parent routing skill that auto-detects engine
- `/adk:diagram-excalidraw` — hand-drawn architecture diagrams
- `/adk:diagram-drawio` — precise layout with rich icon library
- `/adk:diagram-graphviz` — strict DOT layout for dependency graphs
- `/adk:docs-write` — documentation that may embed diagrams

## Additional Reference

### Human in the Loop

- **Plan first (Phase 0)**: Always confirm intent — diagram type, scope, and audience — before generating.
- **Auto mode**: When invoked with `--auto` or by a parent skill, skip confirmations and proceed directly.

### Type Selection

Based on `--type` parameter or auto-detection from the description, load the matching type reference:

| Type | Reference File | When |
|------|---------------|------|
| flowchart | `${CLAUDE_SKILL_DIR}/references/types/flowchart.md` | Default for process/workflow/pipeline/decision descriptions |
| sequence | `${CLAUDE_SKILL_DIR}/references/types/sequence.md` | Message passing, API calls, protocol exchanges |
| class | `${CLAUDE_SKILL_DIR}/references/types/class.md` | OOP class hierarchies, interfaces, relationships |
| state | `${CLAUDE_SKILL_DIR}/references/types/state.md` | State machines, status transitions |
| er | `${CLAUDE_SKILL_DIR}/references/types/er.md` | Database entity relationships |
| gantt | `${CLAUDE_SKILL_DIR}/references/types/gantt.md` | Project timelines, task scheduling |
| mindmap | `${CLAUDE_SKILL_DIR}/references/types/mindmap.md` | Concept maps, brainstorming |
| timeline | `${CLAUDE_SKILL_DIR}/references/types/timeline.md` | Historical events, release timelines |
| c4 | `${CLAUDE_SKILL_DIR}/references/types/c4.md` | C4 architecture diagrams |
| pie | `${CLAUDE_SKILL_DIR}/references/types/pie.md` | Pie/donut charts |
| quadrant | `${CLAUDE_SKILL_DIR}/references/types/quadrant.md` | Priority/evaluation matrices |
| sankey | `${CLAUDE_SKILL_DIR}/references/types/sankey.md` | Flow/resource distribution |
| xy | `${CLAUDE_SKILL_DIR}/references/types/xy.md` | XY scatter/line/bar charts |
| block | `${CLAUDE_SKILL_DIR}/references/types/block.md` | Block diagrams |
| architecture | `${CLAUDE_SKILL_DIR}/references/types/architecture.md` | Architecture icon diagrams |
| gitgraph | `${CLAUDE_SKILL_DIR}/references/types/gitgraph.md` | Git branch visualization |
| journey | `${CLAUDE_SKILL_DIR}/references/types/journey.md` | User journey maps |
| kanban | `${CLAUDE_SKILL_DIR}/references/types/kanban.md` | Kanban boards |
| packet | `${CLAUDE_SKILL_DIR}/references/types/packet.md` | Network packet diagrams |
| radar | `${CLAUDE_SKILL_DIR}/references/types/radar.md` | Radar/spider charts |
| requirement | `${CLAUDE_SKILL_DIR}/references/types/requirement.md` | Requirement diagrams |

Load ONLY the single type reference file that matches the user's request. Do NOT load multiple type files.

### Rendering Pipeline

Rendering always produces both **light and dark** variants in **SVG and PNG** by default.

### Step 1: Determine Output Location

1. If a `diagramkit.config.json` exists at the project root → use its `outputDir` setting
2. If invoked by a doc skill → place in `diagrams/` folder sibling to the document
3. Otherwise → place in `./diagrams/` at the project root

### Step 2: Render with diagramkit (Primary)

```bash
# SVG — both light and dark
diagramkit render diagram.mermaid --format svg --theme both

# PNG — both themes, 2x scale for retina
diagramkit render diagram.mermaid --format png --theme both --scale 2
```

diagramkit renders Mermaid using a headless browser with Mermaid's built-in renderer. For dark mode, it applies `postProcessDarkSvg` which adjusts background, text colors, and element fills for WCAG-compliant contrast on dark surfaces.

If the project has a `diagramkit.config.json`, diagramkit reads it automatically for output directory, default format, theme, and scale.

### Step 3: Fallback — Mermaid CLI (`mmdc`)

If diagramkit is not installed or fails, use the Mermaid CLI directly.

**Install:** `npm install -g @mermaid-js/mermaid-cli`

```bash
# Light variants
mmdc -i diagram.mermaid -o diagrams/diagram-light.svg --theme default
mmdc -i diagram.mermaid -o diagrams/diagram-light.png --theme default

# Dark variants
mmdc -i diagram.mermaid -o diagrams/diagram-dark.svg --theme dark
mmdc -i diagram.mermaid -o diagrams/diagram-dark.png --theme dark
```

### Step 4: Verify Outputs

Confirm these files exist:
- `<name>-light.svg` and `<name>-dark.svg`
- `<name>-light.png` and `<name>-dark.png`

### Theming & Dark Mode

Load `${CLAUDE_SKILL_DIR}/references/theming.md` when applying styles. Summary: avoid hardcoded hex unless needed; prefer `classDef` for repeated styles; hex-only (no color names); diagramkit `postProcessDarkSvg` fixes default theme contrast for dark output.

`classDef` example: `classDef primary fill:#4C78A8,stroke:#2E5A88,color:#fff`

### Quality Standards

1. **Max ~15 nodes** — split complex systems into focused diagrams.
2. **Semantic IDs** — `api_gateway` not `A`.
3. **Subgraphs** for 3+ related nodes; **edge styling**: solid sync, dotted async, thick critical path.
4. **Clear labels**, **readable flow** (`TD` hierarchies, `LR` sequences), **header comment** with title.

### Known Limitations

Platform ~5k byte caps; huge flowcharts hit "too many edges"; reserved words (`end`, `default`) need quoting; self-loops look weak vs Graphviz; beta diagram types may change; theme engine is hex-only.

---

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:diagram-mermaid
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:diagram-mermaid --render --format png <prompt-text>
```
