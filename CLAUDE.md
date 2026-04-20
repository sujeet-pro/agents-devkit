# ADK — Claude Code delta

Read [AGENTS.md](AGENTS.md) first; it is the canonical contract for any agent working **on** this repository. Everything below is Claude-specific.

## Claude specifics

- Custom subagents: `.claude/agents/<name>.md` (installed from [agents-claude/](agents-claude/) by `adk-install`).
- Hook config: `.claude/settings.json` (installed from [hooks/claude.json](hooks/claude.json) — symlink in this repo).
- Skill discovery: `.claude/skills/<name>` symlinks into the hub at `.agents/skills/<name>`.
- Optional local Claude env flags: `.claude/settings.local.json`.

## Working artifacts

All intermediate output goes under `.temp/` (gitignored). See `AGENTS.md` for the full path table.

## Installation

This package is published on npm and the CLI auto-detects how it was launched:

- `npm install -g agents-devkit` then `adk-install` → writes into `$HOME`.
- `npm install --save-dev agents-devkit` then `npx adk-install` → writes into the project's dot-dirs.
- `git clone …` then `npm install && npm run setup` → writes wherever you choose; symlinks point at the clone.

User config lives at `~/.config/adk/settings.json5`. Project config (when `--mode project`) lives at `<project>/.adk/settings.json5`.
