# ADK — Gemini delta

Read [AGENTS.md](AGENTS.md) first; it is the canonical contract.

## Note for Gemini CLI users

This repo is primarily a Claude Code plugin (`.claude-plugin/plugin.json`). Gemini CLI does not consume Claude plugin manifests directly, so the `agents-skills/` tree is what you want.

## Install for Gemini CLI

```bash
node bin/adk-install --target gemini
```

This symlinks every `agents-skills/adk-<name>/` folder into `~/.gemini/skills/` (or `<project>/.gemini/skills/` with `--mode project`). Each symlink resolves to `skills/<name>/`, so each skill's full contents (SKILL.md + references/) are present.

Skill invocation in Gemini: refer to skills by their `adk-<name>` form (e.g., `adk-plan-brainstorm`).

## Differences from Claude

- No subagent dispatch. The Gemini-side use of `auto` collapses to a single agent reading the auto skill workflow and following it sequentially.
- No native MCP host integration today (varies by Gemini CLI version). The MCP-aware skills will fall back to documented CLI alternatives (`gh`, `npx playwright`, etc.) where available.
- Hooks are not supported.

## Working artifacts

Same `.temp/` rule as Claude. See AGENTS.md.
