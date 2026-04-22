# ADK — Claude Code delta

Read [AGENTS.md](AGENTS.md) first; it is the canonical contract for any agent working **on** this repository. Everything below is Claude-specific.

## Repo IS the plugin

This repo is a Claude Code plugin (`adk`). Skills are invoked as `/adk:<skill-name>`, e.g. `/adk:plan-brainstorm`, `/adk:review-pr`, `/adk:auto`.

| Component | Location | Notes |
| --- | --- | --- |
| Plugin manifest | `.claude-plugin/plugin.json` | `name: "adk"` |
| Marketplace | `.claude-plugin/marketplace.json` | Private marketplace for distribution |
| Skills | `skills/<name>/SKILL.md` | No `adk-` prefix in folder names; frontmatter `name` matches folder |
| Subagents | `agents/<role>.md` | Markdown + YAML frontmatter |
| Hooks | `hooks/hooks.json` | PreToolUse:Bash, PostToolUse:Edit/Write, Stop, SessionStart |
| MCP | `.mcp.json` | `${ENV_VAR}` placeholders; `bin/adk-mcp-install` resolves them |
| Monitors | `monitors/monitors.json` | `cicd-monitor` watches `gh pr checks` |
| Settings | `settings.json` | Plugin-level Claude defaults |

## Local development

```bash
claude --plugin-dir /Users/sujeet/personal/agents-devkit
```

Inside Claude:

```
/adk:auto                  # prompt-routing dispatcher (recommended starting point)
/adk:plan-brainstorm       # any specific skill, by name
/reload-plugins            # after editing a SKILL.md
```

## Interaction contract

Every ADK skill is highly interactive by default and supports `--auto` for unattended runs. The full contract is at `bin/canonical/interaction-contract.md` (single source of truth) and propagated as a byte-identical copy into every `skills/<name>/references/interaction-contract.md` by `bin/adk-sync-contracts`. Never edit the per-skill copies directly.

## Mode contract

Many skills support `--mode review | fix | auto`. See `skills/mode-contract/SKILL.md` for the universal definition. Each skill declares its supported modes in `metadata.modes`.

## Auto-router

`/adk:auto` reads the prompt, classifies the domain, runs `requirements` + `scoping` (via `agents/brainstorm-facilitator.md`), then dispatches per-task subagents (via `agents/dispatcher.md`) with the right downstream skills. It is the default entry point when the user issues a non-trivial prompt.

## Working artifacts

All intermediate output goes under `.temp/` (gitignored). See AGENTS.md for the full path table; the canonical task layout is `.temp/task-<slug>/{context,requirements,scope,brainstorm,spec,design,plan,roadmap,preview/,validation/,browser-validation/,report}.md`.

## When editing this repo

- Plan in `.temp/plans/<slug>.md` first.
- Run `npm run sync-contracts` after editing `bin/canonical/*`.
- Run `npm run validate` before commit.
- Use `gh` CLI for every GitHub op.
- Do not touch `docs/` or `gh-pages/`.
