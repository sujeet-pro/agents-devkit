# `docs-diagram` — workflow detail

## Phase 0 — prompt expansion

1. Classify the diagram type from the prompt:
   - Explicit arg wins (`sequence`, `er`, `c4`, etc.).
   - Keyword hints:
     - "flow / decision / branching" → `flowchart`.
     - "sequence / call / interaction / request-response" → `sequence`.
     - "state / lifecycle / status transitions" → `state`.
     - "class / UML / inheritance" → `class`.
     - "ER / schema / table / relation" → `er`.
     - "gantt / timeline with durations" → `gantt`.
     - "git branching model" → `gitgraph`.
     - "mind map / brainstorm" → `mindmap`.
     - "timeline of events" → `timeline`.
     - "architecture / system / containers" → `c4`.
2. Resolve repo via `repos.md`; optional `--scope` path.
3. Pick slug: `diagram-<type>-<kebab-subject>`. Create
   `.temp/task-<slug>/`.

## Phase 1 — preflight

1. `bin/adk-info --check`.
2. If `--scope` path given, verify it exists.
3. Check diagramkit availability:
   ```
   npx --no-install @adk/diagramkit --version
   ```
   If it fails, skip rendering; still produce `.mermaid`.
4. Load `~/.config/adk/docs.md.mermaid_render_mode` (default
   `light_and_dark`).

## Phase 2 — gather evidence (only if `--scope` given)

1. Read files in the scope:
   - `.kt`, `.java`, `.ts`, `.tsx`, `.py`, `.go` for code structure.
   - `.sql`, `schema.yaml`, `*.prisma` for schema.
   - `openapi.yaml`, `*.proto` for interface definitions.
   - `docker-compose.yml`, `k8s/**/*.yaml` for infra.
2. Build node + edge list in `elements.md`:
   - Nodes: service / class / table / state / actor / task.
   - Edges: call / references / implements / extends / inherits.
3. Apply `references/node-budget.md`:
   - If > 15 nodes: propose a split. Surface choices:
     - Overview + zoom-in.
     - Lifecycle phase split.
     - Actor-view split.
   - Under `--auto`, default to overview + zoom-in (2 diagrams).
   - Under `-i`, ask.

## Phase 3 — draft

1. Open `.temp/task-<slug>/<subject>.mermaid`.
2. Add the title comment:
   ```
   %% <subject> — drawn by adk-docs:docs-diagram on YYYY-MM-DD %%
   ```
3. Pick idiomatic syntax from
   `references/mermaid-types-catalog.md`.
4. Emit nodes / edges grounded in `elements.md` (or the prompt's
   description if no scope).
5. For a pair / split, write multiple `.mermaid` files:
   - `<subject>.overview.mermaid`.
   - `<subject>.<zoom-name>.mermaid`.

## Phase 4 — validate + render

1. Validate Mermaid syntax (parse).
2. If diagramkit is available:
   - Run `npx @adk/diagramkit render --input <subject>.mermaid --output <subject>.svg --mode light_and_dark`.
   - Produces `<subject>.light.svg` and `<subject>.dark.svg`.
3. If diagramkit is missing:
   - Write the `.mermaid` file only.
   - Note in the report that rendering was skipped + the exact
     install one-liner (`npm i -g @adk/diagramkit`).

## Phase 5 — report

1. Write `.temp/task-<slug>/report.md`.
2. Include the path to each `.mermaid` file + SVG pair.
3. Include the node count and an "embed me" snippet:
   ```
   ```mermaid
   <content>
   ```
   ```
4. Surface any split decisions made under `--auto`.
