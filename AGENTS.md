# ADK Repository Guidance

Canonical entry point for any agent working **on** this repository (`agents-devkit` itself, not the ADK skills installed elsewhere). `CLAUDE.md` is a thin Claude-specific delta that points back here.

## What this repo is

A toolkit you install (preferably via `git clone` + `npm run setup`, or via `npm install` for a pinned version, or via `npx skills add` for a skills-only quick try) that lays down self-contained `adk-*` skills, runtime-specific custom subagents, hooks, MCP server configs, and global prompts into:

- Claude Code (CLI) and Claude Desktop
- Codex CLI and Codex Desktop
- Cursor (App + CLI)
- Gemini CLI
- Antigravity, Junie, and any generic harness that reads `.agents/skills/`

The Node CLI under [cli/](cli/) is the only installer. It is fully idempotent — re-running converges every target to the current state.

## Directory map

| Path | Purpose | Notes |
| --- | --- | --- |
| [skills/](skills/) | 39 public `adk-*` skills, each one self-contained | `SKILL.md` + flat `references/` (filenames task-prefixed; only `interaction-contract.md` is shared verbatim) |
| [agents-claude/](agents-claude/) | Self-contained Claude custom subagents (Markdown + YAML) | One file per agent |
| [agents-cursor/](agents-cursor/) | Self-contained Cursor custom subagents (Markdown + YAML) | One file per agent |
| [agents-codex/](agents-codex/) | Self-contained Codex custom agents (TOML) | One file per agent |
| [hooks/](hooks/) | Runtime-specific hook configs | `claude.json`, `cursor.json`, `codex.json` |
| [mcp-config/servers/](mcp-config/servers/) | Per-server MCP configs with `${ENV_VAR}` placeholders | Merged into runtime `mcp.json` |
| [global-prompts/](global-prompts/) | Always-on instructions injected into runtime memory files | Managed `<!-- adk:global-prompts:start/end -->` block |
| [workflows/](workflows/) | Composable multi-skill YAML pipelines | Optional |
| [cli/](cli/) | Node installer (`adk-install`) | Only install path; pure ESM, no Python anywhere |
| [docs/](docs/), [gh-pages/](gh-pages/) | Pagesmith docs source + built site | `npm run docs:build` |

There is no `ai-guidelines/`, no `agent-personas/`, no `prj-*` skill folder, no projection script, no Python anywhere. Each skill carries its own task-prefixed persona, constitution (or standards), clarifying-questions, output-format, artifact-format, anti-patterns, validator (mandatory four-phase gate), and (when relevant) research-protocol, multi-repo, comment-format, reply-templates, postback-protocol, and design-system references inline. The single global file is `interaction-contract.md` — every skill ships an identical copy; the source of truth is `global-prompts/interaction-contract.md`. All 39 skills' references are unique — there is no shared boilerplate at runtime.

## Self-containment rules

- Every skill in `skills/<name>/` must work as-is when copied out of this repo. Nothing inside it may reference shared content elsewhere.
- `references/` is flat. No subdirectories. No `_shared/`. Cross-skill references in `SKILL.md` are by name only — never relative file paths into another skill folder.
- Every file in `agents-claude/`, `agents-cursor/`, `agents-codex/` is a complete, runnable agent definition for that runtime. The lists per provider may differ; one file per provider per agent. There is no shared persona source.
- Every hook file under `hooks/` is the full config for its runtime.
- Every MCP server config under `mcp-config/servers/<name>.json` is complete on its own.

## Working artifacts (`.temp/`)

All intermediate agent output goes under `.temp/`. Never write plans, drafts, reports, scratch markdown, or cloned reference material anywhere else.

| Path | Purpose |
| --- | --- |
| `.temp/plans/<slug>.md` | Implementation and restructure plans |
| `.temp/drafts/<slug>.md` | Prose drafts before promotion |
| `.temp/reports/<slug>.md` | Review findings, audits, investigations |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos |
| `.temp/notes/<slug>.md` | Short-lived working notes |
| `.temp/scripts/<name>.mjs` | One-off maintenance scripts that are not part of the CLI |

`.temp/` is gitignored. Promote content to a tracked path only when it is the deliverable.

## Interaction model (applies to every skill)

Every skill ships `references/interaction-contract.md` (the global, identical contract) and `references/clarifying-questions.md` (the skill-specific questions the agent must ask in default-ask mode, with how-to-pick rubrics for each option). Default mode is **highly interactive**: each meaningful decision is presented as 2-3 options with `Pros / Cons / Best when / Blast radius / Reversibility`, one is marked `(default)`, the user picks. `--auto` skips all approval gates and uses the documented defaults; the skill still validates and still produces a final report. The same contract is mirrored in `global-prompts/interaction-contract.md` so it lands in every runtime's memory file.

When you author or edit a skill in this repo, keep these in sync (all task-prefixed except `interaction-contract.md`):
- `references/interaction-contract.md` (identical copy across all skills — update via the global prompt at `global-prompts/interaction-contract.md` and propagate).
- `references/<task>-clarifying-questions.md` (skill-specific — every option has a "How to pick" rubric).
- `references/<task>-persona.md` (skill-specific role / mission / hard rules / status banner).
- `references/<task>-constitution.md` (shared baseline + skill-specific non-negotiables; status banner mirrored from persona). Some skills use `<task>-standards.md` for this role.
- `references/<task>-artifact-format.md` (the deliverable's actual format and where it lives).
- `references/<task>-output-format.md` (default vs detailed report shape).
- `references/<task>-validator.md` (the four-phase validator gate the skill MUST run; required for every skill).

## Maintenance commands

```bash
npm run validate          # validates skills, agents, hooks (replaces old Python tests)
npm run skills:manifest   # regenerate skills-manifest.json from skills/
npm run setup             # interactive installer (alias: adk-install)
npm run setup:dry         # preview, write nothing
npm run docs:build        # build gh-pages/ from docs/
```

## Settings

| Scope | Path | Format |
| --- | --- | --- |
| User | `~/.config/adk/settings.json5` | json5 (comments allowed) |
| Project | `<project>/.adk/settings.json5` | json5; overrides user file field-by-field |

Both files are managed by `adk-install`. The user file also stores `knownPackagePaths` so that re-runs from a different install location prune cleanly.

## Skill catalog

39 public skills: 1 top router (`adk`) + 8 category routers + 30 task skills. See [skills-manifest.json](skills-manifest.json) for the full list and `skills/<name>/SKILL.md` for each skill's contract.

| Lifecycle stage | Category router | Task skills |
| --- | --- | --- |
| Plan, research, spec, design | `adk-plan` | `adk-plan-brainstorm`, `adk-plan-research`, `adk-plan-spec`, `adk-plan-design`, `adk-plan-roadmap` |
| Implement code | `adk-build` | `adk-build-feature`, `adk-build-refactor`, `adk-build-migrate`, `adk-build-test`, `adk-build-deps` |
| Review existing changes | `adk-review` | `adk-review-pr`, `adk-review-local`, `adk-review-feedback`, `adk-review-handoff` |
| Author or check docs | `adk-docs` | `adk-docs-write`, `adk-docs-review` (with `--mode confluence` for inline + footer comments on Confluence pages) |
| Audit a repo or site | `adk-audit` | `adk-audit-repo`, `adk-audit-site` |
| Ship to a destination | `adk-publish` | `adk-publish-commit`, `adk-publish-github`, `adk-publish-bitbucket`, `adk-publish-confluence`, `adk-publish-gdrive` |
| Make a picture | `adk-visualize` | `adk-visualize-diagram`, `adk-visualize-chart` |
| Frontend / UI work | `adk-frontend` | `adk-frontend-design`, `adk-frontend-feature`, `adk-frontend-react-csr` |
| Bootstrap a docs site | (no router) | `adk-doc-site-setup` |
| Bootstrap AI in a repo | (no router) | `adk-adopt-ai-in-repo` |

## Provider-specific notes

| Provider | Entry point | Skills discovery | Custom agent format |
| --- | --- | --- | --- |
| Claude Code | `CLAUDE.md` | `.claude/skills/` | Markdown + YAML frontmatter, one file per agent |
| Claude Desktop | `claude_desktop_config.json` | n/a | n/a (only MCP) |
| Cursor (App + CLI) | `AGENTS.md` | `.cursor/skills/` | Markdown + Cursor-shaped frontmatter |
| Codex CLI | `AGENTS.md` | `.codex/skills/`, `.agents/skills/` | TOML (one file per agent) |
| Codex Desktop | `~/Library/Application Support/Codex/...` | n/a | n/a (only MCP) |
| Gemini CLI | `GEMINI.md` | `.agents/skills/` | n/a |
| Antigravity | `AGENTS.md` | `.antigravity/skills/` | n/a |
| Junie | `AGENTS.md` | `.junie/skills/` | n/a |

## Install-scenario ↔ link-target matrix

Ordered from suggested (top) to most minimal (bottom). The first three paths use the Node CLI in this repo and wire up all five surfaces (skills, agents, hooks, MCP, global prompts). The `npx skills` row uses the third-party [`skills`](https://skills.sh) loader and lands skills only.

| Install | Command | Package lives at | CLI links into | Best when |
| --- | --- | --- | --- | --- |
| Clone + install script (**suggested**) | `git clone … && npm install && npm run setup` | The clone you choose | Either (`--mode global` or `--mode project`); symlinks point at the clone so edits show up live | Default for almost everyone — `git pull` to update, edit skills in place |
| Global npm | `npm install -g agents-devkit && adk-install` | `$(npm prefix -g)/lib/node_modules/agents-devkit` | `$HOME/.{agents,claude,cursor,codex,antigravity,junie,gemini}/...` | Pinned to a published version, one toolkit per machine |
| Per-project npm | `npm i --save-dev agents-devkit && npx adk-install` | `<project>/node_modules/agents-devkit` | `<project>/.{agents,claude,cursor,codex,antigravity,junie}/...` | Pinned in `package.json`, CI-reproducible bundle in one repo |
| `npx skills add` (skills only — non-tech folks) | `npx skills add sujeet-pro/agents-devkit` | (cached by `skills` loader) | Agent's skills folder only | No Node toolchain commitment; **NOT** installed: custom subagents, hooks, MCP servers, global prompts |

When documenting installation for users, keep this ordering: clone-first, npm modules second, `npx skills` third with the "skills only" caveat called out explicitly.

## Core rules for editors of this repo

- Accuracy over speed.
- Plan before non-trivial change.
- Write intermediate artifacts to `.temp/` only.
- Validate every meaningful change with `npm run validate`.
- Keep output concise and bullet-first.
- Do not present inference as fact.
- Do not reintroduce shared sources (`ai-guidelines/`, `agent-personas/`, `_shared/`). Each skill stands alone; each agent file stands alone.
- When you change a skill's `SKILL.md`, keep its `references/interaction-contract.md` and `references/constitution.md` aligned so consumers downstream get the same contract.
