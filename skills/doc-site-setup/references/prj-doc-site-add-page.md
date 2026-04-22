---
name: prj-doc-site-add-page
description: Add or update a single documentation page in this repo's @pagesmith/docs site, with the right frontmatter, file placement, sidebar slot, and optional drafts/series wiring. Reads node_modules/@pagesmith/docs/skills/pagesmith-docs-add-page/SKILL.md when present, falls back to the inline guidance below otherwise.
---

# Project: Add a Doc-Site Page

## Read the source skill (locally installed first, fallback to inline)

1. **Try first**: `node_modules/@pagesmith/docs/skills/pagesmith-docs-add-page/SKILL.md`
   - Plus `node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json`
   - Plus `node_modules/@pagesmith/docs/schemas/docs-home-frontmatter.schema.json`
   - Plus `node_modules/@pagesmith/docs/schemas/docs-section-meta.schema.json`
   - Plus `node_modules/@pagesmith/docs/REFERENCE.md`
2. **Fallback (inline below)**: only when `@pagesmith/docs` is not installed.

When the locally installed files exist, **they win over this inline body** on any conflict.

## When to use

- A new `<contentDir>/<section>/<slug>/README.md` (or top-level page) is needed.
- An existing page must be updated to match new code / config.
- A page must be marked `draft: true` (visible in dev, excluded from build).
- A page needs to be promoted from draft to published.

## When NOT to use

- Generating many pages at once → `prj-doc-site-generate-content`.
- Reordering the sidebar / changing nav structure only → `prj-doc-site-configure-nav`.
- Adding a diagram inside a page → `prj-doc-site-add-diagram` (then come back here to wire the embed).

## Workflow

1. **Decide location** — `<contentDir>/<section>/<slug>/README.md` (folder-based, preferred) or `<contentDir>/<section>/<slug>.md` (file-based).
2. **Pick the template** — home, quickstart, concept, how-to, or reference (templates below).
3. **Write the page** — required frontmatter (`title`, `description`), optional `order`, `draft`, etc.
4. **Wire navigation** — confirm the section's `meta.json5` either includes the new slug in `pages` or omits `pages` entirely (auto-pickup).
5. **Validate**:
   ```bash
   npx pagesmith-docs dev      # check sidebar + URL
   npx pagesmith-docs build    # must exit 0
   ```
6. **Report** — file path, frontmatter summary, sidebar location.

## Inline fallback

### Where pages live

Pagesmith reads `contentDir` from `pagesmith.config.json5`. Typical layouts:

| Page                | File                                       | URL                      |
| ------------------- | ------------------------------------------ | ------------------------ |
| Home                | `<contentDir>/README.md`                   | `/`                      |
| Top-level guide     | `<contentDir>/guide/<slug>.md`             | `/guide/<slug>`          |
| Top-level reference | `<contentDir>/reference/<slug>.md`         | `/reference/<slug>`      |
| Series page         | `<contentDir>/guide/<series>/<slug>.md`    | `/guide/<series>/<slug>` |
| Folder-based page   | `<contentDir>/guide/<slug>/README.md`      | `/guide/<slug>`          |
| Section landing     | `<contentDir>/guide/<series>/README.md`    | `/guide/<series>`        |

The URL is always slashless. Folder-based pages are recommended so each page can own its `diagrams/` and asset folder.

### Minimal page template

```md
---
$schema: ../../node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json
title: Install
description: Get the project running locally in under a minute.
order: 1
---

# Install

Short intro sentence.

## Prerequisites

- Node.js 24+.

## Steps

1. ...
```

Required: `title`, `description`. Optional: `order`, `draft`, `tags`, `lastUpdatedOn`, `navLabel`, `sidebarLabel`, `$schema`.

### Home page (extra `DocHome` frontmatter)

```md
---
$schema: ../node_modules/@pagesmith/docs/schemas/docs-home-frontmatter.schema.json
title: My Docs
description: Short blurb used for SEO.
hero:
  title: My Project
  tagline: Short value prop.
  actions:
    - label: Quickstart
      href: /guide/quickstart
    - label: GitHub
      href: https://github.com/<owner>/<repo>
features:
  - title: Fast
    description: ...
  - title: Typed
    description: ...
---

# My Docs

Optional markdown body below the hero.
```

### Concept page

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
````

### How-to page

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

## Verify

<how to confirm it worked>

## Gotchas

- <non-obvious pitfall>
```

### Reference page

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
````

### Drafts

```md
---
title: Work in progress
description: ...
draft: true
---
```

Draft pages render in `pagesmith-docs dev` but are **excluded** from `build`. Don't link to a draft from a non-draft page.

### Sidebar visibility

For a new page to appear in the sidebar:

1. Place it in the correct section folder.
2. The section's `meta.json5` either:
   - lists it explicitly in `pages`, or
   - omits `pages` entirely (Pagesmith auto-picks up new files).
3. Set `order` on the frontmatter (lower shows first) when you want a specific position.

If the section's `meta.json5` has a `pages` array, you **must** add the new slug explicitly — the array is authoritative.

## Gotchas

- `title` / `description` must be strings. YAML's unquoted colons break parsing — quote the value.
- One `# h1` per page (validator enforces).
- Sequential heading depth (no skipping h2 → h4).
- `order` values are per-section, not global.
- Relative image paths work: `![diagram](./diagrams/flow.svg)`.

## Anti-patterns

- Documenting wished-for behavior. Read the code first.
- Duplicating README content into the docs site verbatim — split: home for promotion, `reference/` for API, `guide/` for narrative.
- Forgetting `description` — schema-required, build fails without it.
- Linking to `draft: true` pages from non-draft pages.
