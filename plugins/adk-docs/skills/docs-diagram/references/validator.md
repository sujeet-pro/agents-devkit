# `docs-diagram` — per-phase validator

Logged to `.temp/task-<slug>/validation/docs-diagram.md`.

## Phase 0

- [ ] `.temp/task-<slug>/` exists, gitignored.
- [ ] Prompt saved verbatim.
- [ ] Diagram type is one of the supported 10
      (`references/mermaid-types-catalog.md`).

## Phase 1

- [ ] `bin/adk-info --check` == 0.
- [ ] If `--scope` given: path exists.
- [ ] Diagramkit availability recorded (available | missing).

## Phase 2 (only if `--scope`)

- [ ] `elements.md` exists with ≥ 1 node and ≥ 1 edge.
- [ ] Every node has a `Source` citation.
- [ ] Every edge has a `Source` citation.
- [ ] Node count ≤ 15 OR a split decision is recorded in
      `validation/docs-diagram.md`.

## Phase 3

- [ ] `<subject>.mermaid` file exists.
- [ ] First line is the Mermaid title comment matching the regex:
      `^%% .+ — drawn by adk-docs:docs-diagram on \d{4}-\d{2}-\d{2} %%$`.
- [ ] Mermaid type declaration is on line 2 or 3 (after the comment
      and optional blank line).
- [ ] Node IDs are kebab-case; labels in quotes when they contain
      spaces.
- [ ] No node ID contains `.` / `/` / whitespace.

## Phase 4

- [ ] Mermaid syntax is valid (parses, no error).
- [ ] If diagramkit is available:
      - [ ] Render succeeded within 30s.
      - [ ] SVG pair produced (`<basename>.light.svg` and
            `<basename>.dark.svg`).
      - [ ] Neither SVG is zero bytes.

## Phase 5

- [ ] `report.md` exists.
- [ ] Report includes the embed snippet (fenced mermaid block).
- [ ] Report cites every produced file.

## Content guardrails

- [ ] Never ASCII art.
- [ ] Never > 15 nodes in a single `.mermaid` file.
- [ ] When `--scope` is used, never an edge without a citation.

## On any failure

- Log the failure + remediation.
- Block next phase.
- After 3 same-kind failures, stop and surface.
