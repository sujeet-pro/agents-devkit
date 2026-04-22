---
name: prj-doc-site-setup
description: Reconfigure or re-bootstrap the @pagesmith/docs + diagramkit doc-site in this repo. Use when packages need reinstalling, configs are missing, the docs/ tree needs rescaffolding, or sibling prj-doc-site-* skills need refreshing. Reads node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/SKILL.md and node_modules/diagramkit/skills/diagramkit-setup/SKILL.md when present, falls back to the inline guidance below otherwise.
---

# Project: Doc-Site Setup

> Use this skill to **re-run** or **adjust** the docs-site setup that `adk-doc-site-setup` originally performed in this repo. For first-time bootstrap of a brand-new repo, prefer `adk-doc-site-setup` from the agents-devkit installation.

## Read the source skills (locally installed first, fallback to inline)

1. **Try first**: `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/SKILL.md`
   - Plus `node_modules/@pagesmith/docs/REFERENCE.md` and `node_modules/@pagesmith/docs/schemas/pagesmith-config.schema.json`.
2. **And**: `node_modules/diagramkit/skills/diagramkit-setup/SKILL.md`
   - Plus `node_modules/diagramkit/REFERENCE.md` and `node_modules/diagramkit/schemas/diagramkit-config.v1.json`.
3. **Fallback (inline below)**: only when one or both packages are not installed.

When the locally installed files exist, **they win over this inline body** on any conflict.

## When to use

- `pagesmith.config.json5` or `diagramkit.config.json5` is missing or invalid.
- `package.json` no longer has the `docs:*` or `render:diagrams*` scripts.
- The `prj-doc-site-*` skills are missing from `.agents/skills/` (or any of the harness folders).
- The repo just upgraded `@pagesmith/docs` or `diagramkit` and the agent should re-read the version-pinned references.
- The `docs/` content directory was renamed or moved.

## When NOT to use

- A single page needs to be added → `prj-doc-site-add-page`.
- A bulk content generation pass → `prj-doc-site-generate-content`.
- Sidebar / nav reordering only → `prj-doc-site-configure-nav`.
- Adding or refreshing a diagram → `prj-doc-site-add-diagram`.
- Deployment plumbing only → `prj-doc-site-deploy`.

## Workflow

1. **Audit state**:
   - `@pagesmith/docs` and `diagramkit` in `package.json`?
   - `pagesmith.config.json5` exists with valid `$schema`, `name`, `title`, `origin`, `basePath`, `contentDir`, `outDir`?
   - `diagramkit.config.json5` exists with `mermaidLayout: { mode: 'auto' }`?
   - `<contentDir>/README.md`, `<contentDir>/meta.json5`, `guide/`, `reference/` all present?
   - `package.json` has `docs:dev`, `docs:build`, `docs:preview`, `render:diagrams*` scripts?
   - `.agents/skills/prj-doc-site-*` pointers exist? Mirrored into detected harness folders?

2. **Plan changes** in `.temp/plans/prj-doc-site-setup.md`. Confirm with the user before overwriting any existing config or scaffold.

3. **Apply** — install missing packages, run `npx pagesmith-docs init` and `npx diagramkit init` for missing config, scaffold missing `meta.json5` / `README.md` files, add missing `package.json` scripts, write missing `prj-*` pointers.

4. **Validate**:
   ```bash
   npx diagramkit render . --force
   npx diagramkit validate . --recursive
   npx pagesmith-docs build
   ```
   All three must exit 0 with no errors and no `LOW_CONTRAST_TEXT` / `ASPECT_RATIO_EXTREME` warnings.

5. **Report** — files changed, validation results, any follow-ups.

## Inline fallback — full setup playbook

### 1. Install packages

```bash
npm add @pagesmith/docs diagramkit
# Only if PNG / JPEG / WebP / AVIF output is needed:
npm add sharp
```

### 2. Pagesmith config

Run interactive (or `--yes` for non-interactive):

```bash
npx pagesmith-docs init           # interactive
# or:
npx pagesmith-docs init --yes \
  --content-dir ./docs \
  --base-path /<repo-name> \
  --origin https://<owner>.github.io \
  --ai
```

Confirm `pagesmith.config.json5` includes:

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

`basePath` must start with `/` and not end with `/` (except `/`). `contentDir` is relative to the config file. Never set `origin` to `http://localhost`.

### 3. Diagramkit config

```bash
npx diagramkit init --yes
# Skip warmup if Graphviz-only:
npx diagramkit warmup
```

Confirm `diagramkit.config.json5` includes at least:

```json5
{
  $schema: "./node_modules/diagramkit/schemas/diagramkit-config.v1.json",
  mermaidLayout: { mode: "auto", targetAspectRatio: 4 / 3, tolerance: 2.5 },
}
```

### 4. Scaffold the content tree

```
<contentDir>/
  README.md
  meta.json5
  guide/
    meta.json5
    README.md
    getting-started/README.md
    quickstart/README.md
    concepts/{meta.json5, README.md, <one-folder-per-concept>/README.md}
    how-to/{meta.json5, README.md, <one-folder-per-recipe>/README.md}
  reference/
    meta.json5
    README.md
    overview/README.md
    api/{meta.json5, <one-folder-per-export>/README.md}
    cli/{meta.json5, <one-folder-per-command>/README.md}
    config/README.md
    changelog/README.md
```

Page templates and `meta.json5` shapes — see sibling `prj-doc-site-add-page` and `prj-doc-site-configure-nav` skills.

### 5. `package.json` scripts

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

### 6. Re-install sibling prj-doc-site-* skills

For each skill (`prj-doc-site-add-page`, `prj-doc-site-generate-content`, `prj-doc-site-configure-nav`, `prj-doc-site-add-diagram`, `prj-doc-site-deploy`), make sure:

- The canonical `.agents/skills/<name>/SKILL.md` exists.
- Mirror pointers exist in every harness folder the repo uses (`.claude/`, `.cursor/`, `.codex/`, `.continue/`).

## Anti-patterns

- Overwriting an existing `pagesmith.config.json5` or `diagramkit.config.json5` without showing the user the diff first.
- Skipping `mermaidLayout: { mode: 'auto' }` in `diagramkit.config.json5` — every future Mermaid diagram will trigger `ASPECT_RATIO_EXTREME` warnings the agent has to chase.
- Setting `origin` to `http://localhost`.
- Re-scaffolding `<contentDir>/` on top of existing content. Audit and reuse existing pages.
