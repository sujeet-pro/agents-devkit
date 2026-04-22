# ADK — Claude Code delta

Read [AGENTS.md](AGENTS.md) first; it is the canonical contract for any agent working **on** this repository. Everything below is Claude-specific.

## Claude specifics

- Custom subagents: `.claude/agents/<name>.md` (installed from [agents-claude/](agents-claude/) by `adk-install`).
- Hook config: `.claude/settings.json` (installed from [hooks/claude.json](hooks/claude.json) — symlink in this repo).
- Skill discovery: `.claude/skills/<name>` symlinks into the hub at `.agents/skills/<name>`.
- Optional local Claude env flags: `.claude/settings.local.json`.

## Interaction contract

Every ADK skill is highly interactive by default and supports `--auto` for unattended runs. See `global-prompts/interaction-contract.md` and any skill's `references/interaction-contract.md` for the full text. Default mode asks one question at a time with explained options (`Pros / Cons / Best when / Blast radius / Reversibility`); `--auto` picks the documented `(default)` at every fork. Every skill also runs a four-phase validator gate (`<task>-validator.md`) at every phase boundary — pre-execution, mid-flow, pre-handoff/pre-publish, post-execution — before declaring success.

## Reference filename convention

References under each skill's `references/` are **task-prefixed** by the skill's task token (the suffix after `adk-`): e.g., `pr-reviewer-persona.md` and `pr-review-validator.md` for `adk-review-pr`; `feature-persona.md` and `feature-validator.md` for `adk-build-feature`. The single file shared verbatim across all skills is `interaction-contract.md`.

## Working artifacts

All intermediate output goes under `.temp/` (gitignored). See `AGENTS.md` for the full path table.

## Installation

Install paths in priority order. Paths 1 and 2 use the bundled Node CLI and wire up all five surfaces (skills, custom subagents, hooks, MCP, global prompts). Path 3 uses the third-party [`skills`](https://skills.sh) loader and lands skills only.

1. **Suggested — clone + install script.** `git clone https://github.com/sujeet-pro/agents-devkit.git && cd agents-devkit && npm install && npm run setup`. Symlinks point at the clone, so `git pull` refreshes everything and local edits show up live.
2. **npm modules — pinned / CI-reproducible.** `npm install -g agents-devkit && adk-install` (writes into `$HOME`) or `npm install --save-dev agents-devkit && npx adk-install` (writes into the project's dot-dirs).
3. **Non-tech folks — `npx skills add sujeet-pro/agents-devkit`.** Lands SKILL.md files only. Custom subagents, hooks, MCP servers, and global prompts are NOT installed via this path.

The CLI used in paths 1 and 2 auto-detects how it was launched and the install scope; override with `--mode global|project` or `--root <path>`. User config lives at `~/.config/adk/settings.json5`. Project config (when `--mode project`) lives at `<project>/.adk/settings.json5`.
