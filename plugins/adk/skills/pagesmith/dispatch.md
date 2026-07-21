# pagesmith — flavor detection + task routing

Two decisions, in order: **which flavor** the site is, then **which task** you're doing → which installed skill to delegate to.

## Step 1 — detect the flavor (by the config file on disk)

| Config at repo root | Flavor | Packages | Deep skills live under |
|---|---|---|---|
| `pagesmith.config.json5` | **docs-preset** | `@pagesmith/docs` | `node_modules/@pagesmith/docs/skills/` |
| `site.config.json5` | **core-native** | `@pagesmith/site` (+ `@pagesmith/core`) | `node_modules/@pagesmith/{site,core}/skills/` |
| neither | **greenfield** | — | out of scope → `/adk:scaffold-pagesmith-docs` |

`--flavor docs|core` overrides detection. If both files somehow exist, the one the repo's build script actually consumes wins — check `package.json`.

## Step 2 — route the task → the installed skill to follow

Delegate by reading and following `node_modules/<pkg>/skills/<name>/SKILL.md`. Do not restate what those skills contain here — that is version-sensitive and lives in the install (`rules.md`).

| Task | Sub-flow | Flavor | Follow (installed skill) |
|---|---|---|---|
| Add / write a docs page, guide, reference, or seed a whole set | docs-content | docs-preset | `pagesmith-docs-add-page`, `pagesmith-generate-docs` |
| Sidebar / top-nav / section ordering | docs-nav | docs-preset | `pagesmith-docs-configure-nav` |
| Layout / footer / CSS / header / theme | docs-theme | docs-preset | `pagesmith-docs-customize-theme` |
| Full-text search (Pagefind / Cmd-K) | docs-search | docs-preset | `pagesmith-docs-add-search` |
| Publish to GitHub Pages | docs-deploy | docs-preset | `pagesmith-docs-deploy-gh-pages` |
| Add a content collection / a content loader | core-content | core-native | `pagesmith-core-add-collection`, `pagesmith-core-add-loader` |
| Restyle / theme a core-native site; apply a preset | core-theme | core-native | `pagesmith-site-customize-theme`, `pagesmith-site-use-preset` |
| **Develop the packages** — a loader, a remark/rehype markdown plugin, a validator, a new preset | package-dev | monorepo | `pagesmith-core-add-loader`, `pagesmith-core-customize-markdown`, `pagesmith-core-write-validator`, `pagesmith-site-use-preset` |
| Author page prose (markdown body) | content | either | the flavor's add-page / add-collection skill above |
| Create / re-render / fix diagrams | → `/adk:diagramkit` | — | (route out) |
| Scaffold a brand-new site (no config yet) | → `/adk:scaffold-pagesmith-docs` | — | (route out) |

Routing is by data, not vibes. When several rows match, the strongest discriminator wins: **an explicit deploy ask > a config/nav/theme/search change > content authoring**. If the site has no config at all, greenfield wins over everything and you route out.

## Materialize the skills before you follow them

The installed skills are the source of truth, so make sure they're present in the consumer:

```bash
npx pagesmith skills install      # @pagesmith/* (bin follows the install: pagesmith-docs / pagesmith-core)
npx diagramkit skills install     # for diagram work handed to /adk:diagramkit
```

Fallback when the `skills install` subcommand isn't available yet: follow `node_modules/<pkg>/skills/<pkg>-setup/SKILL.md`.

## Sibling skills (route out, don't reimplement)

- **`/adk:diagramkit`** — anything diagram: authoring, re-rendering, contrast/health checks. Pagesmith embeds the SVGs; diagramkit produces them.
- **`/adk:scaffold-pagesmith-docs`** — greenfield: create the config, wire the workflow, seed the skeleton. Once a site exists, come back here.
- **`/adk:document`** — a standalone document (ADR, RCA, migration guide) as prose. This skill writes *site pages* that fit the site; `/adk:document` drafts freestanding markdown.

## When the classifier is wrong

If the picked flavor or sub-flow doesn't fit — a `pagesmith.config.json5` that's actually a diagramkit config, a "docs" ask against a core-native site — say so in Phase 1 ("this reads like a core-native site, not a docs preset; confirm or correct?") and proceed on the corrected route. Don't silently force a bad fit, and don't guess a schema you couldn't read from the install.
