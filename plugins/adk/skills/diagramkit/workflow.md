# diagramkit — workflow

Six phases. Writes local files and runs the local diagramkit CLI; never commits, pushes, or publishes. The phased process is the contract; the **Workflow tool** drives Phase 2 for the repo-wide audit (one agent per engine or content area).

## Phase 0 — verify + materialize

- **Doctor.** Run `npx diagramkit doctor` to confirm diagramkit is installed in this repo and Chromium is warm (rendering needs a headless browser). A failing doctor **stops the skill** — report the gap (`rules.md`); don't render into a broken toolchain.
- **Materialize the engine skills.** Run `npx diagramkit skills install` so `node_modules/diagramkit/skills/*` stubs are on disk in this repo. If that subcommand isn't in the installed version, fall back to following `node_modules/diagramkit/skills/diagramkit-setup/SKILL.md`, and say you used the fallback.
- Always anchor on the **local** install (`npx diagramkit …`), never a global one.

## Phase 1 — route + shape

- Classify the input per `dispatch.md` into one route: **new-diagram**, **render**, **embed**, or **audit**.
- **new-diagram**: unless `--engine` was given, select the engine by reading `node_modules/diagramkit/skills/diagramkit-auto/SKILL.md` and applying its selection logic — do not guess. State the engine chosen and why.
- **render**: resolve the source(s) to re-render (a path, a glob, or "all changed sources").
- **embed**: resolve the target content file and the rendered diagram to place in it.
- **audit**: determine scope (repo root, or a `--scope-dir <dir>` subtree) and enumerate every diagram source by engine.
- In `-i` mode, confirm the route, the engine choice, and the scope before proceeding.

## Phase 2 — author / audit (the Workflow for a repo-wide audit)

**new-diagram / render / embed** — delegate to the one relevant installed skill and do the work inline:

- Author or edit the source by following `node_modules/diagramkit/skills/diagramkit-<engine>/SKILL.md`. That skill owns the palette, the readability budget, and the layout conventions — follow it exactly; never restate it here.
- Say you skipped the Workflow (a single diagram or one re-render doesn't need a fan-out).

**audit** — drive a **Workflow**:

1. **Fan out one agent per engine (or per content area).** Each agent gets its slice of the repo (the sources for its engine, or the content under a directory) plus one instruction: run `diagramkit validate` over the slice, and for every issue apply the fix by following `node_modules/diagramkit/skills/diagramkit-review/SKILL.md` and the relevant `diagramkit-<engine>/SKILL.md` — contrast/WCAG corrections, embed-safety fixes, and re-rendering any stale SVG whose source changed. Agents run in parallel over disjoint slices.
2. **Consolidate** each agent's fixes and the list of anything it could not repair.
3. **Re-validate** the whole repo (Phase 3) as the gate — the audit isn't done until a repo-wide `diagramkit validate` is green or every remaining failure is reported with a reason.

## Phase 3 — render + validate

- **Render.** `npx diagramkit render` the changed source(s) so the light/dark SVGs match the source. Never hand-edit rendered output; change the source and re-render.
- **Validate.** `npx diagramkit validate` over the changed surface (or the whole repo for an audit). Add `--fail-on <severity>` to set the failure threshold and `--scope-dir <dir>` to narrow the scan **if the installed version supports those flags**; if it doesn't, fall back to a plain `diagramkit validate` scoped to that subtree and say so.
- A failing gate **stops the phase** — fix the cause (via the engine skill) and re-run; never suppress or skip the check.

## Phase 4 — embed

- Only for the **embed** route (or when a new diagram is destined for a content file). Produce the light/dark `<picture>` markup **per the installed skill's guidance** (`diagramkit-<engine>` / `diagramkit-review` document the exact pattern) and place it at the target location.
- **Broader page authoring** — writing the surrounding content, frontmatter, or site config — is out of scope here; route it to `/adk:pagesmith`. This skill produces the diagram and the embed snippet, not the page.
- Only embed a diagram that passed Phase 3.

## Phase 5 — report

- Risk-first summary: any diagram that failed validation or couldn't be repaired first, then what got done — sources touched, renders produced, embeds placed, contrast/WCAG issues fixed (with `path`).
- Suggest next steps: a review (`/adk:review .`), a PR (open it yourself with `git` + the `gh` CLI — gated), or `/adk:pagesmith` for the surrounding content.
- **Nothing is committed or published.** Report the local file paths and stop.

## Narrate

State the doctor result and whether skills materialized (CLI or fallback), the route classified, the engine chosen and where its rules came from, the audit fan-out ("auditing 3 engines in parallel"), every render and validate result (and any flag you fell back on), and any diagram you couldn't repair. Never go silent for more than a phase.
