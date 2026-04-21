# Pagesmith Setup Reference (fallback)

> This file is the inline fallback for `@pagesmith/docs` setup guidance. When the package is installed, prefer:
> - `node_modules/@pagesmith/docs/REFERENCE.md` — full config + CLI reference (version-pinned).
> - `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/SKILL.md` — official setup skill.
> - `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/references/setup-docs.md` — canonical bootstrap/retrofit playbook.
> - `node_modules/@pagesmith/docs/schemas/pagesmith-config.schema.json` — config schema for IDE auto-complete.

## What `@pagesmith/docs` gives you

- A convention-based docs site built on the Pagesmith content + site stack.
- Optional `pagesmith.config.json5` (zero-config also works when `docs/` exists at the repo root).
- A docs home page from `<contentDir>/README.md`.
- Top navigation from top-level content folders.
- Flat per-section sidebars with ordering and grouping from `meta.json5`.
- Built-in Pagefind search, breadcrumbs, prev/next links, theme controls, edit links, layout overrides.
- Asset publishing via `publicDir`, `assets`, automatic root `llms.txt` / `llms-full.txt` copying, content-relative companion asset rewrites.
- The shared Pagesmith markdown pipeline: GFM, GitHub alerts, math, smartypants, code blocks with line numbers / titles / highlights / collapse.

## Prerequisites

- Node.js 24+. Pagesmith will not run on older versions.
- `npm` (tested), `pnpm` or `yarn` (treat commands below as interchangeable).
- A writable project directory with a `package.json`.

## Fast path (interactive init)

```bash
npm add @pagesmith/docs
npx pagesmith-docs init
```

Prompts and good defaults:

| Prompt          | Default source            | Notes                                                      |
| --------------- | ------------------------- | ---------------------------------------------------------- |
| Project name    | `package.json` `name`     | Becomes `name` in `pagesmith.config.json5`.                |
| Title           | Project name, title-cased | Used in `<title>` and header.                              |
| Origin          | Probed from `git remote`  | For GitHub repos tries `https://<owner>.github.io`.        |
| Base path       | `/<repo-name>`            | Leave `/` only if hosting at a custom-domain root.         |
| Content dir     | `./docs`                  | Falls back to `./content` if `docs/` is not desired.       |
| Search          | `true`                    | Enables Pagefind. Adds ~300KB to first build.              |
| AI integrations | `true`                    | Writes `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` memory files. |

## Non-interactive init (CI / scripts / agents)

```bash
npx pagesmith-docs init --yes \
  --name my-docs \
  --title "My Docs" \
  --base-path /my-docs \
  --origin https://acme.github.io \
  --content-dir ./docs \
  --search \
  --ai
```

`--ai` writes `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `.pagesmith/markdown-guidelines.md` so downstream agents inherit the contract.

The init command is **idempotent**: re-running updates `pagesmith.config.json5`, backfills missing scaffold fields, and refreshes the `$schema` pointer to the installed package schema.

## Resulting config (`pagesmith.config.json5`)

Minimum you should commit at the repo root:

```json5
{
  $schema: "./node_modules/@pagesmith/docs/schemas/pagesmith-config.schema.json",
  name: "my-docs",
  title: "My Docs",
  origin: "https://acme.github.io",
  basePath: "/my-docs",
  contentDir: "./docs",
  outDir: "./gh-pages",
}
```

Rules:

- `basePath` must start with `/` and not end with `/` (except when it is exactly `/`). `my-docs` and `/my-docs/` both break asset URLs.
- `origin` must be the real production origin even for local builds. Pagesmith only uses it for canonical URLs and `sitemap.xml`. Never `http://localhost`.
- `contentDir` must be relative to the config file (not absolute) so Docker and CI work.
- `outDir` defaults to `./gh-pages` and is conventionally git-ignored.

## What init writes

```
<project-root>/
  pagesmith.config.json5
  docs/
    README.md                            # home
    guide/
      meta.json5
      README.md
      getting-started/README.md
      configuration/README.md
    reference/
      meta.json5
      README.md
      overview/README.md
      api/README.md
  public/                                # optional static assets
  gh-pages/                              # build output (git-ignored)
  .github/workflows/gh-pages.yml         # if --ai or deploy chosen
  AGENTS.md / CLAUDE.md / GEMINI.md      # if --ai
  .pagesmith/markdown-guidelines.md      # if --ai
```

Add `gh-pages/` and `.pagesmith/` to `.gitignore` if not already listed.

## Zero-config fallback

`pagesmith-docs dev`, `build`, `preview`, and `mcp --stdio` work with no `pagesmith.config.json5` as long as:

- `docs/` (preferred) or `content/` exists at the project root.
- Output goes to `<repo-root>/gh-pages` by default.

Agents usually still want an explicit `pagesmith.config.json5` for predictable builds. Only skip it when the repo has nothing to configure.

## `package.json` scripts

```json
{
  "scripts": {
    "docs:dev": "pagesmith-docs dev",
    "docs:build": "pagesmith-docs build",
    "docs:preview": "pagesmith-docs preview"
  }
}
```

`pagesmith-docs` is the package's bin; it delegates to the `pagesmith-site` runtime with the docs preset already attached.

## Validate

1. `npx pagesmith-docs dev` — dev server on `http://localhost:4321` (default).
2. Open the home page and one seeded guide page. Both must render.
3. `npx pagesmith-docs build` — must exit 0.
4. `npx pagesmith-docs preview` — must serve the built site from disk.

Only declare the setup done when all four succeed.

## TypeScript config

When the repo already authors config in TypeScript (`pagesmith.config.ts`), keep it as-is and use `defineConfig` from `@pagesmith/docs`. Init writes JSON5 only — when a TypeScript config already exists, init reads it for prompt defaults but never overwrites the file.

Resolution order: `--config <path>` → `pagesmith.config.ts` → `.mts` → `.mjs` → `.js` → `.json5` → `.json`.

## Gotchas

- `basePath` syntax: must start with `/` and not end with `/` (except `/`).
- `origin` must be the production origin (never `http://localhost`).
- `contentDir` must be relative to the config file.
- If a project already has a `CLAUDE.md`/`AGENTS.md`, init **appends** guidance rather than overwriting. Review the diff before committing.
- `pagefind` is pulled in transitively. If search is disabled, that download still happens — mention it so users aren't surprised.
- Init is safe to re-run.

## MCP server (stdio)

`@pagesmith/docs` exposes a stdio MCP server for AI tooling:

- Command: `pagesmith-docs mcp --stdio`
- Optional flags: `--config <path>`, `--root <path>`
- Programmatic entry: `@pagesmith/docs/mcp`

Primary tools: `docs_validate_config`, `docs_resolve_config`, `docs_list_pages`, `docs_get_page`, `docs_search_pages`.

## Versioning model

- The installed npm package is the versioned source of truth for AI guidance.
- Files under `node_modules/@pagesmith/docs/skills/...` and `node_modules/@pagesmith/docs/schemas/*` match the exact installed package version.
- This inline reference is a snapshot and may lag the installed package.
