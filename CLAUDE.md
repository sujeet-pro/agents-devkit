# ADK — Claude Code plugin contract

Canonical guide for any Claude session working **on** this repository (`agents-devkit` itself, not the ADK skills installed elsewhere). The repo IS the `adk` Claude Code plugin.

## What this repo is

This repo is a single Claude Code plugin loaded via `.claude-plugin/plugin.json`. The Claude plugin host loads everything — there is no separate "installer" step. Distribution is via the marketplace at `.claude-plugin/marketplace.json`, which exposes two plugin sources:

- `adk` — `source: { source: "github", repo: "sujeet-pro/agents-devkit" }` — tracks `main`.
- `adk-npm` — `source: { source: "npm", package: "agents-devkit" }` — installs the plugin from the npm registry so users can pin a semver release.

The same marketplace also works when added from a local clone (`/plugin marketplace add ~/code/agents-devkit`), which lets contributors edit the working tree and refresh through the standard `/plugin` lifecycle.

Skills are invoked as `/adk:<skill-name>`, e.g. `/adk:plan-brainstorm`, `/adk:review-pr`, `/adk:auto`.

## Directory map

| Path | Purpose | Notes |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | Plugin manifest | `name: "adk"`, semver `version`. Component dirs use the [default plugin layout](https://code.claude.com/docs/en/plugins-reference#standard-plugin-layout). |
| `.claude-plugin/marketplace.json` | Marketplace catalog | Single `adk` plugin entry; `source.source: "github"` tracks `main`. |
| `skills/<name>/` | All skills | `SKILL.md` + `references/`. Bare folder names, no `adk-` prefix. Frontmatter `name` matches folder. |
| `agents/<role>.md` | Subagents | Markdown + YAML frontmatter. Plugin subagents do not support `hooks`, `mcpServers`, or `permissionMode` per the [plugin spec](https://code.claude.com/docs/en/sub-agents). |
| `hooks/hooks.json` | Lifecycle hooks | `PreToolUse:Bash`, `PostToolUse:Edit\|Write`, `Stop`, `SessionStart`. |
| `.mcp.json` | MCP server registry | `${ENV_VAR}` placeholders. Resolved at session start by Claude Code from your shell env. |
| `monitors/monitors.json` | Background monitors | `cicd-monitor` watches `gh pr checks`. |
| `settings.json` | Plugin-level Claude defaults | `subagentStatusLine` etc. Currently only `agent` and `subagentStatusLine` keys are honored. |
| `bin/` | Repo CLI scripts | Auto-added to the Bash tool's `PATH` while the plugin is enabled. |
| `bin/canonical/` | Single source of truth | `interaction-contract.md` + `system-prompt.md`. Propagated into every skill via `bin/adk-sync-contracts`. |
| `bin/internal/` | Repo helpers | `manifest.mjs`, `generate-skill-docs.mjs`. |
| `docs/`, `gh-pages/` | Pagesmith docs source + built site | UNTOUCHED in normal feature work — owned by the docs skill. |
| `.claude/skills/prj-update-docs/` | Repo-local skill | Project-only skill for refreshing the doc site. Loaded as `/prj-update-docs` (no plugin namespace) when working in this repo. |
| `.claude/settings.local.json` | Personal local settings | Not checked-in flags (e.g. experimental env vars). |

## Skill folder shape

```
skills/<name>/
  SKILL.md
  references/
    how-it-works.md            # required: mermaid diagram + decision flow
    modes.md                   # required: which --mode this skill supports
    persona.md / workflow.md / clarifying-questions.md / output-format.md /
    artifact-format.md / validator.md / anti-patterns.md / examples.md
    interaction-contract.md    # PHYSICAL COPY synced from bin/canonical/
    [optional: research-protocol.md, mcp-fallback.md, multi-repo.md, scripts/]
```

Migrated skills keep their existing `<task>-prefixed` reference filenames (e.g. `plan-brainstorm-persona.md`) to minimize churn. New skills use bare names.

## SKILL.md frontmatter

```yaml
---
name: <skill-name>            # required, must equal folder basename
description: |                # required, single paragraph; Claude uses it for auto-invoke
  <when to use, what it does, when NOT to use>
metadata:                     # optional, ADK-specific
  category: meta | discovery | plan | frontend | build | review | docs | audit | publish | observability | bootstrap
  kind: top | router | task
  modes: [auto, fix, review]
  layer: 0..10
  needs_mcp: [github, datadog, ...]
disable-model-invocation: false
---
```

See the [Claude Code skills spec](https://code.claude.com/docs/en/skills#frontmatter-reference) for the full set of supported keys (including `allowed-tools`, `argument-hint`, `arguments`, `context`, `agent`, `paths`, `effort`, `model`).

## Cross-reference convention

When a `SKILL.md` references another skill, use the Claude-invocable form:

> Hand off to `/adk:plan-spec`.

When referencing a subagent, use its file path: `agents/<role>.md` (no prefix).

## Working artifacts (`.temp/`)

All intermediate output goes under `.temp/` (gitignored). The canonical layout enforced by `temp-folder` skill:

```
.temp/task-<slug>/
  context.md, requirements.md, scope.md, brainstorm.md, spec.md, design.md, roadmap.md
  preview/sample-{1..5}.html
  plan.md
  validation/<phase>.md
  browser-validation/<mode>/...
  report.md
```

Also at top-level:

| Path | Purpose |
| --- | --- |
| `.temp/plans/<slug>.md` | Restructure / refactor plans (no specific task) |
| `.temp/drafts/<slug>.md` | Prose drafts before promotion |
| `.temp/reports/<slug>.md` | Reviews, audits, investigations |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos for research |
| `.temp/notes/<slug>.md` | Short-lived working notes |

## Interaction contract

Every ADK skill is highly interactive by default and supports `--auto` for unattended runs. The full contract lives at `bin/canonical/interaction-contract.md` (single source of truth) and is propagated byte-identically into every skill's `references/interaction-contract.md` by `bin/adk-sync-contracts`. Never edit per-skill copies directly.

## Mode contract

Many skills support `--mode review | fix | auto`. See `skills/mode-contract/SKILL.md` for the universal definition. Each skill declares its supported modes in `metadata.modes`.

## Auto-router

`/adk:auto` reads the prompt, classifies the domain, runs `requirements` + `scoping` (via `agents/brainstorm-facilitator.md`), then dispatches per-task subagents (via `agents/dispatcher.md`) with the right downstream skills. It is the default entry point when the user issues a non-trivial prompt.

## Local development

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
claude --plugin-dir "$(pwd)"
```

Inside Claude:

```
/adk:auto                  # prompt-routing dispatcher (recommended starting point)
/adk:plan-brainstorm       # any specific skill, by name
/reload-plugins            # after editing a SKILL.md, agent, hook, or MCP entry
```

For docs-site work and repo-level maintenance:

```bash
npm install                # only needed when building the docs site
npm run validate           # bin/adk-validate — structural + content checks; regenerates skills-manifest.json
npm run validate:sync      # bin/adk-sync-contracts --check
npm run sync-contracts     # bin/adk-sync-contracts (propagate canonical files)
npm run docs:build         # build gh-pages/ from docs/
```

## Core rules for editors of this repo

- Plan before non-trivial change; lock plan in `.temp/plans/`.
- Write intermediate artifacts to `.temp/` only; never the repo root.
- Validate every change with `npm run validate`.
- Keep output concise and bullet-first.
- Do not present inference as fact.
- Do not edit `references/interaction-contract.md` in any skill — edit `bin/canonical/interaction-contract.md` and run `npm run sync-contracts`.
- Use `gh` CLI for all GitHub operations (PRs, issues, runs, releases). MCP `github` is fallback.
- Do not touch `docs/` or `gh-pages/` outside of dedicated docs work — use `/prj-update-docs` for the full refresh.
