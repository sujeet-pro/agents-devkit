# pagesmith — workflow

Six phases. The default flow stops at the Phase 2 → Phase 3 boundary and waits for a go-ahead before it writes. `--plan` stops after Phase 2; `--act` skips the confirm gate. The phased process is the contract; the **Workflow tool** drives the multi-surface fan-out in Phase 3.

## Phase 0 — detect the flavor + gather

- **Detect the flavor** from the config file at the repo root:
  - `pagesmith.config.json5` → **docs-preset** (a `@pagesmith/docs` site).
  - `site.config.json5` → **core-native** (a `@pagesmith/site` + `@pagesmith/core` site).
  - neither → **greenfield**: this skill maintains an *existing* site — stop and route to `/adk:scaffold-pagesmith-docs` (`rules.md`).
  - `--flavor docs|core` overrides detection.
- **Note the install.** From `package.json`, which `@pagesmith/*` packages and which `diagramkit` version are installed, and the repo's **own** build/validate scripts — you run those exact commands in Phase 4, never assumed ones.
- **Read enough of the existing site** (a couple of existing pages + the config) to match its conventions in Phase 3.

## Phase 1 — route + materialize the package skills

- Classify the task per `dispatch.md` → the sub-flow + the matching installed skill(s) (e.g. `pagesmith-docs-add-page`, `pagesmith-docs-configure-nav`, `pagesmith-core-add-collection`, `pagesmith-site-customize-theme`).
- **Materialize the package skills** in the consumer so the guidance is present and version-matched:
  ```bash
  npx pagesmith skills install      # @pagesmith/* skills (bin follows the install: pagesmith-docs / pagesmith-core)
  npx diagramkit skills install     # when the task also touches diagrams
  ```
  If the `skills install` subcommand isn't available yet, follow `node_modules/<pkg>/skills/<pkg>-setup/SKILL.md` as the fallback. Do not invent the missing skill's steps (`rules.md`).
- **Open the matched skill** — read and follow `node_modules/<pkg>/skills/<name>/SKILL.md`. It points at the version-matched `node_modules/<pkg>/REFERENCE.md` / schemas that are authoritative for this install. Do not restate schema, frontmatter, or flags from memory (`persona.md`).

## Phase 2 — plan + confirm

- State the plan the matched skill implies: pages to add/change, config keys to touch, whether a rebuild or deploy is needed, and the exact repo scripts you'll validate with.
- In `-i` mode, confirm flavor + route + outline (cap 3 questions). In default mode, state your assumptions so the user can correct.
- **Stop and confirm** before writing (unless `--act`). `--plan` stops here and touches nothing.

## Phase 3 — delegate + execute (the Workflow)

For a change spanning more than one page or surface (seeding a docs set, a combined nav + theme + search change, a `pagesmith-generate-docs` run), drive a **Workflow**:

1. Fan out one agent **per page / per surface**, each following the *same* matched `node_modules/<pkg>/skills/<name>/SKILL.md` — parallel where the units are independent (separate pages) and serialized only where one output feeds the next (nav depends on the pages existing).
2. Stitch the results into the site's structure, matching existing conventions.
3. Run a **completeness/consistency critic** pass against the matched skill's contract: every new page has valid frontmatter, the nav/sidebar resolves, no orphan pages, links aren't dead, search still indexes. Its findings become the next revision before the set survives.

```js
const UNITS = pagesToAuthor;             // one work item per page / surface
const drafts = await parallel(UNITS.map(u => () =>
  agent(`Follow node_modules/${pkg}/skills/${skill}/SKILL.md to author "${u.title}". ` +
        `Read REFERENCE.md/schemas for exact frontmatter + placement; do not guess.`,
        {agentType:'implementer', phase:'Author', schema:PAGE})));
const audit = await agent(
  `Check this set against the skill's contract: frontmatter valid, nav resolves, no orphans, links live.`,
  {input: drafts, phase:'Critique', schema:FINDINGS});
```

A single page or a single config key is done inline against the matched skill — say you skipped the Workflow. Content prose uses the reader-first voice (`persona.md`); a full standalone document is `/adk:document`; diagrams are `/adk:diagramkit`.

## Phase 4 — validate (the repo's own scripts)

- Run the repo's **own** commands from Phase 0 (read them out of `package.json`) — the build and the validate/check scripts. Never assume a script name; use what the repo defines.
- A failing gate **stops the phase** — fix the cause or report. Never hand-edit generated output (`dist/`, the search index) to make a check pass; regenerate it via the build.
- Self-coherence: what changed matches the plan; explain any deviation.

## Phase 5 — report + gated deploy

- Report the flavor, the route, the `node_modules` skill delegated to, the files changed (`path:line`), and every validator result (`persona.md` output shape).
- **Deploy is gated.** `--deploy` (or an explicit ask) runs the repo's own gh-pages path — its GitHub Actions workflow or deploy script — and any `git push` / `gh pr create` is **confirmed first**, never force-pushed, never to a protected branch (`rules.md`). Otherwise recommend the exact command and stop.

## Narrate

State the flavor detected (and the config file it came from), the route + the matched `node_modules` skill, the materialize step (or its fallback), the Workflow fan-out for multi-surface work, and every validator result. Confirm before any deploy or push. Never go silent for more than a phase.
