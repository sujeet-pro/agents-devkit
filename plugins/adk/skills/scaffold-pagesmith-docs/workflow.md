# scaffold-pagesmith-docs — workflow

Five phases, greenfield and write-heavy. Phases 0–1 touch nothing (gather + advise). Phase 2 does the scaffold and is where the **Workflow tool** fans out. Phase 3 validates. Phase 4 reports. The finish line is a running preview — never a deploy. `--dry-run` stops after Phase 1 with the full plan.

## Phase 0 — gather

Collect the five inputs, defaulting sensibly and **stating each default** so the user can correct it:

- **target dir** (positional; default cwd), **project name**, **base path** (default `/` for local preview; a subpath if it deploys under one), **deploy target** (`gh-pages` or `none`), and the **primary diagram engine(s)** (`--engine`, repeatable).
- **Detect the target's state before anything else:**
  - Is it a git repo? If not, note it — a scaffold that will deploy to GitHub Pages needs one.
  - Is there a `package.json`? If not, the setup step initializes one.
  - **Does a `pagesmith.config.*` already exist, or is the docs tree non-empty?** This is the hard gate — **stop and confirm** before writing (`rules.md`). This skill is greenfield; an existing site belongs to `/adk:pagesmith`.
- In `-i`, confirm every choice here before moving on.

## Phase 1 — advise

- Present the two site flavors and recommend one:
  - **docs preset (`@pagesmith/docs`)** — the default for a documentation site. Batteries-included: nav, search, layouts.
  - **core-native (`@pagesmith/core` + `@pagesmith/site`)** — when the user wants a custom site around the content pipeline, not the docs preset.
- State the recommendation and the one-line reason; in `-i`, confirm. `--preset` forces the choice and skips the advice.
- **`--dry-run` stops here:** print the plan — packages to install, the target tree, the commands, and the sample content to be seeded — and touch nothing.

## Phase 2 — scaffold (the Workflow tool fans out where independent)

The sequential spine runs in order; only the content authoring parallelizes.

1. **Install the packages.** `npm install @pagesmith/docs diagramkit` (for `core-native`, install `@pagesmith/core @pagesmith/site diagramkit` instead). Git operations are `git` directly; any clone is SSH-only (`../../SAFETY.md`).
2. **Apply the package's own setup — do not hand-author config.** Read and follow the installed setup skill for the config file **and** the deploy workflow, passing through the Phase 0 base path + deploy target. It owns the schema; this skill never restates it:

   ```text
   node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/SKILL.md
   ```

   The deploy-target specifics (base-path arithmetic, 404 fallback, the Actions workflow) live in the installed deploy skill when present:

   ```text
   node_modules/@pagesmith/docs/skills/pagesmith-docs-deploy-gh-pages/SKILL.md
   ```

3. **Materialize the package skills into the repo.** The canonical mechanism is the `skills install` CLI — idempotent, and what CI's `--check` gate expects:

   ```bash
   npx pagesmith skills install && npx diagramkit skills install
   ```

   If the `skills install` subcommand is unavailable (an older package that predates it), fall back to following each package's setup skill, which materializes the stubs by hand:

   ```text
   node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/SKILL.md   # pagesmith stub materialization
   node_modules/diagramkit/skills/diagramkit-setup/SKILL.md            # diagramkit stub materialization
   ```

4. **Seed sample content — fan out via the Workflow tool.** These artifacts are independent, so author them in parallel: one **guide** page, one **reference** page, and **one diagram per requested engine**. Each diagram author reads and follows the installed engine-selection skill — never a palette or engine name restated here:

   ```text
   node_modules/diagramkit/skills/diagramkit-auto/SKILL.md
   ```

   Sketch (each author delegates to the installed skill; a verify pass confirms the artifact before it survives):

   ```js
   const ARTIFACTS = [
     { kind: 'guide',     spec: 'a Getting Started guide page' },
     { kind: 'reference', spec: 'a reference page for one config surface' },
     ...engines.map(e => ({ kind: 'diagram', engine: e,
        spec: `one sample diagram via node_modules/diagramkit/skills/diagramkit-auto/SKILL.md` })),
   ];
   const seeded = await pipeline(
     ARTIFACTS,
     a => agent(`Author the ${a.kind} (${a.spec}); follow the installed package skill exactly.`,
                { agentType: 'implementer', phase: 'Seed' }),
     out => agent(`Verify this artifact renders/builds in the scaffolded site — default to failed if unsure: ${JSON.stringify(out)}`,
                { phase: 'Verify', schema: VERDICT }),
   );
   ```

   A single-engine, single-page scaffold may be authored inline — say you skipped the fan-out.

## Phase 3 — validate

Run the gates on the scaffolded site; a failing gate stops the phase (fix the cause, never paper over it):

- **Stub integrity** — `npx pagesmith skills install --check && npx diagramkit skills install --check`. Non-zero means a stub is missing, stale, or orphaned.
- **Site build** — the build command the setup skill wired up (`validateDocs` / the docs build).
- **Diagrams** — `npx diagramkit validate` (structure, embed-safety, contrast) over the seeded diagrams.
- **Preview smoke check** — start the dev server, confirm it serves the seeded pages, then stop it. This is the "ends previewable" guarantee.

## Phase 4 — report

- Emit the `persona.md` output shape: the tree created (guide, reference, diagrams, config, deploy workflow, materialized stubs), the dev / build / deploy commands, and every validator result.
- **Deploy is recommended, never run.** Print the exact deploy command (from the setup skill) for a human to execute. This skill does not push, deploy, or open a PR (`rules.md`).
- Name the skills now available in the repo (`pagesmith-docs-*`, `diagramkit-*`) and note their bodies live version-matched under `node_modules` — the stubs only point.

## Narrate

State each phase boundary, every auto-defaulted Phase 0 choice, the preset chosen and why, which setup/engine skill you delegated to (and any CLI-unavailable fallback you took), the Phase 2 fan-out ("seeding 1 guide + 1 reference + N diagrams in parallel"), and every validator result. Confirm before overwriting anything that already exists. Never go silent for more than a phase, and never claim done without a green build and a smoke-checked preview.
