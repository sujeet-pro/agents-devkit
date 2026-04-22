---
title: 'memory-files'
description: 'Top-level repo memory files (AGENTS.md, CLAUDE.md, GEMINI.md) and how they compose.'
---

# Repo memory files

ADK ships three top-level memory files that any agent reads on activation. They form a layered contract: `AGENTS.md` is the canonical source, the others are runtime-specific deltas that point back to it.

## Files

| File | Audience | Purpose |
| --- | --- | --- |
| [`AGENTS.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/AGENTS.md) | Any agent working **on** this repo | Canonical contract — directory map, skill shape, working-artifact rules, interaction model. |
| [`CLAUDE.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/CLAUDE.md) | Claude Code | Claude-specific delta: `/adk:<skill>` invocation, plugin layout, subagents, hooks, MCP. |
| [`GEMINI.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/GEMINI.md) | Gemini CLI users | Notes for installing via `bin/adk-install --target gemini` and the differences from Claude. |

## Reading order for agents

1. Read `AGENTS.md` first — it covers the directory map, skill anatomy, cross-reference convention, and `.temp/` working-artifact rules.
2. Read the runtime-specific delta (`CLAUDE.md` / `GEMINI.md`) to learn how to invoke skills in that surface.
3. For any specific skill, read `skills/<name>/SKILL.md` plus its `references/` folder.

## Cross-reference convention

When a memory file references another skill, use **both** forms on first mention:

> `@adk:plan-spec` (a.k.a. `adk-plan-spec`)

The validator (`bin/adk-validate`) enforces dual-form on first mention.

## Source

`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` at repo root.
