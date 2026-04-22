---
title: 'doc-site-setup'
description: '|'
skill_name: doc-site-setup
category: task
---
# doc-site-setup — bootstrap pagesmith docs in a project

This is a thin wrapper. It does NOT re-implement pagesmith — it INSTALLS pagesmith (which ships its own skills) and delegates ongoing work to those skills.

## When to use

- Brand-new repo with no docs site.
- Existing repo where docs are markdown in `docs/` but no rendering pipeline.
- User says "set up Pagesmith", "add docs", "build a doc site".

## When NOT to use

- The repo already has `pagesmith.config.json5`. Use `pagesmith-docs-add-page` (or other `pagesmith-docs-*`) directly.
- Non-pagesmith setup (Docusaurus, MkDocs, etc.) — out of scope.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<project-name>` | optional | Defaults to `package.json` `name` |
| `<base-path>` | optional | For GitHub Pages: `/<repo-name>` |
| `<deploy>` | optional | `gh-pages` (default) / `none` |
| `--auto` | optional | Pick documented defaults |

## Workflow

1. **Phase 1 validator.** macOS / Linux. Node 24+. `package.json` exists.
2. **Install pagesmith.** `npm add @pagesmith/docs` (and `npm add -D diagramkit` if diagrams will be authored).
3. **Read `node_modules/@pagesmith/docs/REFERENCE.md`** for version-matched truth (mandatory — overrides anything in this skill if disagreement).
4. **Run `npx pagesmith-docs init --yes --ai`** (the `--ai` writes per-agent memory files). Or non-`--auto`: prompt user for project name / title / base-path / content-dir / search / AI integrations.
5. **Verify scaffold.** `pagesmith.config.json5` present; `docs/` populated; `package.json` has `docs:dev/build/preview` scripts.
6. **`docs:build` smoke test.** `npm run docs:build` must exit 0.
7. **`docs:dev` smoke test.** Start the dev server on a free port; curl `/` and `/guide/getting-started/`; both must be 200.
8. **(Optional) GitHub Pages.** If `<deploy>` = `gh-pages`, hand off to `pagesmith-docs-deploy-gh-pages` (in pagesmith pack).
9. **(Optional) Diagrams.** If user wants diagrams in docs, hand off to `@adk:doc-site-diagrams`.
10. **Install pagesmith skill pack into project.** `npx pagesmith-core skills` (this copies pagesmith's own skills into the consumer's `.claude/skills/` and `.cursor/skills/`).
11. **Phase 4 validator. Report.**

## Mode

`auto` only.

## Output

- `pagesmith.config.json5` at repo root
- `docs/` scaffold (README, guide/, reference/, with seed pages)
- `gh-pages/` build output (gitignored)
- `package.json` updated (scripts + deps)
- `.github/workflows/gh-pages.yml` if deploy chosen
- `.claude/skills/pagesmith-docs-*` — pagesmith's own skills installed

## Anti-patterns

- Re-implementing pagesmith's commands here. ALWAYS delegate via `npx pagesmith-docs ...`.
- Skipping the read of `node_modules/@pagesmith/docs/REFERENCE.md`.
- Globally installing pagesmith. Always `npx`.
- Setting `basePath` to a value that doesn't start with `/` or ends with `/`.
- Forgetting to add `gh-pages/` to `.gitignore`.

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Bootstrap flow + delegation map |
| `references/modes.md` | auto only |
| `references/persona.md` | The doc-site bootstrapper |
| `references/workflow.md` | Detailed steps |
| `references/clarifying-questions.md` | Project name, base-path, deploy choice |
| `references/output-format.md` | Final report |
| `references/artifact-format.md` | What gets created in the consumer repo |
| `references/validator.md` | Smoke tests for build / dev |
| `references/anti-patterns.md` | What NOT to do |
| `references/pagesmith-skill-pack.md` | List of pagesmith skills installed and what each does |
| `references/examples.md` | Sample first-run output |
| `references/interaction-contract.md` | Synced from canonical |
