# diagramkit skill pack — what each skill does

After `diagramkit` is installed and its skill pack copied into the consumer:

| Skill | Purpose |
| --- | --- |
| `diagramkit-setup` | First-time diagramkit setup (covered here for pagesmith docs case) |
| `diagramkit-auto` | Route by file extension; preferred for "render this folder" |
| `diagramkit-mermaid` | Draft a `.mermaid` diagram + render |
| `diagramkit-graphviz` | Draft a `.dot` / `.gv` diagram + render |
| `diagramkit-draw-io` | Draft a `.drawio` diagram + render |
| `diagramkit-excalidraw` | Draft a `.excalidraw` diagram + render |
| `diagramkit-review` | Review existing diagrams in a repo for correctness/clarity |

For embedded usage in pagesmith docs:
- Place source next to consuming markdown: `docs/<section>/diagrams/<name>.mermaid`
- Run `npm run docs:diagrams` (or `npm run docs:build` which depends on it)
- Reference rendered output: `![Architecture overview](./diagrams/overview.svg)`
