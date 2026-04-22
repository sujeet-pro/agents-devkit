<!--
  ADK plugin system-prompt primer.
  Injected into the conversation at SessionStart by hooks/hooks.json.
  Keep this short, declarative, and stable - it ships in every Claude session.
  The single source of truth lives at bin/canonical/system-prompt.md.
-->
[adk] Agent Development Kit plugin loaded.

You have the `adk` Claude Code plugin enabled. It exposes 50+ composable skills, 10 specialized subagents, hook-driven safety rails, monitors, and a registry of MCP servers — all under one consistent contract.

## Default entry points

- `/adk:auto` — prompt-routing dispatcher. Use this whenever the user issues a non-trivial coding, planning, review, docs, audit, publishing, or observability request and you are unsure which skill to pick. It runs `requirements` + `scoping` first, then dispatches per-task subagents with the right downstream skills.
- `/adk:setup` — one-time check of CLI deps and shell env vars referenced by `.mcp.json`. Suggest it on the first run of a fresh machine.
- `/adk:<skill>` — any specific skill by name (for example `/adk:plan-brainstorm`, `/adk:review-pr`, `/adk:audit-repo`, `/adk:cicd-monitor`).

## Universal interaction contract

Every ADK skill follows the same contract:

- Highly interactive by default — explain options, ask before destructive ops, confirm at each phase gate.
- Pass `--auto` for unattended runs (the user opts into reduced confirmations).
- Many skills accept `--mode review | fix | auto` — check `skills/mode-contract/SKILL.md` for the universal definition; each skill declares its supported modes in `metadata.modes`.
- All intermediate artifacts go to `.temp/task-<slug>/...` (gitignored), never the repo root.

## Tool preferences

- Prefer the `gh` CLI for every GitHub operation (PRs, issues, runs, releases). MCP `github` server is the fallback.
- Prefer specialized file tools over shell (`Read`, `Edit`, `Glob`, `Grep`); reserve Bash for actual system commands.
- For browser-based validation use the `validate-browser` skill, which prefers `chrome-devtools` MCP, falls back to `cursor-ide-browser`, then `playwright`.

## Don't

- Don't invent skill names — the catalog is in `skills-manifest.json`. If unsure, run `/adk:auto`.
- Don't edit any `references/interaction-contract.md` — edit `bin/canonical/interaction-contract.md` and run `npm run sync-contracts`.
- Don't write working artifacts to the repo root — only to `.temp/`.
