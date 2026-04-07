---
name: adk-diagram-mermaid
description: "adk - [full] [diagram] Create Mermaid diagrams with full syntax reference for all 21 diagram types. Supports light/dark mode via diagramkit."
user-invocable: true
argument-hint: "<description> [--type flowchart|sequence|class|state|er|gantt|mindmap|timeline|c4|...] [--render] [--format svg|png] [--theme both|light|dark]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, Agent]
dependencies:
  commands: [git]
  npm-packages: [diagramkit]
workflow-tier: full
---

# Mermaid Diagram

Create diagrams using Mermaid syntax. Supports 21 Mermaid v11 diagram types (one type ref each; see Type Selection). Writes a `.mermaid` source file — use `diagramkit render` to produce images with automatic light/dark mode variants.

This skill can be invoked directly or via `/adk:diagram --engine mermaid`.

Accepted file extensions: `.mermaid`, `.mmd`, `.mmdc`

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before rendering | Run preflight.py for diagramkit and MCP validation. Ensure npm packages are installed. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Keep both editable source file and rendered SVG. |

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/adk-<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--type` | `flowchart`, `sequence`, `class`, `state`, `er`, `gantt`, `gitgraph`, `mindmap`, `timeline`, `c4`, `architecture`, `kanban`, `quadrant`, `sankey`, `xy`, `packet`, `radar`, `journey`, `pie`, `requirement`, `block` | auto-detect | Diagram type |
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg`, `png` | `svg` | Output image format |
| `--theme` | `both`, `light`, `dark` | `both` | Theme variants to render |
| `--help` | flag | off | Show help |

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the goal, diagram type, and scope |
| 1. Research & Options | yes | Analyze requirements, determine structure |
| 2. Approach Selection | skip | Direct execution after confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Generate diagram source file |
| 5. Validate & Learn | yes | Verify renderability, naming, consistency |

## Human in the Loop

- **Plan first (Phase 0)**: Always confirm intent — diagram type, scope, and audience — before generating.
- **Auto mode**: When invoked with `--auto` or by a parent skill, skip confirmations and proceed directly.

## Workflow

### Phase 0: Intent Confirmation

Confirm: diagram type, components to include, audience, output location. For Trivial requests, 1-line inline confirm.

### Phase 1: Determine Type & Structure

If `--type` is not specified, auto-detect from the description. Analyze requirements, identify components, relationships, and the best layout direction.

### Phase 4: Generate Mermaid Source

Write a `.mermaid` file following the type reference loaded below. Apply quality standards.

File header:

```
%% Diagram: <title>
%% Type: <diagram-type>
```

### Phase 5: Validate & Report

Validate syntax, check for reserved word conflicts, verify renderability.

```
Mermaid source file written:
  Source: ./diagrams/<name>.mermaid

Render with: diagramkit render ./diagrams/<name>.mermaid
```

## Type Selection

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

## Rendering

```bash
# Default: both light and dark SVG variants
diagramkit render diagram.mermaid

# PNG only, light mode
diagramkit render diagram.mermaid --format png --theme light

# Both themes, custom scale
diagramkit render diagram.mermaid --format png --scale 2
```

diagramkit renders Mermaid using a headless browser with Mermaid's built-in renderer. For dark mode, it applies `postProcessDarkSvg` which adjusts background, text colors, and element fills for WCAG-compliant contrast on dark surfaces.

## Theming & Dark Mode

Load `${CLAUDE_SKILL_DIR}/references/theming.md` when applying styles. Summary: avoid hardcoded hex unless needed; prefer `classDef` for repeated styles; hex-only (no color names); diagramkit `postProcessDarkSvg` fixes default theme contrast for dark output.

`classDef` example: `classDef primary fill:#4C78A8,stroke:#2E5A88,color:#fff`

## Quality Standards

1. **Max ~15 nodes** — split complex systems into focused diagrams.
2. **Semantic IDs** — `api_gateway` not `A`.
3. **Subgraphs** for 3+ related nodes; **edge styling**: solid sync, dotted async, thick critical path.
4. **Clear labels**, **readable flow** (`TD` hierarchies, `LR` sequences), **header comment** with title.

## Known Limitations

Platform ~5k byte caps; huge flowcharts hit "too many edges"; reserved words (`end`, `default`) need quoting; self-loops look weak vs Graphviz; beta diagram types may change; theme engine is hex-only.

---

## Adjacent Skills

- `/adk:diagram` — parent routing skill that auto-detects engine
- `/adk:diagram-excalidraw` — hand-drawn architecture diagrams
- `/adk:diagram-drawio` — precise layout with rich icon library
- `/adk:diagram-graphviz` — strict DOT layout for dependency graphs
- `/adk:docs-write` — documentation that may embed diagrams
