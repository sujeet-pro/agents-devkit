---
name: adk-diagram
description: "[full] [diagram] Use when creating diagrams — auto-detects engine or use --engine flag"
user-invocable: true
argument-hint: "<description> [--engine mermaid|excalidraw|drawio|graphviz] [--type flowchart|sequence|class|state|er|gantt|mindmap|...] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
  npm-packages: [diagramkit]
workflow-tier: full
---

# Diagram

Unified diagram skill: creates diagrams using the best engine for the job. Auto-detects the right engine from context and diagram type, or accepts an explicit `--engine`. Supports Mermaid, Excalidraw, draw.io, and Graphviz.

Load references: `references/workflow-6phase.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`. For Medium/Large: also load `references/agentic-teams.md`, `references/principal-engineer.md`.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--engine` | `mermaid`, `excalidraw`, `drawio`, `graphviz` | auto-detect | Force a specific diagram engine |
| `--type` | `flowchart`, `sequence`, `class`, `state`, `er`, `gantt`, `mindmap`, `timeline`, `architecture`, `network`, `freeform`, etc. | auto-detect | Diagram type hint for engine selection |
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg`, `png`, `jpeg`, `webp` | `svg` | Output image format (when rendering) |
| `--theme` | `both`, `light`, `dark` | `both` | Theme variants to render |
| `--scale` | `<number>` | `1` | Scale factor for raster output |
| `--quality` | `<number>` | `85` | Quality for lossy formats |
| `--palette` | `<name>` | default | Color palette (Excalidraw) |
| `--style` | `<name>` | none | Style preset |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Behavior Variations

- **`--engine mermaid`**: Text-based diagrams. Best for flowcharts, sequence, ER, class, state, timeline, mindmap, Gantt, C4. Diffs well in Git.
- **`--engine excalidraw`**: Hand-drawn feel. Best for architecture overviews, system context, freeform layouts, hub-and-spoke. Produces `.excalidraw` JSON.
- **`--engine drawio`**: Precise layout with rich icon library. Best for network topology, enterprise architecture, BPMN, multi-page. Produces `.drawio` XML.
- **`--engine graphviz`**: Strict DOT layout. Best for existing `.dot` assets, dependency graphs, strict graph layout. Use only when repo already uses Graphviz.
- **Engine-specific parameters** (`--palette`, `--style`): Silently ignored when the selected engine does not support them.

### Examples

```
/adk-diagram architecture overview of the auth system
/adk-diagram --engine mermaid --type sequence user login flow
/adk-diagram --engine excalidraw system architecture from codebase
/adk-diagram --engine drawio AWS infrastructure layout
/adk-diagram --engine graphviz update the dependency graph
/adk-diagram --render --format png --scale 2 deployment pipeline
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

If `--engine` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the engine:

| Signal | Engine | Stage File |
|---|---|---|
| Flowchart, sequence, ER, class, state, timeline, mindmap, Gantt, C4, gitgraph, kanban, quadrant, sankey, XY, packet, radar, journey, pie, requirement, block | mermaid | `stages/mermaid.md` |
| Architecture overview, system context, freeform, hub-and-spoke, codebase map, PR overview | excalidraw | `stages/excalidraw.md` |
| Network topology, enterprise, BPMN, org chart, multi-page, AWS/Azure/GCP detailed infrastructure | drawio | `stages/drawio.md` |
| Existing `.dot` files, strict graph layout, dependency graphs, legacy Graphviz assets | graphviz | `stages/graphviz.md` |

### Engine Selection Rules

When `--engine` is not specified, auto-detect:

1. `--type=freeform` -> **Excalidraw**.
2. `--type=network` with "topology", "rack", "physical" -> **Draw.io**.
3. `--type=architecture` with "overview", "high-level", "system context" -> **Excalidraw**.
4. `--type=architecture` with "AWS", "Azure", "GCP" + "detailed" -> **Draw.io**.
5. `--type` is `sequence`, `class`, `state`, `er`, `gantt`, `gitgraph`, `mindmap`, `timeline`, `kanban`, `quadrant`, `sankey`, `xy`, `packet`, `radar`, `journey`, `c4` -> **Mermaid**.
6. "BPMN", "business process", "org chart", "multi-page" -> **Draw.io**.
7. "codebase", "project structure", "repo overview", "architecture diagram" -> **Excalidraw**.
8. "flowchart", "process", "workflow", "pipeline", "decision tree" -> **Mermaid**.
9. Default -> **Mermaid**.

### Default Preference Order

When the diagram type could work with multiple engines: **Mermaid > Excalidraw > draw.io > Graphviz**

### Context Signals

- If the project already uses a specific engine (check for `.mmd`, `.mermaid`, `.excalidraw`, `.drawio`, `.dot` files), prefer that engine for consistency.
- If `--render` is specified, ensure the selected engine can produce rendered output.

After selecting the engine, load the corresponding stage file and follow its instructions.

## Common Phases

All engines share the 6-phase workflow from `references/workflow-6phase.md`. Each stage file defines which phases apply.

### Phase 0: Intent Expansion

Follow the stage file's intent confirmation guidance. Always run this phase before taking action.

### Phase 1: Research & Options

Follow the stage file's exploration guidance. Every engine uses this phase, though simpler requests may keep it brief.

### Phase 2: Approach Selection

Use this phase when the user needs to choose notation, layout, or scope. Simpler requests may skip it.

### Phase 3: Planning

Use this phase when the diagram needs a multi-step build plan. Simpler requests may skip it and move directly from approval to execution.

### Phase 4: Execute

Follow the stage file's execution instructions.

### Phase 5: Validate & Learn

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Source file path only
- **standard**: Full report with engine, source path, and rendered output paths
- **detailed**: Standard output plus engine selection rationale, validation results, and rendering details

## Adjacent Skills

- `/adk-plan` -- planning workflows that may need architecture diagrams
- `/adk-spec` -- specifications that may need visual documentation
- `/adk-write` -- documentation that may embed diagrams
