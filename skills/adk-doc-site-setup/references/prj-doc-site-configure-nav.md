---
name: prj-doc-site-configure-nav
description: Configure sidebar, top-nav, section ordering, grouping, and page visibility in this repo's @pagesmith/docs site using meta.json5 files and frontmatter. Use to reorder, hide, rename, group, pin, or add external links to docs navigation, or when a page is missing from the sidebar. Reads node_modules/@pagesmith/docs/skills/pagesmith-docs-configure-nav/SKILL.md when present, falls back to the inline guidance below otherwise.
---

# Project: Configure Doc-Site Navigation

## Read the source skill (locally installed first, fallback to inline)

1. **Try first**: `node_modules/@pagesmith/docs/skills/pagesmith-docs-configure-nav/SKILL.md`
   - Plus `node_modules/@pagesmith/docs/schemas/docs-root-meta.schema.json`
   - Plus `node_modules/@pagesmith/docs/schemas/docs-section-meta.schema.json`
   - Plus `node_modules/@pagesmith/docs/REFERENCE.md`
2. **Fallback (inline below)**: only when `@pagesmith/docs` is not installed.

When the locally installed files exist, **they win over this inline body** on any conflict.

## When to use

- A page is missing from the sidebar even though the markdown file exists.
- The sidebar order needs to change.
- A section needs renaming, hiding, collapsing, or pinning to the top.
- An external link should appear in the sidebar or top nav.
- A series (grouped reading order) needs to be created or rearranged.

## When NOT to use

- A new page needs to be authored → `prj-doc-site-add-page` first, then come back here.
- The whole docs structure is being redesigned → `prj-doc-site-generate-content` (re-architect) or `prj-doc-site-setup` (rescaffold).

## Workflow

1. **Identify the level** — is the change at the site root (top-level sections + header) or inside a section (sidebar group)?
2. **Edit the right `meta.json5`**:
   - Root: `<contentDir>/meta.json5`
   - Section: `<contentDir>/<section>/meta.json5`
3. **Validate**:
   ```bash
   npx pagesmith-docs dev      # meta.json5 hot-reloads
   npx pagesmith-docs build    # surfaces invalid pages entries / broken slugs
   ```
4. **Report** — files changed, before/after sidebar layout, validation result.

## Inline fallback

### How Pagesmith resolves navigation

For each folder under `contentDir`:

1. Read `meta.json5` (if present): `title`, `order`, `collapsed`, `pages`, `header`, `sections`.
2. For each page file, read `title`, `description`, `order`, `draft` from frontmatter.
3. Folders without `meta.json5` fall back to:
   - Title derived from the folder name (`getting-started` → "Getting Started").
   - Order = alphabetical.
   - Pages = all markdown files in the folder (sorted by `order` then title).

### Root `meta.json5`

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

- `sections` — ordered list of folder slugs in the sidebar. Omit a section to hide it.
- `header` — top-nav items. `path` for internal routes (honors `basePath`); `href` for absolute URLs.

### Section `meta.json5`

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

#### `pages` entry shapes

| Shape                                        | Meaning                                            |
| -------------------------------------------- | -------------------------------------------------- |
| `'install'`                                  | Render `<section>/install.md` using its own title. |
| `{ path: 'install' }`                        | Same as above; explicit form.                      |
| `{ path: 'install', title: 'Installation' }` | Override the sidebar label only.                   |
| `{ label: 'X', href: 'https://…' }`          | External link in the sidebar.                      |

#### Behavior

- Omit `pages` entirely → include every file in the folder, ordered by frontmatter `order` then title.
- Include a `pages` array → order is **authoritative**; files not listed are still served by URL but hidden in the sidebar.
- `order` at the section level determines sibling section order.
- `collapsed: true` starts the group collapsed.

### Series (grouped reading order)

```json5
{
  title: "Concepts",
  series: [
    { title: "Authentication", pages: ["sessions", "jwt", "oauth"] },
    { title: "Storage", pages: ["sqlite", "postgres"] },
  ],
}
```

Pages not referenced by a series stay visible under the automatic `Miscellaneous` group.

### Page-level knobs (frontmatter)

```md
---
title: Your First Page
description: ...
order: 2
draft: true
---
```

- `order` — lower values come first inside the parent section.
- `draft: true` — visible in `dev`, excluded from `build`. Don't link from non-drafts.

## Common tasks

### Pin a page to the top

```md
---
title: Overview
order: 0
---
```

### Hide from sidebar but keep reachable

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
3. Update each section's `meta.json5`.
4. Update the root `meta.json5` `sections` to control top-level order.
5. Run `npx pagesmith-docs build` to catch dangling links.

## Gotchas

- `pages` entries must match file names without extension. Mismatches **silently drop** the entry.
- Nested folder slugs need a path segment: `pages: ['advanced/caching']`.
- `path` in section/root metas is resolved against `basePath`; do not prefix it yourself.
- Top-level `header` items do not inherit from the sidebar. Define them explicitly.
- Root `meta.json5` `sections` controls both order **and presence**.
- Keep onboarding pages first in manual section ordering.

## Anti-patterns

- Listing every section file in `pages` "for safety" — locks ordering and creates merge friction. Use `pages` only when order matters.
- Creating multiple ways for the same page to appear in the sidebar (frontmatter `order` + `pages` array). Pick one.
- Renaming files instead of overriding `title` in `meta.json5` — breaks bookmarks and inbound links.
