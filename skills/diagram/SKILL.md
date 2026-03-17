---
name: diagram
description: Orchestrate diagram generation using Mermaid or Excalidraw. Selects the best tool based on diagram purpose and delegates to the appropriate skill.
user_invocable: true
arguments:
  - name: description
    description: "Description of what to diagram"
    required: true
  - name: type
    description: "Diagram type: flowchart, sequence, class, state, er, architecture, freeform, mindmap, timeline, gantt, c4, gitgraph, kanban, quadrant, sankey, xy, packet, radar, journey, requirement (default: auto-detect)"
    required: false
  - name: engine
    description: "Rendering engine: mermaid, excalidraw, auto (default: auto)"
    required: false
  - name: format
    description: "Output format: svg, jpeg, both (default: svg)"
    required: false
  - name: output-dir
    description: "Output directory for generated files (default: ./diagrams)"
    required: false
  - name: target
    description: "Target platform: markdown, confluence, google-doc (default: markdown)"
    required: false
---

# Diagram Orchestrator

Select the best diagramming tool and delegate generation to the appropriate skill. This skill is the entry point for all diagram creation — it analyzes the request, picks the right engine, and composes the output.

## Engine Selection Rules

### When to use Excalidraw

Prefer Excalidraw for diagrams that benefit from a **visual, spatial, hand-drawn aesthetic** or **freeform layout**:

| Use Case | Why Excalidraw |
|----------|----------------|
| **Architecture overview diagrams** | Spatial layout, color-coded components, hand-drawn feel makes them approachable |
| **System context diagrams** (top of a doc) | Overview diagrams at the top of documents look best with visual richness |
| **Infrastructure / cloud diagrams** | AWS/Azure/GCP layouts with grouped services, VPCs, subnets |
| **Freeform / whiteboard-style** | No rigid structure — boxes, arrows, annotations placed freely |
| **Hub-and-spoke diagrams** | Central orchestrator with radiating connections |
| **Deployment diagrams** | Servers, containers, networking topology |
| **User flow / journey maps** (visual) | When spatial layout matters more than strict sequence |
| **PR description overview** | A quick visual summary of what changed architecturally |
| **Project summary / codebase overview** | Analyzing a codebase and producing a visual architecture map |

### When to use Mermaid

Prefer Mermaid for diagrams that need **structured, precise, text-based** representations:

| Use Case | Why Mermaid |
|----------|-------------|
| **Sequence diagrams** | Mermaid's sequence syntax is excellent — lifelines, activation, alt/par blocks |
| **Flowcharts / decision trees** | Structured flow with clear branching and subgraphs |
| **Class diagrams / data models** | UML-style with inheritance, composition, interfaces |
| **State machines** | State transitions with guards and composite states |
| **ER diagrams** | Database schema with cardinality notation |
| **Gantt charts** | Project timelines with dependencies |
| **Git branching strategies** | gitGraph for branch/merge visualization |
| **C4 model diagrams** | Context, Container, Component, Deployment views |
| **Mindmaps** | Hierarchical topic exploration |
| **Timelines** | Historical / sequential events |
| **Kanban boards** | Task status tracking |
| **Packet / protocol diagrams** | Network packet structure with bit fields |
| **Sankey / flow diagrams** | Energy/data flow with proportional widths |
| **XY charts** | Bar and line charts |
| **Quadrant charts** | 2x2 comparison matrices |
| **Low-level design (LLD)** | Detailed component interactions, API contracts |
| **Inline in markdown** | Mermaid renders natively in GitHub, GitLab, Confluence, etc. |

### Auto-Detection Logic

When `engine=auto` (default), apply these rules in order:

1. If `engine` is explicitly set to `mermaid` or `excalidraw` → use that.
2. If `type=freeform` → **Excalidraw**.
3. If `type=architecture` and description mentions "overview", "high-level", "system context", or "infrastructure" → **Excalidraw**.
4. If `type` is one of: `sequence`, `class`, `state`, `er`, `gantt`, `gitgraph`, `mindmap`, `timeline`, `kanban`, `quadrant`, `sankey`, `xy`, `packet`, `radar`, `journey`, `requirement`, `c4` → **Mermaid** (these types have dedicated Mermaid syntax).
5. If description mentions "codebase", "project structure", "repo overview", "architecture diagram" → **Excalidraw**.
6. If description mentions "PR overview", "what changed", "system overview" → **Excalidraw**.
7. If description mentions "detailed", "low-level", "LLD", "API contract", "data flow steps" → **Mermaid**.
8. If description mentions "flowchart", "process", "workflow", "pipeline", "decision tree" → **Mermaid**.
9. Default → **Mermaid** (more universally renderable).

### Type Auto-Detection

When `type` is not specified, detect from the description:

| Keywords in Description | Detected Type |
|------------------------|---------------|
| process, workflow, decision, pipeline, steps, branching, if/then | `flowchart` |
| interactions, request/response, API calls, message passing, temporal | `sequence` |
| object, inheritance, data model, interface, type hierarchy, class | `class` |
| state machine, lifecycle, status transition, "when X happens" | `state` |
| database schema, tables, relationships, foreign keys, entities | `er` |
| architecture, system, infrastructure, services, deployment, overview | `architecture` |
| freeform, whiteboard, hand-drawn, spatial layout | `freeform` |
| timeline, history, chronological, milestones | `timeline` |
| mindmap, brainstorm, concept map, topic exploration | `mindmap` |
| project plan, schedule, dependencies, deadlines | `gantt` |
| branching strategy, merge, git flow, release process | `gitgraph` |
| context, container, component, C4 | `c4` |
| kanban, board, task status, todo/doing/done | `kanban` |
| comparison matrix, quadrant, priority/effort | `quadrant` |
| flow distribution, energy flow, proportional | `sankey` |
| chart, bar, line, data visualization | `xy` |
| packet, protocol, bit field, header structure | `packet` |

## Workflow

### Step 1: Analyze Request

Parse the description, type, and engine arguments. Apply auto-detection rules above.

### Step 2: Delegate to Engine Skill

Based on the selected engine, invoke the appropriate skill:

- **Mermaid**: Use the `/mermaid` skill with the resolved type, description, format, and output-dir.
- **Excalidraw**: Use the `/excalidraw` skill with the description, format, and output-dir.

Pass through all relevant arguments.

### Step 3: Handle Output Format

The engine skill produces source files and SVG by default.

- **`format=svg`** (default for markdown): The engine skill handles this directly. SVG is embedded inline in markdown.
- **`format=jpeg`**: After the engine skill produces SVG, invoke the `/image-transform` skill to convert SVG→JPEG.
- **`format=both`**: Produce both SVG and JPEG.

### Step 4: Target Platform Adjustments

- **`target=markdown`** (default): Embed SVG inline or as `![alt](path.svg)`. Include a `<details>` block with the source.
- **`target=confluence`**: Always produce JPEG (Confluence renders JPEG attachments reliably). Upload via the confluence-publish workflow.
- **`target=google-doc`**: Produce JPEG for embedding via Google Docs image insertion.

When `target=confluence` or `target=google-doc`, automatically set `format=jpeg` regardless of what was specified.

### Step 5: Report Output

Print the generated files:

```
Diagram generated:
  Engine: mermaid
  Source: ./diagrams/auth-flow.mermaid
  SVG:    ./diagrams/auth-flow.svg
  JPEG:   ./diagrams/auth-flow.jpg (for Confluence)

Embed in markdown:
  ![Auth Flow](./diagrams/auth-flow.svg)
```

## Composability

This skill is designed to be called from other skills:

- **`/doc-write`**: Calls `/diagram` for each diagram identified in the document outline.
- **`/pr-review`**: Can call `/diagram` to generate a visual summary of architectural changes.
- **`/research`**: Can call `/diagram` to visualize findings.
- **`/confluence-publish`**: Calls `/image-transform` to convert diagram SVGs to JPEG before upload.
- **Standalone**: Invoked directly by the user with `/diagram`.

When called from another skill, respect the caller's `target` and `format` preferences.

## Prerequisites

The following tools must be available globally:

| Tool | Install Command | Used By |
|------|----------------|---------|
| `mmdc` | `npm install -g @mermaid-js/mermaid-cli` | Mermaid SVG rendering |
| `excalidraw-to-svg` | `npm install -g excalidraw-to-svg` | Excalidraw SVG rendering |
| `sharp` | Available via `npx` or project-local install | SVG→JPEG conversion |

If a tool is missing, warn the user and provide the install command. Still save the source file so it can be rendered later.
