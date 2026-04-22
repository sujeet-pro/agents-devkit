# Pagesmith Add-Page Reference (fallback)

> Inline fallback for adding a page to a `@pagesmith/docs` site. When the package is installed, prefer:
> - `node_modules/@pagesmith/docs/skills/pagesmith-docs-add-page/SKILL.md`
> - `node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json`
> - `node_modules/@pagesmith/docs/schemas/docs-home-frontmatter.schema.json`
> - `node_modules/@pagesmith/docs/REFERENCE.md`

## Where pages live

Pagesmith reads `contentDir` from `pagesmith.config.json5`. Typical layouts:

| Page                | File                                    | URL                      |
| ------------------- | --------------------------------------- | ------------------------ |
| Home                | `<contentDir>/README.md`                | `/`                      |
| Top-level guide     | `<contentDir>/guide/<slug>.md`          | `/guide/<slug>`          |
| Top-level reference | `<contentDir>/reference/<slug>.md`      | `/reference/<slug>`      |
| Series page         | `<contentDir>/guide/<series>/<slug>.md` | `/guide/<series>/<slug>` |
| Section landing     | `<contentDir>/guide/<series>/README.md` | `/guide/<series>`        |

The URL is always slashless — both `/guide/install` and `/guide/install/` resolve. Do not hand-append `.html` or trailing slashes to links.

For doc-site projects, **prefer folder-based pages** (`<section>/<slug>/README.md`) so each page can own its `diagrams/` and asset folder.

## Minimal page template

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

Required frontmatter: `title`, `description`. Optional: `order`, `draft`, `tags`, `lastUpdatedOn`, `navLabel`, `sidebarLabel`, `$schema`.

The `$schema` path is **relative to the markdown file** so editors can auto-complete frontmatter. For a page at `<content>/guide/install/README.md` the path is `../../node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json`.

## Frontmatter — full reference

| Field          | Type      | Description                        |
| -------------- | --------- | ---------------------------------- |
| `title`        | `string`  | Page title (sidebar + browser tab) |
| `description`  | `string`  | Meta description for SEO           |
| `navLabel`     | `string`  | Override top navigation label      |
| `sidebarLabel` | `string`  | Override sidebar label             |
| `order`        | `number`  | Manual sort order within section   |
| `draft`        | `boolean` | Exclude from production build      |
| `tags`         | `array`   | Tags for filtering                 |
| `lastUpdatedOn`| `string`  | ISO date for last-updated badge    |

## Home page (`<contentDir>/README.md`)

The home page accepts extra `DocHome` frontmatter fields:

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
packages:
  - name: my-pkg
    description: Core package
    href: /reference/api/my-pkg
    tag: stable
codeExample:
  label: Quickstart
  title: hello.ts
  code: |
    import { hello } from "my-pkg"
    hello()
---

# My Docs

Optional markdown body below the hero.
```

If a home frontmatter field is missing (for example `description`), Pagesmith fails the build with a schema error. Fill all required fields.

`DocHome` field summary:

| Field         | Type     | Description                                        |
| ------------- | -------- | -------------------------------------------------- |
| `layout`      | `string` | `DocHome` for the home layout                      |
| `tagline`     | `string` | Short description below title                      |
| `install`     | `string` | Install command snippet                            |
| `actions`     | `array`  | CTA buttons (`{ label, href, theme: 'brand' }`)    |
| `features`    | `array`  | Feature cards (`{ icon, title, description }`)     |
| `packages`    | `array`  | Package cards (`{ name, description, href, tag }`) |
| `codeExample` | `object` | Code example (`{ label, title, code }`)            |

## Section landing pages

Each section can have a custom landing page at `<section>/README.md`. If absent, Pagesmith auto-generates a listing page enumerating the section's children — this is a feature, not a bug. Override only when you want a tailored intro.

## Drafts

```md
---
title: Work in progress
description: ...
draft: true
---
```

Draft pages:
- Render in `pagesmith-docs dev` (so you can preview).
- Are **excluded** from `build` output.
- Don't link to a draft page from another page's body.

## Verify a new page

1. `npx pagesmith-docs dev` — page must appear at the expected URL and in the sidebar.
2. `npx pagesmith-docs build` — must exit 0. Schema errors surface here.
3. Run `pagesmith-docs build` again after committing to make sure draft pages behave as expected.

## Sidebar visibility

For a brand-new page to show up in the sidebar:

1. Place it in the correct section folder.
2. Confirm the section's `meta.json5` either:
   - lists it explicitly in `pages`, or
   - omits `pages` entirely (Pagesmith auto-picks up new files).
3. Set `order` on the frontmatter (lower shows first) when you want a specific position.

If the section's `meta.json5` has a `pages` array, you **must** add the new slug explicitly — the array is authoritative. Otherwise the page is reachable by URL but hidden from navigation.

## Gotchas

- `title`/`description` must be strings. YAML's unquoted colons break parsing (`description: Use when: X` will fail). Quote the value or use a single string without a colon.
- `order` values are per-section, not global. Two sections can both have an `order: 1` page.
- The auto-generated listing page uses each child page's `title` and `description` — keep them short and self-contained.
- If a new page is missing from the sidebar, check the section's `meta.json5` `pages` array first (not the frontmatter).
- Relative image paths work: `![diagram](./diagrams/flow.svg)` resolves correctly for both dev and build.
- One `# h1` per page (validator enforces). Sequential heading depth (no skipping h2 → h4).
