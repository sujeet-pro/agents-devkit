# ADK — Agent Onboarding Reference

This file is meant for **coding agents** (Claude Code, Cursor, Codex CLI, Codex Desktop, Claude Desktop, Antigravity, Junie, Gemini CLI, etc.) after `agents-devkit` has been installed into a host (`$HOME` or a project). Read this once, then route user requests into the installed skills.

## What you just got

ADK ships a catalog of self-contained `adk-*` skills covering planning, research, implementation, review, documentation, audits, publishing, visualization, and frontend work. Every skill is a single folder with:

- `SKILL.md` — YAML frontmatter (`name`, `description`, optional `compatibility` / `metadata` / `license` / `allowed-tools`) plus a thin orchestration body.
- `references/` — flat list of supporting files (`persona.md`, `workflow.md`, `output-format.md`, `constitution.md`, `working-artifacts.md`, `research-protocol.md`, `review-comment-format.md`, `brainstorming-workflow.md`, `mcp-fallback.md`, `anti-patterns.md`, `examples.md`). No `_shared/`. No subdirs. The skill is fully self-contained.

Each skill is independently copy-able; nothing it needs lives outside its own folder.

## Where things live after install

`adk-install` lands files under the install root (`$HOME` for global, `<project>` for project mode):

| Surface | Path |
| --- | --- |
| Skills hub (single source of truth) | `<root>/.agents/skills/<name>` |
| Claude Code mirror | `<root>/.claude/skills/<name>` (symlink to hub) |
| Cursor mirror | `<root>/.cursor/skills/<name>` (symlink) |
| Codex CLI mirror | `<root>/.codex/skills/<name>` (symlink) |
| Antigravity / Junie mirror | `<root>/.antigravity/skills/<name>`, `<root>/.junie/skills/<name>` |
| Claude custom subagents | `<root>/.claude/agents/<name>.md` (symlink to package `agents-claude/`) |
| Cursor custom subagents | `<root>/.cursor/agents/<name>.md` (symlink to package `agents-cursor/`) |
| Codex custom agents | `<root>/.codex/agents/<name>.toml` (symlink to package `agents-codex/`) |
| Hooks | `<root>/.<runtime>/{settings,hooks}.json` (symlink) |
| MCP config | `<root>/.<runtime>/mcp.json` (merged) |
| Memory file managed block | `<root>/.<runtime>/<MEMORY>.md` between `<!-- adk:global-prompts:start/end -->` |
| User config | `~/.config/adk/settings.json5` |
| Project config | `<project>/.adk/settings.json5` (project mode only) |

Raw package source lives at `node_modules/agents-devkit/` (npm install) or the cloned repo root (clone install).

## When to activate which skill

Activate the top-level router first if intent is non-trivial:

| User intent | Router | Task skill |
| --- | --- | --- |
| Any non-trivial request | `adk` | (router picks) |
| Decide between options, close ambiguity | `adk-plan` | `adk-plan-brainstorm` |
| Verify framework / library behavior | `adk-plan` | `adk-plan-research` |
| Write a spec / PRD | `adk-plan` | `adk-plan-spec` |
| Write architectural design | `adk-plan` | `adk-plan-design` |
| Draft an implementation roadmap | `adk-plan` | `adk-plan-roadmap` |
| Add a feature or fix a bug | `adk-build` | `adk-build-feature` |
| Restructure code with no behavior change | `adk-build` | `adk-build-refactor` |
| Migrate framework / runtime | `adk-build` | `adk-build-migrate` |
| Author or expand tests | `adk-build` | `adk-build-test` |
| Manage dependencies | `adk-build` | `adk-build-deps` |
| Review a PR | `adk-review` | `adk-review-pr` |
| Self-review local changes | `adk-review` | `adk-review-local` |
| Address review feedback | `adk-review` | `adk-review-feedback` |
| Capture a session handoff | `adk-review` | `adk-review-handoff` |
| Author docs | `adk-docs` | `adk-docs-write` |
| Review docs | `adk-docs` | `adk-docs-review` |
| Audit a repository | `adk-audit` | `adk-audit-repo` |
| Audit a public site | `adk-audit` | `adk-audit-site` |
| Draft a commit message | `adk-publish` | `adk-publish-commit` |
| Open a PR or push to GitHub | `adk-publish` | `adk-publish-github` |
| Push to Bitbucket | `adk-publish` | `adk-publish-bitbucket` |
| Publish to Confluence | `adk-publish` | `adk-publish-confluence` |
| Publish to Google Drive | `adk-publish` | `adk-publish-gdrive` |
| Make a diagram | `adk-visualize` | `adk-visualize-diagram` |
| Make a chart | `adk-visualize` | `adk-visualize-chart` |
| UI / UX design | `adk-frontend` | `adk-frontend-design` |
| Frontend feature work | `adk-frontend` | `adk-frontend-feature` |
| Build a React 19 client-side sample | `adk-frontend` | `adk-frontend-react-csr` |

Each skill's own `SKILL.md` carries the authoritative "When to use" / "When NOT to use"; prefer it when this table conflicts.

## How to activate

1. **File-read activation** — read the matching `SKILL.md`. Then read each file in `references/` listed in the managed block at the bottom.
2. **Skill-tool activation** — if the runtime has a dedicated skill-activation tool, call it with the skill name.

After activation, resolve any `references/<file>` paths relative to the skill's directory.

## Working artifact contract

Every skill writes intermediate output under `.temp/` in the host repo:

- `.temp/plans/<slug>.md`
- `.temp/drafts/<slug>.md`
- `.temp/reports/<slug>.md`
- `.temp/reference-repos/<owner>__<repo>/`
- `.temp/notes/<slug>.md`

Never write scratch content elsewhere. `.temp/` must be gitignored — `adk-install` warns if it isn't.

## Philosophy (short form)

- Plan first, then implement.
- Prefer primary sources over memory.
- Self-contained skills with inline references.
- Concise, decision-oriented output.
- Parallel subagents for non-trivial review, research, and testing.
- Working artifacts only in `.temp/`.

## Help

- Public docs: built into `gh-pages/` from `docs/`.
- Skill catalog: `skills-manifest.json` (regenerated via `npm run skills:manifest`).
- Validation: `npm run validate`.
