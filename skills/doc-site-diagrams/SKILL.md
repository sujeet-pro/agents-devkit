---
name: doc-site-diagrams
description: |
  Wrap `diagramkit` (mermaid / graphviz / drawio / excalidraw rendering with light+dark mode pairs) for use inside a pagesmith docs site. Installs `diagramkit` as a dev-dep, wires the build to render `.mermaid` / `.dot` / `.gv` / `.excalidraw` / `.drawio` files into SVG/PNG next to their source, and delegates ongoing diagram authoring to `diagramkit-mermaid`, `diagramkit-graphviz`, `diagramkit-draw-io`, `diagramkit-excalidraw`, and `diagramkit-auto`. Use after `@adk:doc-site-setup` (a.k.a. `adk-doc-site-setup`) when the user wants diagrams in their docs. Do not use to build standalone diagrams (use `@adk:visualize-diagram` (a.k.a. `adk-visualize-diagram`)).
metadata:
  category: docs
  kind: task
  layer: 6
  modes: [auto]
---

# doc-site-diagrams — wrap diagramkit for pagesmith docs

Thin wrapper. Installs `diagramkit` and delegates to its skill pack.

## When to use

- A pagesmith docs site exists (`pagesmith.config.json5` present).
- The user wants embedded diagrams in their docs.

## When NOT to use

- One-off standalone diagram → `@adk:visualize-diagram`.
- Docs site does not exist yet → run `@adk:doc-site-setup` first.

## Workflow

1. Phase 1 validator. `pagesmith.config.json5` exists; Node 24+.
2. `npm add -D diagramkit`.
3. Read `node_modules/diagramkit/REFERENCE.md` (or its README.md if no REFERENCE.md) for version-matched truth.
4. Add `npm run docs:diagrams` script: `npx diagramkit build`.
5. Update `npm run docs:build` to depend on `docs:diagrams`.
6. Configure pagesmith to recognize rendered SVGs (default: `docs/.../<name>.svg` next to `<name>.mermaid`).
7. Demo: create a sample `docs/architecture/diagrams/overview.mermaid` and render it; confirm the SVG appears.
8. Install diagramkit skill pack into consumer's `.claude/skills/` (per its installer).
9. Phase 4 validator. Report.

## Output

- `diagramkit` added to `package.json` devDependencies
- `npm run docs:diagrams` script wired
- Sample diagram + rendered SVG (if user opted in)
- `.claude/skills/diagramkit-*` skills installed in consumer

## Mode

`auto` only.

## Anti-patterns

- Globally installing `diagramkit`. Always devDep + npx.
- Hand-running per-format renderers. Use `npx diagramkit build` (auto-detects formats).
- Skipping read of `node_modules/diagramkit/REFERENCE.md`.

## Delegation

| Want to | Use |
| --- | --- |
| Draft a mermaid diagram | `diagramkit-mermaid` |
| Draft a graphviz dot diagram | `diagramkit-graphviz` |
| Draft a drawio diagram | `diagramkit-draw-io` |
| Draft an excalidraw diagram | `diagramkit-excalidraw` |
| Let diagramkit choose by extension | `diagramkit-auto` |
| Review diagrams in a repo | `diagramkit-review` |
| First-time diagramkit setup outside pagesmith | `diagramkit-setup` |

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Wire-up flow |
| `references/modes.md` | auto only |
| `references/persona.md` | The diagram-pipeline bootstrapper |
| `references/workflow.md` | Detailed steps |
| `references/clarifying-questions.md` | Sample diagram opt-in |
| `references/output-format.md` | Final report |
| `references/artifact-format.md` | Files created in consumer repo |
| `references/validator.md` | Build/render smoke test |
| `references/anti-patterns.md` | What NOT to do |
| `references/diagramkit-skill-pack.md` | List of diagramkit skills with usage |
| `references/examples.md` | Sample setup output |
| `references/interaction-contract.md` | Synced from canonical |
