# adk-diagram

Create or update markdown docs with editable diagram source files across Mermaid, Excalidraw, Draw.io, and Graphviz, rendered via diagramkit.

## Quick Start

```bash
npx adk-diagram "add a system architecture diagram" --doc README.md --engine mermaid
```

## What This Skill Does

Creates or refreshes diagrams inside markdown documentation. Merges the diagram skill family into one entrypoint: choose the right engine, write the editable source file, render through `diagramkit`, and update the markdown to point at the rendered asset. Supports Mermaid, Excalidraw, Draw.io, and Graphviz from a single skill.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<diagram-request>` | free text | required | What the diagram should explain |
| `--doc` | markdown path | none | Markdown file to create or update |
| `--name` | kebab-case slug | inferred | Diagram file base name |
| `--engine` | `mermaid`, `excalidraw`, `drawio`, `graphviz` | inferred | Force a specific diagram engine |
| `--type` | engine-specific type | inferred | Diagram type or hint for engine selection |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | command | yes |
| `node` | command | yes |
| `npx` | command | yes |
| `python3` | command | yes |
| `diagramkit` | npm package | yes |

## Skill Layout

```
adk-diagram/
  SKILL.md
  README.md
  scripts/
    preflight.py
  references/
    README.md
    workflow.md
    persona.md
    engines-and-types.md
    mermaid.md
    excalidraw.md
    drawio.md
    graphviz.md
    diagramkit-integration.md
    markdown-integration.md
    _shared/
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
```

## Workflow

1. Confirm the doc target, audience, engine, diagram type, and file name.
2. Inspect the relevant markdown, code, and nearby docs before drafting.
3. Select the right engine and source extension using engine-and-types reference.
4. Write the editable source file in the correct `diagrams/` folder.
5. Render through `diagramkit`, preferring project-local `npx diagramkit` when available.
6. Update the markdown to add or replace the diagram embed.
7. Verify the source file, rendered output, and markdown link all line up.

## Interaction Protocol

Unless `--auto` is set, the skill follows an interactive workflow:

1. **Intent confirmation** -- confirms the diagram purpose, target markdown document, engine, and diagram type.
2. **Draft review** -- presents the diagram source for review before rendering.
3. **Render result** -- after rendering, reports the output path and confirms the markdown embed was updated.
4. **User response** -- `ok` to approve and render, feedback text to revise, `engine X` to switch engine, `done` to finalize.

## Output Format

Each run produces:
- Doc target path
- Diagram source file path
- Engine and type used
- Rendered SVG path
- Markdown update confirmation
- Validation results

## Examples

### Add an architecture diagram to a README
```bash
npx adk-diagram "add a system architecture diagram" --doc README.md --engine mermaid
```
Confirms the scope, drafts a Mermaid flowchart, renders to SVG, updates the README embed.

### Update an existing flow diagram
```bash
npx adk-diagram "update the auth flow to include the new OAuth provider" --doc docs/auth.md --name auth-flow
```
Reads the existing diagram source, proposes changes, re-renders, and updates the markdown.

### Create an ER diagram with Graphviz
```bash
npx adk-diagram "create an ER diagram for the billing schema" --doc docs/billing.md --engine graphviz --type er --auto
```
Skips confirmations, inspects the billing models, generates a Graphviz DOT source, renders to SVG.

## What Success Looks Like

- [ ] The markdown points at an existing rendered `.svg`
- [ ] The editable source file exists beside or near the rendered asset
- [ ] The markdown embed is correctly placed and readable
- [ ] The engine and type match the diagram's purpose
- [ ] If rendering could not run, the doc and source are in a recoverable state
- [ ] The skill reports source, rendered output, and validation results
