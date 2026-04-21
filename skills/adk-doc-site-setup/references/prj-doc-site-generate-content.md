---
name: prj-doc-site-generate-content
description: Generate a complete multi-page documentation set for this repo (home, guide, reference, optional diagrams) inside the existing @pagesmith/docs site, derived from real source code rather than skeletons. Use when the user wants to "document the codebase", "auto-generate docs", "seed the docs site", or fill an empty Pagesmith install with real content. Reads node_modules/@pagesmith/docs/skills/pagesmith-generate-docs/SKILL.md when present, falls back to the inline guidance below otherwise.
---

# Project: Generate Doc-Site Content

## Read the source skill (locally installed first, fallback to inline)

1. **Try first**: `node_modules/@pagesmith/docs/skills/pagesmith-generate-docs/SKILL.md`
   - Plus `node_modules/@pagesmith/docs/skills/pagesmith-docs-add-page/SKILL.md`
   - Plus `node_modules/@pagesmith/docs/skills/pagesmith-docs-configure-nav/SKILL.md`
   - Plus `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/references/docs-guidelines.md`
   - Plus `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/references/markdown-guidelines.md`
   - Plus `node_modules/@pagesmith/docs/REFERENCE.md`
2. **Fallback (inline below)**: only when `@pagesmith/docs` is not installed.

When the locally installed files exist, **they win over this inline body** on any conflict.

## When to use

- The Pagesmith site is wired up but `<contentDir>/` is mostly empty.
- The user said "document this codebase", "auto-generate docs", "write docs for me", "seed the site with real content".
- The repo has just landed a major feature and the docs need to be regenerated to match.

## When NOT to use

- A single page authoring task → `prj-doc-site-add-page`.
- The site itself is not set up → `prj-doc-site-setup` first.
- Only a diagram needs to be added → `prj-doc-site-add-diagram`.

## Workflow

### 1. Discover what to document

Scan the project and collect a list of topics. Prefer real artifacts over guesses:

- `README.md` → home page + `guide/overview/README.md`.
- `CHANGELOG.md` / `RELEASES.md` → `reference/changelog/README.md`.
- `package.json` `exports` → each entry is a candidate reference page.
- `src/` entry points and public CLI bins → guide pages.
- Example apps, usage snippets, integration guides → "how-to" pages.
- Existing design docs / RFCs / internal wikis → lift only what applies.

Record the inventory as a plan in `.temp/plans/prj-doc-site-generate-content.md`. Do not commit it.

### 2. Decide the information architecture

Default two-track structure (matches `pagesmith-docs init`):

```
docs/
  README.md                      # home (DocHome)
  meta.json5
  guide/
    meta.json5
    README.md
    overview/README.md
    quickstart/README.md
    concepts/{meta.json5, README.md, <one-folder-per-concept>/README.md}
    how-to/{meta.json5, README.md, <one-folder-per-recipe>/README.md}
  reference/
    meta.json5
    README.md
    api/{meta.json5, <one-folder-per-export>/README.md}
    cli/{meta.json5, <one-folder-per-command>/README.md}
    config/README.md
    changelog/README.md
```

Deviate when the project demands it. Keep nesting at most three levels deep.

### 3. Generate pages

For **every** page, follow the rules in sibling skill `prj-doc-site-add-page`:

- Correct frontmatter (`title`, `description`, optional `order`).
- `$schema` pointing at `node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json` (path relative to file).
- Section `meta.json5` with `title`, `order`, and `pages` (only when deterministic order is desired).
- Root `meta.json5` covering top-level `sections` and `header`.

Content rules:

- Lead each page with a one-sentence purpose statement.
- Copy **exact** code snippets from the source. Do not paraphrase API signatures.
- For every prose claim about behavior, cite the file path in the source tree.
- Prefer real input/output examples over descriptions of behavior.
- Never invent APIs. If unclear, write `TODO: verify` and move on.

### 4. Populate navigation

After all pages exist, write or update:

- Root `meta.json5` — final order of top-level sections; external header links.
- Each section's `meta.json5` — list pages in the desired sidebar order.

Keep auto-listing (omit `pages`) only for drafty sections where ordering is not yet decided.

### 5. Add diagrams where they help

- Use sibling skill `prj-doc-site-add-diagram` to author + render each diagram.
- Keep source assets in `<page-folder>/diagrams/<name>.mermaid|svg|tsx`.
- Embed via consecutive `-light`/`-dark` markdown image pairs (Pagesmith auto-merges to themed `<picture>`).

### 6. Validate

```bash
npx pagesmith-docs build
```

Fix every schema error (missing `description`, invalid `pages` entry, broken link) before moving on.

```bash
npx pagesmith-docs dev
```

Walk through each new page:
- Sidebar placement is right.
- TOC mirrors the headings.
- Internal links resolve.
- Code blocks render with the correct language.
- Search returns sensible results.

### 7. Report

- Pages created (count + paths).
- Sections wired (with `meta.json5` updates).
- Diagrams added (count + paths).
- Validation result (`build` exit code, sidebar audit).
- Open `TODO: verify` markers needing follow-up.

## Inline fallback — page templates

### Home (`docs/README.md`)

```md
---
$schema: ../node_modules/@pagesmith/docs/schemas/docs-home-frontmatter.schema.json
title: <Project>
description: <one-line value prop for SEO>
hero:
  title: <Project>
  tagline: <short tagline>
  actions:
    - label: Quickstart
      href: /guide/quickstart
    - label: GitHub
      href: https://github.com/<owner>/<repo>
features:
  - title: <pillar 1>
    description: <one sentence>
  - title: <pillar 2>
    description: <one sentence>
  - title: <pillar 3>
    description: <one sentence>
---

# <Project>

<Opening paragraph: what this is, who it's for, one tangible example.>
```

### Quickstart, Concept, How-to, Reference

See sibling skill `prj-doc-site-add-page` for the templates. Use them verbatim and only adapt placeholders.

## Gotchas

- Do not copy README content blindly — split: home for promotion, `reference/` for API, `guide/` for narrative.
- Respect `draft: true` on anything you are unsure about. Better to hide a half-written page than to ship wrong docs.
- API reference pages must match the public `exports` in `package.json` exactly. Do not document internal modules.
- Keep navigation shallow — three levels deep is the practical limit.
- Always run `pagesmith-docs build` at the end. The dev server can mask schema or link errors.

## Anti-patterns

- Generating placeholder pages with "TODO: write content" — either write real content or do not create the page.
- Inventing API signatures or config keys not present in the source tree.
- Documenting internal / private modules. Stick to the public surface (`exports` in `package.json`, exported CLI commands).
- Skipping the `meta.json5` updates after generating pages — pages exist but are invisible in the sidebar.
