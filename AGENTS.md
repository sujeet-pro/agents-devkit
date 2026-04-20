# ADK Repository Guidance

Canonical entry point for any agent working **on** this repository (`agents-devkit` itself, not the ADK skills installed elsewhere). `CLAUDE.md` is a thin Claude-specific delta that points back here.

## What this repo is

A toolkit you install via `npm` or `git clone` that lays down self-contained `adk-*` skills, runtime-specific custom subagents, hooks, and MCP server configs into:

- Claude Code (CLI) and Claude Desktop
- Codex CLI and Codex Desktop
- Cursor (App + CLI)
- Gemini CLI
- Antigravity, Junie, and any generic harness that reads `.agents/skills/`

The Node CLI under [cli/](cli/) is the only installer. It is fully idempotent — re-running converges every target to the current state.

## Directory map

| Path | Purpose | Notes |
| --- | --- | --- |
| [skills/](skills/) | 37 public `adk-*` skills, each one self-contained | `SKILL.md` + flat `references/` |
| [agents-claude/](agents-claude/) | Self-contained Claude custom subagents (Markdown + YAML) | One file per agent |
| [agents-cursor/](agents-cursor/) | Self-contained Cursor custom subagents (Markdown + YAML) | One file per agent |
| [agents-codex/](agents-codex/) | Self-contained Codex custom agents (TOML) | One file per agent |
| [hooks/](hooks/) | Runtime-specific hook configs | `claude.json`, `cursor.json`, `codex.json` |
| [mcp-config/servers/](mcp-config/servers/) | Per-server MCP configs with `${ENV_VAR}` placeholders | Merged into runtime mcp.json |
| [global-prompts/](global-prompts/) | Always-on instructions injected into runtime memory files | Managed `<!-- adk:global-prompts:start/end -->` block |
| [workflows/](workflows/) | Composable multi-skill YAML pipelines | Optional |
| [cli/](cli/) | Node installer (`adk-install`) | Only install path |
| [docs/](docs/), [gh-pages/](gh-pages/) | Pagesmith docs source + built site | `npm run docs:build` |

There is no `ai-guidelines/`, no `agent-personas/`, no `prj-*` skill folder, no projection script, no Python anywhere. Each skill carries the persona / constitution / output-format text it needs, inline.

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

`.temp/` is gitignored. Promote content to a tracked path only when it is the deliverable.

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

37 public skills: 1 top router (`adk`) + 8 category routers + 28 task skills. See [skills-manifest.json](skills-manifest.json) for the full list and `skills/<name>/SKILL.md` for each skill's contract.

| Lifecycle stage | Category router | Task skills |
| --- | --- | --- |
| Plan, research, spec, design | `adk-plan` | `adk-plan-brainstorm`, `adk-plan-research`, `adk-plan-spec`, `adk-plan-design`, `adk-plan-roadmap` |
| Implement code | `adk-build` | `adk-build-feature`, `adk-build-refactor`, `adk-build-migrate`, `adk-build-test`, `adk-build-deps` |
| Review existing changes | `adk-review` | `adk-review-pr`, `adk-review-local`, `adk-review-feedback`, `adk-review-handoff` |
| Author or check docs | `adk-docs` | `adk-docs-write`, `adk-docs-review` |
| Audit a repo or site | `adk-audit` | `adk-audit-repo`, `adk-audit-site` |
| Ship to a destination | `adk-publish` | `adk-publish-commit`, `adk-publish-github`, `adk-publish-bitbucket`, `adk-publish-confluence`, `adk-publish-gdrive` |
| Make a picture | `adk-visualize` | `adk-visualize-diagram`, `adk-visualize-chart` |
| Frontend / UI work | `adk-frontend` | `adk-frontend-design`, `adk-frontend-feature`, `adk-frontend-react-csr` |

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

## Core rules for editors of this repo

- Accuracy over speed.
- Plan before non-trivial change.
- Write intermediate artifacts to `.temp/` only.
- Validate every meaningful change with `npm run validate`.
- Keep output concise and bullet-first.
- Do not present inference as fact.
- Do not reintroduce shared sources (`ai-guidelines/`, `agent-personas/`, `_shared/`). Each skill stands alone; each agent file stands alone.
