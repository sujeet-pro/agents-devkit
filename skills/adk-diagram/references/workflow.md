# ADK Diagram Workflow

## Phases

### Phase 1: Understand
Clarify what needs to be visualized, the audience, target document, and preferred format.

**Inputs:** user diagram request, `--doc`, `--name`, `--engine`, `--type` flags
**Actions:**
- Parse the diagram request and identify what should be explained
- Identify the target markdown document
- Determine audience and complexity level
- Check for existing diagrams in the target document
- Present confirmation summary to user

**Gate:** User confirms scope, engine preference, and target document. Skip when `--auto` is set.

**Outputs:** confirmed diagram purpose, target doc, audience

### Phase 2: Choose Engine
Select the appropriate diagram engine based on diagram type and project conventions.

**Quick decision matrix** (see `references/engines-and-types.md` for full detail):

| Signal | Engine | Guide |
| --- | --- | --- |
| flow, sequence, ER, class, state, timeline, gantt, C4, mindmap, pie, sankey, journey | **Mermaid** | `mermaid.md` |
| freeform architecture, system context, hand-drawn overview, codebase map | **Excalidraw** | `excalidraw.md` |
| network topology, cloud infra, BPMN, org chart, swimlanes, multi-page | **Draw.io** | `drawio.md` |
| dependency graph, call graph, strict hierarchy, rank constraints, existing `.dot`/`.gv` | **Graphviz** | `graphviz.md` |

**Actions:**
- Match the diagram request against the decision matrix above
- Check project conventions for existing diagram engine preferences
- If `--engine` is provided, validate it fits the diagram type
- Load exactly one engine guide from `references/` for the selected backend
- If Mermaid is selected, route to the matching type section in `mermaid.md`

**Outputs:** selected engine and type with rationale

### Phase 3: Draft
Create the diagram source in the chosen format and present for review.

**Actions:**
- Read the current markdown and source material the diagram summarizes
- Write the editable source file using the engine-specific extension (`.mermaid`, `.excalidraw`, `.drawio`, `.dot`)
- Validate source syntax for the chosen engine
- Present the diagram source for user review

**Gate:** User approves source. Skip when `--auto` is set.

**Outputs:** diagram source file

### Phase 4: Render
Generate visual output via diagramkit and validate rendering.

**Actions:**
- Render using `npx diagramkit render <source-file>` (prefer project-local install)
- Prefer SVG output for markdown docs
- If the project has a `diagramkit.config.json5`, honor its settings
- When diagramkit generates light and dark variants, prefer a `<picture>` block
- Validate rendering succeeded (output file exists and is non-empty)
- If rendering fails, report the error and leave source file in place for retry

**Outputs:** rendered diagram asset (SVG preferred)

### Phase 5: Iterate
Refine the diagram based on user feedback.

**Actions:**
- Present the rendered output for user review
- Accept feedback: revise source, re-render, or switch engine
- Repeat until user approves

**Gate:** User approves the rendered output.

**Outputs:** approved diagram

### Phase 6: Deliver
Place the diagram in docs with editable source alongside rendered output.

**Actions:**
- Update the markdown document with the diagram embed (relative SVG or `<picture>` block)
- Place source file in the `diagrams/` folder sibling to the markdown file
- Verify source file, rendered output, and markdown reference all align
- Report final file paths and markdown line reference

**Outputs:** updated markdown, source file, rendered asset

## File Placement
- If `--doc` is provided, use a `diagrams/` folder sibling to that markdown file
- If `--doc` is omitted, use `diagrams/` at the project root
- Source files stay in the diagram area
- Rendered files go into a sibling `.diagramkit/` folder unless project config says otherwise

## Rendering Rules
- Prefer SVG for markdown documents
- Keep editable source committed alongside rendered asset
- When diagramkit generates light and dark variants, prefer `<picture>` for theme awareness
- If the doc style does not support `<picture>`, link the light SVG by default

## Validation Rules
- The markdown points at an existing rendered SVG
- The editable source file exists beside or near the rendered asset
- The markdown embed is correctly placed and readable
- If rendering failed, report the command used and leave source file in place
- Source syntax is valid for the chosen engine

## Auto Mode Behavior
When `--auto` is set:
- Phase 1 (Understand): skip user confirmation, proceed with parsed intent
- Phase 3 (Draft): skip source review, proceed to render
- Phase 5 (Iterate): skip (no interactive feedback)
- Phase 6 (Deliver): still verifies all references align
- Validation rules still apply in full
