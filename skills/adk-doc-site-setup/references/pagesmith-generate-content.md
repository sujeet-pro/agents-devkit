# Pagesmith Generate-Content Reference (fallback)

> Inline fallback for generating a complete multi-page documentation set in a `@pagesmith/docs` site. When the package is installed, prefer:
> - `node_modules/@pagesmith/docs/skills/pagesmith-generate-docs/SKILL.md`
> - `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/references/docs-guidelines.md`
> - `node_modules/@pagesmith/docs/REFERENCE.md`

This reference is the step **after** site setup. Once `pagesmith.config.json5` exists and `npx pagesmith-docs dev` works, use this to seed meaningful content from the actual codebase.

## Workflow

### 1. Discover what to document

Scan the project and collect a list of topics. Prefer real artifacts over guesses:

- `README.md` — turn into a home page + `guide/overview/README.md`.
- `CHANGELOG.md` or `RELEASES.md` — becomes `reference/changelog/README.md`.
- `package.json` `exports` — each entry is a candidate reference page.
- `src/` entry points and public CLI bins — guide pages for each.
- Example apps, usage snippets, integration guides — become "How to" pages.
- Existing design docs, RFCs, internal wikis — lift only what applies.

Record the inventory as a plan in `.temp/plans/pagesmith-generate-docs.md`. Do not commit it.

### 2. Decide the information architecture

Recommended two-track structure (matches the default `pagesmith-docs init`):

```
docs/
  README.md                      # home (DocHome)
  meta.json5                     # root nav: sections + header
  guide/
    meta.json5                   # title: "Guide", order: 1
    README.md                    # /guide
    overview/README.md
    quickstart/README.md
    concepts/
      meta.json5                 # series: optional grouping
      README.md
      <one-folder-per-concept>/README.md
    how-to/
      meta.json5
      README.md
      <one-folder-per-recipe>/README.md
  reference/
    meta.json5                   # title: "Reference", order: 2
    README.md                    # /reference
    api/
      meta.json5
      <one-folder-per-public-export>/README.md
    cli/
      meta.json5
      <one-folder-per-command>/README.md
    config/README.md
    changelog/README.md
```

Deviate when the project clearly demands it (single-CLI tool, library-only, website generator). Keep nesting at most three levels deep.

### 3. Generate pages

For **every** page, follow the rules in `pagesmith-add-page.md`:

- Correct frontmatter (`title`, `description`, optional `order`).
- `$schema` pointing at `node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json` (path relative to the file).
- Section `meta.json5` with `title`, `order`, optional `pages` for deterministic ordering.
- Root `meta.json5` covering top-level `sections` and `header`.

Content rules:

- Lead each page with a one-sentence purpose statement.
- Copy **exact** code snippets from the source. Do not paraphrase API signatures.
- For every prose claim about behavior, cite the file path in the source tree (comment or inline link).
- Prefer real input/output examples over descriptions of behavior.
- Never invent APIs. If something is unclear, write `TODO: verify` and move on.

### 4. Populate navigation

After all pages exist, write or update:

- Root `meta.json5` — pick the final order of top-level sections and any external header links.
- Each section's `meta.json5` — list pages in the order you want them to appear.

Keep auto-listing behavior (omit `pages`) only for drafty sections where the final ordering is not yet decided.

### 5. Add diagrams and screenshots where they help

- Put source assets in `<page-folder>/diagrams/<name>.mmd|svg|tsx`.
- Reference them with relative paths: `![Flow](./diagrams/flow.svg)`.
- Use the consecutive `-light` / `-dark` markdown image pattern for theme-aware embeds (Pagesmith auto-merges into `<picture>`).
- Do not hotlink external image hosts; images bundled with the docs survive deploys.
- For diagram authoring/rendering use diagramkit; see `prj-doc-site-add-diagram.md`.

### 6. Validate

```bash
npx pagesmith-docs build
```

Fix every schema error (missing `description`, invalid `pages` entry, broken link) before moving on.

```bash
npx pagesmith-docs dev
```

Walk through each new page manually:
- Sidebar placement is right.
- TOC mirrors the page headings.
- Internal links resolve.
- Code blocks render with the correct language.
- Search returns sensible results for the first page's title.

### 7. Wire docs scripts and CI

If not present already:

```json
{
  "scripts": {
    "docs:dev": "pagesmith-docs dev",
    "docs:build": "pagesmith-docs build",
    "docs:preview": "pagesmith-docs preview"
  }
}
```

If the user also wants GitHub Pages deployment, see `pagesmith-deploy-gh-pages.md`.

## Page templates

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

### Quickstart (`docs/guide/quickstart/README.md`)

````md
---
title: Quickstart
description: Get up and running with <Project> in under 5 minutes.
order: 1
---

# Quickstart

## Install

```bash
npm add <package>
```

## Run

```bash
npx <command>
```

## Verify

```bash
<verification command>
```

## Next steps

- [Concept overview](../concepts/README.md)
- [How-to recipes](../how-to/README.md)
````

### Concept page (`docs/guide/concepts/<concept>/README.md`)

````md
---
title: <Concept>
description: <what it is, why it matters>
order: <n>
---

# <Concept>

## What it is

<one paragraph>

## Why it exists

<one paragraph>

## Example

```ts
<real code from the source tree>
```

## Related

- [Related concept](../<other>/README.md)
- [How-to recipe](../../how-to/<task>/README.md)
````

### How-to (`docs/guide/how-to/<task>/README.md`)

```md
---
title: <Task>
description: Step-by-step recipe for <task>.
---

# <Task>

## When to use this

<one sentence>

## Steps

1. ...
2. ...
3. ...

## Verify

<how to confirm it worked>

## Gotchas

- <non-obvious pitfall>
```

### Reference page (`docs/reference/api/<surface>/README.md`)

````md
---
title: <Public API surface>
description: Reference for <API surface>.
---

# <Public API surface>

## Import

```ts
import { <X> } from '<package>'
```

## Signature

```ts
<type signature>
```

## Parameters

| Name | Type | Required | Description |
| ---- | ---- | -------- | ----------- |

## Returns

<description>

## Example

```ts
<minimal working example>
```

## Errors

| Error | Cause | Fix |
| ----- | ----- | --- |
````

## Gotchas

- Do not copy README content blindly — READMEs tend to mix promotion with reference. Split: promotion → home, reference → `reference/`, narrative → `guide/`.
- Respect `draft: true` on anything you are unsure about. Better to hide a half-written page than ship wrong docs.
- API reference pages must match the public `exports` in `package.json` exactly. Do not document internal modules.
- Keep navigation shallow — three levels deep is the practical limit (`guide/concepts/auth/README.md`, not `guide/concepts/auth/deep/dive/README.md`).
- Always run `pagesmith-docs build` at the end. A dev server can mask broken schema or missing pages that fail production builds.
