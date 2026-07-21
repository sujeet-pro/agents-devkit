# diagramkit — route dispatch

Route by the shape of the input → the sub-flow → how it's resolved. Every route runs against the **local** diagramkit install and delegates version-sensitive authoring to `node_modules/diagramkit/skills/*` (never restated here). All four routes assume Phase 0 (`diagramkit doctor` + `skills install`) already passed.

| Input shape | Route | How to resolve |
|---|---|---|
| A repo-wide intent — "audit the diagrams", "fix all contrast / WCAG warnings", "diagram health check" — or `--audit`, optionally with `--scope-dir <dir>` | audit | Enumerate every diagram source by engine, then fan out per engine/content area via the Workflow tool, following `node_modules/diagramkit/skills/diagramkit-review/SKILL.md`. Ends on a repo-wide `diagramkit validate` gate. |
| A content file target (`.md` / `.mdx`) plus a diagram to place in it, or `--embed <content-path>` | embed | Render + validate the diagram, then produce the light/dark `<picture>` markup **per the installed skill's guidance** and place it at the target. Broader page/config work → `/adk:pagesmith`. |
| An existing diagram source path or glob (`*.mmd`, `*.excalidraw`, `*.drawio`, `*.dot` / `*.gv`), or "re-render X" | render | `diagramkit render` the source(s), then `diagramkit validate`. No new authoring — the source already exists. |
| Freeform intent to make a diagram ("draw / create a diagram of X"), no source yet | new-diagram | Select the engine via `node_modules/diagramkit/skills/diagramkit-auto/SKILL.md` (or `--engine`), author by following `node_modules/diagramkit/skills/diagramkit-<engine>/SKILL.md`, then render + validate. |

Routing is by data, not vibes. If several match, the strongest discriminator wins: **audit (repo-wide intent) > embed (content target) > render (existing source) > new-diagram (default).**

## What this skill owns vs. delegates

- **diagramkit owns** the lifecycle: verifying the toolchain, routing, driving `render` / `validate`, the audit fan-out, and producing the embed snippet.
- **The installed engine skills own** the authoring: `diagramkit-auto` (engine selection), `diagramkit-<engine>` (palette, readability budget, layout, embed markup), `diagramkit-review` (the audit/fix flow). Read and follow them — never restate their content, which is version-matched to the installed package.
- **`/adk:pagesmith` owns** the surrounding content and site: writing the page prose/frontmatter, configuring, and deploying a Pagesmith site. This skill produces the diagram and the embed markup, not the page.

## When the classifier is wrong

If the picked route doesn't fit — an "audit" that's really one diagram, an embed target that isn't a content file, a "render" whose source doesn't exist yet (so it's actually new-diagram) — say so in Phase 1 ("this reads like a single new diagram, not a re-render; confirm or correct?") and proceed on the corrected route. Don't silently force a bad fit, and don't render a source that doesn't exist.
