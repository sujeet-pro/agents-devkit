---
title: 'adk-doc-site-setup'
description: 'Bootstrap a documentation site in a project using @pagesmith/docs (content + nav + search + theme) and diagramkit (mermaid / graphviz / drawio / excalidraw rendering). Installs npm packages, writes config files, scaffolds the docs/ tree, wires npm scripts, and installs prj-doc-site-* skills so future agents can keep extending the site.'
skill_name: adk-doc-site-setup
category: standalone
---

# adk-doc-site-setup

Standalone task skill that turns any repo into a working documentation site backed by `@pagesmith/docs` (the docs framework) and `diagramkit` (the diagram rendering toolkit), then installs a set of `prj-doc-site-*` project-level skills so future agent sessions can keep extending the site without re-reading this skill.

## When to use

- The repo has no docs site yet and the user wants Pagesmith + diagramkit added.
- The repo has docs scattered in `README.md` / `docs/` but no build, search, or nav config.
- The user said "set up docs", "scaffold a docs site", "add Pagesmith", "bootstrap docs", or similar.
- The user wants the project's agents to be able to keep adding pages and diagrams without re-running this setup skill every time.

## When NOT to use

- The repo already has a working Pagesmith + diagramkit setup → use the installed `prj-doc-site-*` skills.
- The user wants to bootstrap AI scaffolding in general (`AGENTS.md`, `CLAUDE.md`, skill wrappers) → `adk-adopt-ai-in-repo`.

## What gets installed

- `@pagesmith/docs` and `diagramkit` (and optionally `sharp` for raster diagram output).
- Root config files: `pagesmith.config.json5` + `diagramkit.config.json5`.
- `docs/` tree with guide + reference groupings (`meta.json5` + `README.md` per section).
- npm scripts: `docs:dev`, `docs:build`, `docs:preview`.
- Project-level skills under `.agents/skills/prj-doc-site-*` (mirrored into Claude / Cursor / Codex skills folders) so future agents can add pages, generate content, configure nav, embed diagrams, and deploy.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<repo-path>` | optional | Default: current working directory |
| `--content-dir <path>` | optional | Default: `docs/` |
| `--base <path>` | optional | Default: `/` for user sites, `/<repo>/` for project sites |
| `--origin <url>` | optional | Used by deploy and metadata |
| `--skip-deploy` | optional | Skip GitHub Pages deploy wiring |
| `--auto` | optional | Skip approval gates |

## Workflow (high level)

1. **Confirm intent** — restate plan, packages, content-dir, base path, deploy yes/no. Approval gate unless `--auto`.
2. **Detect existing state** — check for existing `pagesmith.config.json5`, `diagramkit.config.json5`, `docs/`, etc.
3. **Install packages** (npm).
4. **Run `pagesmith-docs init`** to write `pagesmith.config.json5`.
5. **Run `diagramkit init` and `diagramkit warmup`** to write `diagramkit.config.json5`.
6. **Scaffold `docs/` tree** (guide + reference groupings).
7. **Wire `package.json` scripts** (docs:dev / docs:build / docs:preview).
8. **Install `prj-doc-site-*` skills** into the consumer project.
9. **Add a hello-world page + diagram** to confirm the rendering pipeline works.
10. **Validate the full setup** — run `docs:build`; confirm output renders; confirm diagrams export.
11. **Deploy (optional)** — wire GitHub Pages deploy if requested.
12. **Report** — what was installed, where, what skills were added, what to run next.

See the full skill at `skills/adk-doc-site-setup/SKILL.md` for the complete workflow + `prj-doc-site-*` catalog.
