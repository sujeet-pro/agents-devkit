---
name: prj-docs
description: Generate and maintain this marketplace's Pagesmith documentation. Use when updating docs/, regenerating reference pages, adding Pagesmith navigation meta, polishing the home page, or documenting marketplace plugins, skills, agents, MCP servers, and helper binaries.
---

# Project Docs

Use this project skill for documentation work in this repository. The site is built with `@pagesmith/docs`; the installed package is the source of truth.

## Read First

Before editing docs, read the locally installed Pagesmith references that match this repo's dependency version:

- `node_modules/@pagesmith/docs/REFERENCE.md`
- `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/references/docs-guidelines.md`
- `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/references/markdown-guidelines.md`
- `node_modules/@pagesmith/docs/schemas/pagesmith-config.schema.json`
- `node_modules/@pagesmith/docs/schemas/docs-root-meta.schema.json`
- `node_modules/@pagesmith/docs/schemas/docs-section-meta.schema.json`
- `node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json`
- `node_modules/@pagesmith/docs/schemas/docs-home-frontmatter.schema.json`

Use `/Users/sujeet/personal/agents-devkit/docs` as the setup/style reference for home-page frontmatter, guide/reference organization, and `series`-based grouping.

## Upstream Pagesmith Skills

When a task maps to one of these workflows, read and follow the matching upstream skill:

- `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/SKILL.md` for bootstrap, retrofit, package scripts, config, and AI pointers.
- `node_modules/@pagesmith/docs/skills/pagesmith-generate-docs/SKILL.md` for generating a complete docs set from real repo artifacts.
- `node_modules/@pagesmith/docs/skills/pagesmith-docs-add-page/SKILL.md` for new guide, reference, or home pages.
- `node_modules/@pagesmith/docs/skills/pagesmith-docs-configure-nav/SKILL.md` for `meta.json5`, ordering, grouping, sidebar, and header/footer navigation.
- `node_modules/@pagesmith/docs/skills/pagesmith-docs-add-search/SKILL.md` for Pagefind search setup and troubleshooting.
- `node_modules/@pagesmith/docs/skills/pagesmith-docs-customize-theme/SKILL.md` for layout, component, CSS variable, footer, and theme overrides.
- `node_modules/@pagesmith/docs/skills/pagesmith-docs-deploy-gh-pages/SKILL.md` for GitHub Pages deployment, `origin`, `basePath`, and workflow changes.

## Pagesmith Feature Surface To Use

Prefer stock `@pagesmith/docs` features before custom code:

- Home page frontmatter: `layout: home`, `tagline`, `actions`, `install`, `features`, `packages`, and `codeExample`.
- Docs organization: top-level `guide/` and `reference/`, folder-based pages, section landing pages, and `meta.json5` with `displayName`, `items`, `orderBy`, `collapsed`, and `series`.
- Markdown: GFM tables/task lists/footnotes, GitHub alerts, math, smart typography, heading anchors, external-link handling, local image publishing, light/dark image pairs, inline SVG assets, and code tabs.
- Code blocks: language identifiers, `title`, `showLineNumbers`, `startLineNumber`, `mark`, `ins`, `del`, `collapse`, `wrap`, `frame`, copy buttons, and dual Shiki themes.
- Search and runtime chrome: built-in Pagefind, `data-pagefind-body`, `data-ps-search-trigger`, theme controls, sidebar, TOC, breadcrumbs, prev/next links, edit links, and footer links.
- Theme customization: config-level theme keys first, CSS custom properties second, `theme.layouts` only when needed.
- Deployment: GitHub Pages-compatible `origin`, `basePath`, `outDir: "gh-pages"`, `.nojekyll`, `404.html`, sitemap, and `pagesmith-docs preview`.
- Validation and MCP: `npx pagesmith-docs build`, `npx pagesmith-docs validate`, and `pagesmith-docs mcp --stdio` when docs-aware inspection helps.

## Marketplace Docs Rules

For this repository:

1. Keep `pagesmith.config.json5` at the repo root and content in `docs/`.
2. Run `npm run docs:reference` after changing plugin manifests, skills, agents, MCP config, or helper binaries.
3. Generated reference pages must stay grouped by plugin/type. Use group slugs like `core-skills`, `code-agents`, `review-mcp`, `docs-plugins`, and `investigate-skills`.
4. Keep reference navigation metadata in `meta.json5` files and use `series` for the plugin/type groups.
5. Keep concepts inside the Guide section as a `Concepts` series rather than a separate top-level section.
6. The home page should present exactly six high-signal feature cards for the marketplace and docs experience.
7. Do not hand-edit generated reference pages when the generator can express the change. Update `scripts/generate-reference-docs.mjs`, then regenerate.
8. Validate with `npm run docs:build` when possible. If build cannot run, report why and list what remains unverified.
