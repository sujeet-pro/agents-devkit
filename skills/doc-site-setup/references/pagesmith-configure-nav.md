# Pagesmith Configure-Nav Reference (fallback)

> Inline fallback for sidebar / top-nav / section ordering in a `@pagesmith/docs` site. When the package is installed, prefer:
> - `node_modules/@pagesmith/docs/skills/pagesmith-docs-configure-nav/SKILL.md`
> - `node_modules/@pagesmith/docs/schemas/docs-root-meta.schema.json`
> - `node_modules/@pagesmith/docs/schemas/docs-section-meta.schema.json`
> - `node_modules/@pagesmith/docs/REFERENCE.md`

Pagesmith generates the whole nav tree from the filesystem plus two sources of declarative config:

- `meta.json5` files (one per section and one at the root).
- `title`, `order`, and `draft` in page frontmatter.

There is **no central `navigation.json`**. Edit the nearest `meta.json5` or the page itself.

## How Pagesmith resolves navigation

For each folder under `contentDir`:

1. Read `meta.json5` (if present): `title`, `order`, `collapsed`, `pages`, `header`, `sections`.
2. For each page file, read `title`, `description`, `order`, `draft` from frontmatter.
3. Folders without `meta.json5` fall back to:
   - Title derived from the folder name (`getting-started` → "Getting Started").
   - Order = alphabetical.
   - Pages = all markdown files in the folder (sorted by `order` then title).

## Root `meta.json5`

Lives at `<contentDir>/meta.json5`. Controls top-level nav:

```json5
{
  $schema: "./node_modules/@pagesmith/docs/schemas/docs-root-meta.schema.json",
  sections: ["guide", "reference"],
  header: [
    { label: "Guide", path: "/guide" },
    { label: "Reference", path: "/reference" },
    { label: "GitHub", href: "https://github.com/<owner>/<repo>" },
  ],
}
```

- `sections` — ordered list of folder slugs that appear in the sidebar. Omit a section to hide it from the generated nav.
- `header` — items in the top navigation bar. Use `path` for internal routes (honors `basePath`) and `href` for absolute URLs.

## Section `meta.json5`

Lives at `<contentDir>/<section>/meta.json5`. Controls the section's sidebar group:

```json5
{
  $schema: "../../node_modules/@pagesmith/docs/schemas/docs-section-meta.schema.json",
  title: "Getting Started",
  order: 1,
  collapsed: false,
  pages: [
    "install",
    "quickstart",
    { path: "first-page", title: "Your First Page" },
    { label: "Changelog", href: "https://github.com/.../releases" },
  ],
}
```

### `pages` entry shapes

| Shape                                        | Meaning                                            |
| -------------------------------------------- | -------------------------------------------------- |
| `'install'`                                  | Render `<section>/install.md` using its own title. |
| `{ path: 'install' }`                        | Same as above; explicit form.                      |
| `{ path: 'install', title: 'Installation' }` | Override the sidebar label only.                   |
| `{ label: 'X', href: 'https://…' }`          | External link in the sidebar.                      |

### Behavior

- Omit `pages` entirely to include every file in the folder, ordered by frontmatter `order` then title.
- Include a `pages` array to make order **authoritative** — files not listed are still served by URL but hidden in the sidebar.
- `order` at the section level determines sidebar group order across the sibling sections under the parent.
- `collapsed: true` starts the group collapsed.

## Series (grouped reading order within a section)

Use `meta.json5` `series` when a section needs guided reading order. Pages not referenced by a series still stay visible under the automatic `Miscellaneous` group:

```json5
{
  title: "Concepts",
  series: [
    {
      title: "Authentication",
      pages: ["sessions", "jwt", "oauth"],
    },
    {
      title: "Storage",
      pages: ["sqlite", "postgres"],
    },
  ],
}
```

## Page-level knobs (frontmatter)

```md
---
title: Your First Page
description: ...
order: 2
draft: true
---
```

- `order` — lower values come first inside the parent section.
- `draft: true` — visible in `dev`, excluded from `build`.

## Common tasks

### Pin a page to the top

```md
---
title: Overview
order: 0
---
```

### Hide from sidebar but keep reachable by URL

Either:
- Remove from the section's `pages` array (when `pages` is used), or
- Set `draft: true` (also hides from production build).

Pagesmith has no "unlisted" flag.

### External link in the sidebar

```json5
pages: [
  "install",
  "quickstart",
  { label: "API docs (external)", href: "https://api.example.com" },
]
```

### Rename without moving the file

Set `title` in the section's `meta.json5` entry. Do not rename the file — URLs would break.

### Reorganize sections entirely

1. Create the new folder under `contentDir`.
2. Move the markdown files.
3. Update each section's `meta.json5` (`title`, `order`, `pages`).
4. Update the root `meta.json5` `sections` to control top-level order.
5. Run `npx pagesmith-docs build` to catch dangling links.

## Verify

```bash
npx pagesmith-docs dev
```

`meta.json5` edits reload live — no restart needed. Always follow up with:

```bash
npx pagesmith-docs build
```

so the build surfaces missing slugs, invalid `pages` entries, or schema errors before deploy.

## Gotchas

- `pages` entries must match file names without extension. `install.md` maps to `'install'`. Mismatches **silently drop** the entry from the sidebar.
- Nested folder slugs need a path segment: `pages: ['advanced/caching']`, not `['caching']`.
- `path` in section/root metas is resolved against `basePath`; do not prefix it yourself.
- Top-level `header` items do not inherit from the sidebar. Define them explicitly if you want parity.
- Root `meta.json5` `sections` controls both order **and presence** — omit a section to hide it from the sidebar index.
- Keep onboarding pages first in manual section ordering before manual setup and deep dives.
