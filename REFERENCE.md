# ADK — Agent Onboarding Reference

This file is meant for **coding agents** (Claude Code, Cursor, Codex CLI, Codex Desktop, Claude Desktop, Antigravity, Junie, Gemini CLI, etc.) after `agents-devkit` has been installed into a host (`$HOME` or a project). Read this once, then route user requests into the installed skills.

## What you just got

ADK ships a catalog of self-contained `adk-*` skills covering planning, research, implementation, review, documentation, audits, publishing, visualization, frontend work, and docs-site bootstrapping. Every skill is a single folder with:

- `SKILL.md` — YAML frontmatter (`name`, `description`, optional `compatibility` / `metadata` / `license` / `allowed-tools`) plus a thin orchestration body.
- `references/` — flat list of supporting files. **Filenames are task-prefixed** by the skill's task token (the suffix after `adk-`); the only exception is `interaction-contract.md`, which is the global propagated copy and keeps its generic name. Standard set on every skill: `<task>-persona.md`, `<task>-constitution.md` (or `<task>-standards.md` for review-style skills), `interaction-contract.md`, `<task>-clarifying-questions.md`, `<task>-output-format.md`, `<task>-artifact-format.md`, `<task>-anti-patterns.md`, `<task>-validator.md` (the four-phase gate the skill MUST run). Skills that need primary-source research add `<task>-research-protocol.md`; skills that consume cross-repo context add `<task>-multi-repo.md`. Some skills also keep `<task>-examples.md`, `<task>-mcp-fallback.md`. Review-style skills (`adk-review-pr`, `adk-docs-review`, `adk-audit-repo`, `adk-audit-site`) add `<task>-comment-format.md`, `<task>-reply-templates.md`, `<task>-comment-reconciliation.md`, `<task>-postback-protocol.md` for the bold-label posted-comment shape and reply protocols. Frontend skills add `<task>-design-system-master.md`, `<task>-pre-delivery-checklist.md`, `<task>-industry-anti-patterns.md`. No `_shared/`. No subdirs.

Each skill is independently copy-able; nothing it needs lives outside its own folder.

## Where things live after install

Files land under the install root. The install root and what gets installed depend on which path the user took (ordered from suggested to most minimal):

| Install scenario | Install root | Package lives at | Surfaces installed |
| --- | --- | --- | --- |
| Clone + install script — **suggested** (`git clone … && npm install && npm run setup`) | Either (`--mode global` or `--mode project`) | The clone path | Skills, custom subagents, hooks, MCP, global prompts |
| Global npm (`npm install -g agents-devkit`) | `$HOME` | `$(npm prefix -g)/lib/node_modules/agents-devkit` | Skills, custom subagents, hooks, MCP, global prompts |
| Per-project npm (`npm i --save-dev agents-devkit`) | `<project>` | `<project>/node_modules/agents-devkit` | Skills, custom subagents, hooks, MCP, global prompts |
| `npx skills add sujeet-pro/agents-devkit` (non-tech folks) | Whatever the [`skills`](https://skills.sh) loader supports for the active agent | (cached by loader) | **Skills only** — custom subagents, hooks, MCP server configs, and global prompts are NOT installed |

If a user took the `npx skills` path, do not assume hooks, MCP servers, or custom subagents exist. Skills' `mcp-fallback.md` instructions still apply (skills degrade gracefully when MCP servers are missing). If the user wants the full kit, point them at the clone or npm-module paths.

Once an install completes, files are arranged like this:

| Surface | Path under install root |
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

If a path you expected to find is missing, it usually means the user opted out of that surface during the interactive install. Re-run `adk-install` and tick the surface in the multiselect.

## Interaction contract (applies to every ADK skill)

Every installed skill has `references/interaction-contract.md`. The same contract is mirrored in the runtime's memory file via `global-prompts/interaction-contract.md`. Summary:

- **Default mode = ask.** At every meaningful decision, present 2-3 options with `Pros / Cons / Best when / Blast radius / Reversibility`, mark one option `(default)`, ask one question, wait. Trivial reversible actions are taken without asking.
- **`--auto` mode.** Skip approval gates, take the documented `(default)` at every fork, still validate, still report.
- **Always.** End with: result, decisions auto-picked, validation evidence, residual risk, offer of more depth.
- **Never auto.** Refuse irreversible destructive ops the skill marks "never auto" (`pr-merge`, force-push, prod deploy, schema drop, `rm -rf`, billing, account writes for other users) — even under `--auto`.

If a user request doesn't pass `--auto`, default to interactive. If it does, suppress the gates but still report.

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
| Review docs (Markdown OR Confluence with `--mode confluence`) | `adk-docs` | `adk-docs-review` |
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
| Bootstrap a docs site (`@pagesmith/docs` + `diagramkit`) in any repo | (no router) | `adk-doc-site-setup` |
| Bootstrap AI scaffolding (`ai-guidelines/`, `AGENTS.md`, `CLAUDE.md`, skill wrappers, hooks) in any repo | (no router) | `adk-adopt-ai-in-repo` |

Each skill's own `SKILL.md` carries the authoritative "When to use" / "When NOT to use"; prefer it when this table conflicts.

## How to activate

1. **File-read activation** — read the matching `SKILL.md`. Then read each file in `references/` listed in the managed block at the bottom. Filenames are task-prefixed (e.g., `pr-reviewer-persona.md`, `feature-validator.md`); only `interaction-contract.md` keeps its generic name. Read in this order so behavior is consistent: `<task>-persona.md` → `<task>-constitution.md` (or `<task>-standards.md`) → `interaction-contract.md` → `<task>-clarifying-questions.md` → `<task>-artifact-format.md` → `<task>-output-format.md` → (`<task>-research-protocol.md` if present) → (`<task>-multi-repo.md` if present) → any skill-specific file (examples, mcp-fallback, comment-format, reply-templates, postback-protocol, comment-reconciliation, design-system-master, pre-delivery-checklist, industry-anti-patterns, brainstorming-workflow) → `<task>-anti-patterns.md` → `<task>-validator.md` last (since the validator references the others).
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
- Interactive by default, `--auto` for unattended runs.
- Parallel subagents for non-trivial review, research, and testing.
- Working artifacts only in `.temp/`.

## Help

- Public docs: built into `gh-pages/` from `docs/`.
- Skill catalog: `skills-manifest.json` (regenerated via `npm run skills:manifest`).
- Validation: `npm run validate`.
