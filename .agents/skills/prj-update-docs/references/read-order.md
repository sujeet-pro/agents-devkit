# Read order — prj-update-docs

Read these files in this order on every run. They are version-pinned to the installed
packages, so they always match the CLI you will actually invoke. Do **not** rely on training
data or globally installed binaries.

## 1. Project constitution

| File                                                | Why                                                               |
| --------------------------------------------------- | ----------------------------------------------------------------- |
| `../../../AGENTS.md`                                | Repo-wide contract (directory map, skill shape, working-artifact rules). |
| `../../../CLAUDE.md`                                | Claude-specific delta (`/adk:*` invocation, plugin layout).       |
| `../../../GEMINI.md`                                | Gemini delta — same plugin, different invocation.                 |
| `../../../bin/canonical/interaction-contract.md`    | Default-ask / explained-options / `--auto` contract.              |
| `../../../pagesmith.config.json5`                   | Site config — `contentDir`, `basePath`, `outDir`, edit links.     |
| `../../../docs/meta.json5`                          | Top-level docs structure + nav order.                             |

## 2. Pagesmith (docs structure + markdown features)

| File                                                                             | Why                                                                       |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `node_modules/@pagesmith/docs/REFERENCE.md`                                      | Canonical config + frontmatter + layout + build CLI.                      |
| `node_modules/@pagesmith/docs/ai-guidelines/docs-guidelines.md`                  | AI-first authoring rules + diagram guidance.                              |
| `node_modules/@pagesmith/docs/ai-guidelines/markdown-guidelines.md`              | Every supported markdown feature (GFM, alerts, math, code-block meta).    |
| `node_modules/@pagesmith/docs/ai-guidelines/setup-docs.md`                       | When `docs/` shape itself needs retrofitting.                             |
| `node_modules/@pagesmith/docs/ai-guidelines/migration.md`                        | When upgrading the installed `@pagesmith/docs` package.                   |
| `node_modules/@pagesmith/docs/ai-guidelines/recipes.md`                          | Common doc-task playbooks.                                                |
| `node_modules/@pagesmith/docs/ai-guidelines/errors.md`                           | Build/validate error catalog with fixes.                                  |
| `node_modules/@pagesmith/docs/schemas/pagesmith-config.schema.json`              | JSON schema for `pagesmith.config.json5`.                                 |
| `node_modules/@pagesmith/docs/schemas/docs-section-meta.schema.json`             | JSON schema for `meta.json5` per section.                                 |
| `node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json`         | JSON schema for page frontmatter.                                         |
| `node_modules/@pagesmith/docs/schemas/docs-home-frontmatter.schema.json`         | JSON schema for the home-page frontmatter.                                |

## 3. diagramkit (diagram authoring + render + validate)

| File                                                                     | Why                                                                       |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `node_modules/diagramkit/REFERENCE.md`                                   | Canonical CLI / API / schemas / supported extensions.                     |
| `node_modules/diagramkit/ai-guidelines/usage.md`                         | Agent setup prompts + CLI quick reference.                                |
| `node_modules/diagramkit/ai-guidelines/diagram-authoring.md`             | Per-engine authoring details (palettes, theming, embedding).              |
| `node_modules/diagramkit/llms.txt`                                       | Compact CLI reference.                                                    |
| `node_modules/diagramkit/llms-full.txt`                                  | Full CLI + API reference (`--agent-help`).                                |
| `node_modules/diagramkit/skills/diagramkit-setup/SKILL.md`               | First-time install / `warmup` / config / pointer install.                 |
| `node_modules/diagramkit/skills/diagramkit-auto/SKILL.md`                | Engine selection table + tie-break rules + iterative loop.                |
| `node_modules/diagramkit/skills/diagramkit-mermaid/SKILL.md`             | Authoring + Review Mode for `.mermaid`.                                   |
| `node_modules/diagramkit/skills/diagramkit-excalidraw/SKILL.md`          | Authoring + Review Mode for `.excalidraw`.                                |
| `node_modules/diagramkit/skills/diagramkit-draw-io/SKILL.md`             | Authoring + Review Mode for `.drawio*`.                                   |
| `node_modules/diagramkit/skills/diagramkit-graphviz/SKILL.md`            | Authoring + Review Mode for `.dot` / `.gv` / `.graphviz`.                 |
| `node_modules/diagramkit/skills/diagramkit-review/SKILL.md`              | Cross-engine audit + repair workflow used in phase 6.                     |
| `node_modules/diagramkit/schemas/diagramkit-config.v1.json`              | JSON schema for `diagramkit.config.json5`.                                |
| `node_modules/diagramkit/schemas/diagramkit-cli-render.v1.json`          | JSON schema for `diagramkit render --json` output (parsed by phase 6).    |

## 4. ADK skills this one delegates to (when present)

| Skill                                | Used in phase | Why                                                |
| ------------------------------------ | ------------- | -------------------------------------------------- |
| `../../../skills/docs-write/SKILL.md`        | 4 (per-page prose) | Author / refresh prose for an individual page.    |
| `../../../skills/docs-review/SKILL.md`       | 3 (drift detection) | Critique an existing doc against its source.    |
| `../../../skills/doc-site-setup/SKILL.md`    | 0 (only on retrofit) | Bootstrap pagesmith if it isn't installed.    |
| `../../../skills/doc-site-diagrams/SKILL.md` | 5 (diagram authoring) | If the project uses this wrapper.            |
| `../../../skills/visualize-diagram/SKILL.md` | 5 (one-off diagrams) | When a diagram isn't part of any doc page.    |

If a delegated skill is missing, fall back to the upstream pack directly (e.g. read
`node_modules/diagramkit/skills/diagramkit-auto/SKILL.md` for diagram authoring).

## 5. Existing docs tree (as a starting point)

| Path                            | Purpose                                                            |
| ------------------------------- | ------------------------------------------------------------------ |
| `../../../docs/README.md`        | Site home page (uses `DocHome` layout).                            |
| `../../../docs/concepts/`        | Conceptual explainers (`philosophy`, `skill-anatomy`, `agents`, `hooks`, `mcp`). |
| `../../../docs/guide/`           | Task-oriented guides grouped by category.                          |
| `../../../docs/reference/`       | One auto-generated page per skill + per agent. **This is the primary surface this skill maintains.** |
| `../../../docs/reference/meta.json5` | Sidebar order under `Reference`.                              |

## Stop conditions

Stop reading more upstream files once you have the answer for the phase you are in. Every
file above unblocks something specific — only read a file if its column 2 matches the work
you are about to do.
