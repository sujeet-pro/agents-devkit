---
name: adk-doc-site-setup
description: Bootstrap a documentation site in a project using @pagesmith/docs (content + nav + search + theme) and diagramkit (mermaid / graphviz / drawio / excalidraw rendering). Installs the npm packages, writes pagesmith.config.json5 and diagramkit.config.json5, scaffolds the docs/ tree with guide and reference groupings (meta.json5 + README.md), wires npm scripts, and installs prj-doc-site-* skills into the consumer project so future agents can keep adding pages, generating content, configuring nav, embedding diagrams, and deploying. Use whenever the user asks to set up a docs site, scaffold Pagesmith+diagramkit, add documentation tooling, or bootstrap a doc site for a repo. Each installed prj-* skill reads from node_modules/<pkg>/skills/ first and falls back to the inlined references shipped with this skill, so it keeps working even if the packages are uninstalled.
---

# ADK Doc-Site Setup

Standalone task skill that turns any repo into a working documentation site backed by **`@pagesmith/docs`** (the docs framework) and **`diagramkit`** (the diagram rendering toolkit), then installs a set of `prj-doc-site-*` project-level skills so future agent sessions can keep extending the site without re-reading this skill.

## When to use

- The repo has no docs site yet and the user wants Pagesmith + diagramkit added.
- The repo has docs scattered in `README.md` / `docs/` but no build, search, or nav config.
- The user said "set up docs", "scaffold a docs site", "add Pagesmith", "bootstrap docs", or similar — even without naming the packages.
- The user wants the project's agents to be able to keep adding pages and diagrams without re-running this setup skill every time.

## When NOT to use

- A `pagesmith.config.json5` already exists and the docs site already builds. → use the installed `prj-doc-site-add-page`, `prj-doc-site-configure-nav`, or `prj-doc-site-add-diagram` skill instead.
- The user only needs a single doc file authored (no site). → `adk-docs-write`.
- Reviewing existing docs. → `adk-docs-review`.
- Designing the docs architecture before scaffolding. → `adk-plan-design` first, then come back here.

## Inputs

| Input             | Required | Notes                                                                                        |
| ----------------- | -------- | -------------------------------------------------------------------------------------------- |
| `<project root>`  | yes      | Defaults to current working directory; must contain a writable `package.json`.               |
| `<content dir>`   | optional | Defaults to `./docs` (falls back to `./content` if `docs/` cannot be used).                  |
| `<base path>`     | optional | Defaults to `/<repo-name>` (GitHub Pages style). Use `/` only for custom-domain root hosts.  |
| `<origin>`        | optional | Defaults to `https://<owner>.github.io` (probed); pass explicit value for custom domains.    |
| `<diagram-only?>` | optional | If true (Graphviz-only repo), `diagramkit warmup` is skipped.                                |
| `--auto`          | optional | Skip the approval gate; non-interactive init flags are used everywhere.                      |
| `--skip-deploy`   | optional | Do not write `.github/workflows/gh-pages.yml`; only scaffold the site locally.               |


## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **Is there already a pagesmith.config.json5? Should we overwrite it?** — _How to pick:_ Default = no, never silent. Yes = explicit user approval needed.
2. **What is the base path (GitHub Pages style `/<repo>/` or custom-domain root `/`)?** — _How to pick:_ GitHub Pages without custom domain → `/<repo>/`. Custom domain → `/`. Subpath hosting → explicit.
3. **Skip GitHub Pages workflow (--skip-deploy)?** — _How to pick:_ Skip when the repo deploys via Vercel/Netlify/S3/custom; the gh-pages workflow would conflict.
4. **Diagram-only repo (Graphviz only, no Mermaid/Excalidraw/Draw.io)?** — _How to pick:_ Yes → skip `diagramkit warmup`. No → warmup required.

## Workflow

### 1. Confirm intent (approval gate unless `--auto`)

Restate the plan in one short paragraph:

- Packages to install (`@pagesmith/docs`, `diagramkit`, optionally `sharp` for raster, `pagefind` is transitive).
- Detected `<content dir>`, `<base path>`, `<origin>`, GitHub deploy yes/no.
- The `prj-doc-site-*` skills that will be installed into `.agents/skills/` (and mirrored into `.claude/skills/`, `.cursor/skills/`, `.codex/skills/` when those harness folders exist).
- Whether to overwrite an existing `pagesmith.config.json5` / `diagramkit.config.json5` (default: no, prompt).

Wait for approval. Skip the gate entirely under `--auto`.

### 2. Detect existing state

Before writing anything, check:

1. Is `@pagesmith/docs` already in `package.json` `dependencies` / `devDependencies`?
2. Is `diagramkit` already installed?
3. Does `pagesmith.config.json5` (or `.ts` / `.mjs`) exist? Does `diagramkit.config.json5` (or `.ts`)?
4. Any existing docs-like folder candidate? (`docs/`, `documentation/`, `guide/`, `content/`, `wiki/`).
5. Any existing diagram source? (`*.mermaid`, `*.mmd`, `*.excalidraw`, `*.drawio`, `*.dot`, `*.gv`).
6. Which harness folders exist? (`.claude/`, `.cursor/`, `.codex/`, `.continue/`, `.agents/`).

Skip any sub-step in the workflow whose outcome is already correct. Never silently overwrite an existing config; always confirm.

### 3. Install packages

```bash
npm add @pagesmith/docs diagramkit
# Only if the user will render PNG/JPEG/WebP/AVIF (not SVG-only):
npm add sharp
```

After install, **read the version-matched references the consumer project now ships**:

- `node_modules/@pagesmith/docs/REFERENCE.md`
- `node_modules/@pagesmith/docs/schemas/*.schema.json`
- `node_modules/diagramkit/REFERENCE.md`
- `node_modules/diagramkit/llms.txt`

If any of these disagree with this skill or the inline references in `references/`, **follow the local files** — they are pinned to the exact installed package version.

If the package is not installed and the user does not want it installed, fall back to the inline copies in `references/`. They are intentionally up to date with the published skills at the time `adk-doc-site-setup` was authored, but they are not version-matched to the user's installed package.

### 4. Run `pagesmith-docs init`

Always invoke through `npx` so the local bin is used:

```bash
# Interactive (recommended unless --auto):
npx pagesmith-docs init

# Non-interactive (CI / agent / --auto):
npx pagesmith-docs init --yes \
  --content-dir ./docs \
  --base-path /<repo-name> \
  --origin https://<owner>.github.io \
  --ai
```

`--ai` writes `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` memory pointers and `.pagesmith/markdown-guidelines.md` so future agent sessions inherit the contract. The init command is idempotent — safe to re-run; it backfills missing scaffold and refreshes the `$schema` pointer.

If init writes `pagesmith.config.json5`, confirm it includes:

```json5
{
  $schema: "./node_modules/@pagesmith/docs/schemas/pagesmith-config.schema.json",
  name: "<repo-name>",
  title: "<Title>",
  origin: "https://<owner>.github.io",
  basePath: "/<repo-name>",
  contentDir: "./docs",
  outDir: "./gh-pages",
}
```

`basePath` must start with `/` and not end with `/` (except when it is exactly `/`). `contentDir` must be relative to the config file. See `references/pagesmith-setup.md` for full guidance.

### 5. Run `diagramkit init` and `diagramkit warmup`

```bash
# Always create the config so mermaidLayout: { mode: 'auto' } is set
npx diagramkit init --yes

# Skip warmup when the project is Graphviz-only (no .mermaid / .excalidraw / .drawio sources)
npx diagramkit warmup
```

Confirm the resulting `diagramkit.config.json5` includes at least:

```json5
{
  $schema: "./node_modules/diagramkit/schemas/diagramkit-config.v1.json",
  mermaidLayout: { mode: "auto", targetAspectRatio: 4 / 3, tolerance: 2.5 },
}
```

`mermaidLayout: { mode: 'auto' }` is what lets the renderer auto-flip `LR ↔ TB` and try ELK when a diagram's aspect ratio drifts wide or tall — without it, every `ASPECT_RATIO_EXTREME` warning has to be fixed source-by-source. See `references/diagramkit-setup.md`.

### 6. Scaffold the `docs/` tree (guide + reference grouping)

If `pagesmith-docs init` did not seed pages already, write the canonical two-track structure:

```
<content-dir>/
  README.md                        # home page (DocHome layout)
  meta.json5                       # root: top-level sections + header links
  guide/
    meta.json5                     # title: "Guide", order: 1
    README.md                      # guide landing
    getting-started/
      meta.json5
      README.md                    # /guide/getting-started
    quickstart/
      meta.json5
      README.md                    # /guide/quickstart
    concepts/
      meta.json5                   # series: list of concept pages
      README.md
      <one-per-concept>/README.md
    how-to/
      meta.json5
      README.md
      <one-per-recipe>/README.md
  reference/
    meta.json5                     # title: "Reference", order: 2
    README.md                      # reference landing
    overview/README.md
    api/
      meta.json5
      README.md
      <one-per-public-export>/README.md
    cli/
      meta.json5
      README.md
      <one-per-command>/README.md
    config/README.md
    changelog/README.md            # often regenerated from CHANGELOG.md
```

Rules:

- Every page is a folder containing `README.md`. Page-local images and diagrams live in a sibling `diagrams/` folder so `<page>/diagrams/<name>.mermaid` and the rendered `<name>-light.svg` / `<name>-dark.svg` move together.
- Every page's frontmatter has at least `title` and `description`. Use `$schema: "../../node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json"` (path relative to the page) so editors auto-complete frontmatter.
- Home page uses the `docs-home-frontmatter.schema.json` and includes `hero`, `features`, optionally `actions`, `packages`, `codeExample`.
- Each section `meta.json5` should set `title`, `order`, optionally `collapsed`. Use `pages: [...]` only when you want a deterministic sidebar order — leaving `pages` out makes the section auto-pick up new files (sorted by frontmatter `order` then title).
- Root `meta.json5` controls top-level nav: `sections: ["guide", "reference"]` plus `header: [{ label, path }]` items.
- Keep navigation at most 3 levels deep.

Detailed templates are in `references/pagesmith-add-page.md`, `references/pagesmith-configure-nav.md`, and `references/pagesmith-generate-content.md`.

### 7. Wire `package.json` scripts

Add (only those not already present):

```json
{
  "scripts": {
    "docs:dev": "pagesmith-docs dev",
    "docs:build": "pagesmith-docs build",
    "docs:preview": "pagesmith-docs preview",
    "render:diagrams": "diagramkit render .",
    "render:diagrams:watch": "diagramkit render . --watch",
    "render:diagrams:check": "diagramkit validate . --recursive"
  }
}
```

Use the repo's existing convention if it has one (e.g. `diagrams:build` instead of `render:diagrams`).

### 8. Install the `prj-doc-site-*` skills into the consumer project

This is the durable handoff. The agent that next opens this repo should not need to re-read `adk-doc-site-setup`; it should see project-level skills already wired up.

For each skill in the table below, write **two files** in the consumer project:

| Project skill                     | Purpose                                                                                  | Source template (this skill)                |
| --------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------- |
| `prj-doc-site-setup`              | Re-run setup or reconfigure pagesmith + diagramkit in this repo                          | `references/prj-doc-site-setup.md`          |
| `prj-doc-site-add-page`           | Add or update a single doc page (frontmatter, file placement, sidebar slot)              | `references/prj-doc-site-add-page.md`       |
| `prj-doc-site-generate-content`   | Generate a complete multi-page doc set from the codebase                                 | `references/prj-doc-site-generate-content.md` |
| `prj-doc-site-configure-nav`      | Sidebar / top-nav / section ordering via `meta.json5` + frontmatter                      | `references/prj-doc-site-configure-nav.md`  |
| `prj-doc-site-add-diagram`        | Author + render a diagram with diagramkit and embed it as a theme-aware `<picture>` pair | `references/prj-doc-site-add-diagram.md`    |
| `prj-doc-site-deploy`             | Build + publish the docs site (GitHub Pages workflow + alternatives)                     | `references/prj-doc-site-deploy.md`         |

For each project skill `<name>`:

1. Write the canonical pointer at `<project>/.agents/skills/<name>/SKILL.md`. The body is the contents of `references/<name>.md` (verbatim) — that file is already a complete, frontmatter-prefixed SKILL.md.
2. Mirror it into every harness folder the repo uses, as a thin pointer that links back to the canonical file:

   ```markdown
   ---
   name: <name>
   description: <copy description from references/<name>.md>
   ---

   # <name>

   Follow [`.agents/skills/<name>/SKILL.md`](../../../.agents/skills/<name>/SKILL.md). Do not duplicate its content here.
   ```

   Detection rules (from `diagramkit-setup` step 5a, applied to both packages):

   | Harness             | Folder              | Detect by                                                |
   | ------------------- | ------------------- | -------------------------------------------------------- |
   | Claude Code         | `.claude/skills/`   | `.claude/` exists, or user mentions Claude / Claude Code |
   | Cursor              | `.cursor/skills/`   | `.cursor/` exists, or user mentions Cursor               |
   | Codex               | `.codex/skills/`    | `.codex/` exists, or user mentions Codex                 |
   | Continue            | `.continue/skills/` | `.continue/` exists, or user mentions Continue           |
   | OpenCode / generic  | `.agents/skills/`   | Always written (canonical location)                      |

3. Commit all installed `prj-doc-site-*` skill files. They are tiny, version-stable across pagesmith / diagramkit upgrades, and let every agent on the team start from the same baseline.

#### How the prj-* skills handle missing node_modules

Each `prj-doc-site-*` skill template uses this read-order pattern at the top of its `SKILL.md`:

```markdown
## Read the source skill (locally installed first, fallback to inline)

1. **Try first**: `node_modules/@pagesmith/docs/skills/<source-skill>/SKILL.md`
   (and the corresponding files under `node_modules/@pagesmith/docs/schemas/` and
   `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/references/`).
2. **Or for diagramkit**: `node_modules/diagramkit/skills/<source-skill>/SKILL.md`
   plus the engine reference under `node_modules/diagramkit/skills/<engine>/references/`.
3. **Fallback (inline below)**: only if (1) and (2) are both missing because the
   packages are not installed in this repo. The inline section is the version
   shipped with `adk-doc-site-setup` at the time it was installed and may lag
   the package in `node_modules/`.
```

This makes the installed skills self-healing: as long as `@pagesmith/docs` and `diagramkit` are in `node_modules/`, the agent reads the version-matched skill bodies; if both packages are uninstalled (or the project is checked out fresh without `npm install`), the inline fallback keeps the skills usable.

### 9. Add a hello-world page + diagram

If the project has no diagram source files yet, seed one so the user sees the full pipeline working:

```
<content-dir>/guide/getting-started/diagrams/hello.mermaid
```

```mermaid
%%{init: {'htmlLabels': false}}%%
flowchart LR
  A[Source] --> B[diagramkit] --> C[SVG]
  C --> D[Pagesmith page]
```

Render with `npx diagramkit render <content-dir>/guide/getting-started/diagrams/hello.mermaid`.

Then embed in `<content-dir>/guide/getting-started/README.md` using the consecutive `-light` / `-dark` markdown image pattern (Pagesmith auto-merges the pair into a themed `<picture>`):

```md
![Pipeline diagram showing source files rendered through diagramkit into a Pagesmith page](./diagrams/hello-light.svg "Doc site pipeline")
![Pipeline diagram showing source files rendered through diagramkit into a Pagesmith page](./diagrams/hello-dark.svg)
```

### 10. Validate the full setup

Run, in order:

```bash
npx diagramkit render . --force
npx diagramkit validate . --recursive
npx pagesmith-docs build
npx pagesmith-docs preview
```

The setup is **only complete** when all four commands exit 0 and `validate` reports no errors, no `LOW_CONTRAST_TEXT` warnings, and no `ASPECT_RATIO_EXTREME` warnings (per `references/diagramkit-setup.md`).

Open `http://localhost:4321` (or whatever port `preview` reports) and check:

- Home page renders with hero / features / CTAs.
- Sidebar shows both `Guide` and `Reference` sections in the chosen order.
- The hello-world page is reachable and the diagram renders in both light and dark mode.
- Search returns sensible results for the home title.

### 11. Deploy (optional — skip with `--skip-deploy`)

For GitHub Pages, write `.github/workflows/gh-pages.yml` per `references/pagesmith-deploy-gh-pages.md`. For other hosts (Vercel, Netlify, S3, custom), point the user at the relevant section of that reference and at `gh-pages/` as the build artifact.

### 12. Report

Use the format in `references/output-format.md`. Include:

- File paths created or modified (config, scaffold, scripts, prj-* skills, deploy workflow).
- The `prj-doc-site-*` skills installed and the harnesses they were mirrored into.
- Validation results from step 10 (build exit code, validate warnings).
- Follow-ups (e.g. content TODOs, `draft: true` pages still hidden from production, deploy DNS step).
- Offer: "Want me to seed real content from the codebase next?" → routes to `prj-doc-site-generate-content`.

**Default report:** Created/modified file paths + prj-doc-site-* skills installed + harness mirrors + validation results + follow-ups.

**Detailed report (on request or `--verbose`):** Add: full pagesmith.config + diagramkit.config emitted, scaffold tree before/after, deploy URL, follow-up content TODOs.

**Artifact:** `doc-site-bootstrap` — Files in the consumer repo (config + scaffold + scripts + workflow) + prj-doc-site-* skills mirrored into harness folders.

**Artifact path:** Consumer repo: pagesmith.config.json5, diagramkit.config.json5, docs/, .github/workflows/gh-pages.yml, .agents/skills/prj-doc-site-*/, harness mirrors. Setup log in .temp/notes/doc-site-setup-<date>.md.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **Is there already a pagesmith.config.json5? Should we overwrite it?** — _How to pick:_ Default = no, never silent. Yes = explicit user approval needed.
2. **What is the base path (GitHub Pages style `/<repo>/` or custom-domain root `/`)?** — _How to pick:_ GitHub Pages without custom domain → `/<repo>/`. Custom domain → `/`. Subpath hosting → explicit.
3. **Skip GitHub Pages workflow (--skip-deploy)?** — _How to pick:_ Skip when the repo deploys via Vercel/Netlify/S3/custom; the gh-pages workflow would conflict.
4. **Diagram-only repo (Graphviz only, no Mermaid/Excalidraw/Draw.io)?** — _How to pick:_ Yes → skip `diagramkit warmup`. No → warmup required.

**Default report:** Created/modified file paths + prj-doc-site-* skills installed + harness mirrors + validation results + follow-ups.

**Detailed report (on request or `--verbose`):** Add: full pagesmith.config + diagramkit.config emitted, scaffold tree before/after, deploy URL, follow-up content TODOs.

**Artifact:** `doc-site-bootstrap` — Files in the consumer repo (config + scaffold + scripts + workflow) + prj-doc-site-* skills mirrored into harness folders.

**Artifact path:** Consumer repo: pagesmith.config.json5, diagramkit.config.json5, docs/, .github/workflows/gh-pages.yml, .agents/skills/prj-doc-site-*/, harness mirrors. Setup log in .temp/notes/doc-site-setup-<date>.md.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **Is there already a pagesmith.config.json5? Should we overwrite it?** — _How to pick:_ Default = no, never silent. Yes = explicit user approval needed.
2. **What is the base path (GitHub Pages style `/<repo>/` or custom-domain root `/`)?** — _How to pick:_ GitHub Pages without custom domain → `/<repo>/`. Custom domain → `/`. Subpath hosting → explicit.
3. **Skip GitHub Pages workflow (--skip-deploy)?** — _How to pick:_ Skip when the repo deploys via Vercel/Netlify/S3/custom; the gh-pages workflow would conflict.
4. **Diagram-only repo (Graphviz only, no Mermaid/Excalidraw/Draw.io)?** — _How to pick:_ Yes → skip `diagramkit warmup`. No → warmup required.

## Default vs detailed output

**Default report:** Created/modified file paths + prj-doc-site-* skills installed + harness mirrors + validation results + follow-ups.

**Detailed report (on request or `--verbose`):** Add: full pagesmith.config + diagramkit.config emitted, scaffold tree before/after, deploy URL, follow-up content TODOs.

**Artifact:** `doc-site-bootstrap` — Files in the consumer repo (config + scaffold + scripts + workflow) + prj-doc-site-* skills mirrored into harness folders.

**Artifact path:** Consumer repo: pagesmith.config.json5, diagramkit.config.json5, docs/, .github/workflows/gh-pages.yml, .agents/skills/prj-doc-site-*/, harness mirrors. Setup log in .temp/notes/doc-site-setup-<date>.md.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |

<!-- adk:references:end -->

## Anti-patterns

- Skipping the install of the `prj-doc-site-*` skills. Without them, every future doc change requires re-reading this skill from scratch.
- Skipping `diagramkit init` because "we'll only render Graphviz". Without `mermaidLayout: { mode: 'auto' }` in config, any future Mermaid diagram triggers `ASPECT_RATIO_EXTREME` warnings the agent has to chase one by one.
- Hand-editing rendered SVGs in `.diagramkit/` instead of editing the source.
- Hardcoding `%%{init: {theme: ...}}%%` in Mermaid sources — diagramkit owns theme injection.
- Setting `pagesmith.config.json5` `origin` to `http://localhost`. Use the real production origin even for local builds — Pagesmith only uses it for canonical URLs and `sitemap.xml`.
- Writing pagesmith config with absolute paths in `contentDir`. Always relative to the config file.
- Skipping `pagesmith-docs build` after wiring everything. The dev server can mask schema and link errors that fail the production build.
- Mixing two skill-install mechanisms (this skill's `prj-*` install AND `npx skills add sujeet-pro/diagramkit`) in the same repo. Pick one.
