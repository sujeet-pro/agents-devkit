---
title: 'memory-files'
description: 'Repo memory file (CLAUDE.md) and how it composes with the plugin.'
---

# Repo memory file

ADK ships a single top-level memory file at the repo root: [`CLAUDE.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/CLAUDE.md). It is the canonical contract for any Claude session working **on** this repository (`agents-devkit` itself, not the ADK skills installed elsewhere).

## File

| File | Audience | Purpose |
| --- | --- | --- |
| [`CLAUDE.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/CLAUDE.md) | Any Claude session editing this repo | Canonical contract — directory map, skill shape, plugin component layout, working-artifact rules, interaction model. |

ADK is a Claude-only plugin. There is no `AGENTS.md`, `GEMINI.md`, or runtime-specific delta — `CLAUDE.md` is the single source of truth.

## Reading order for agents

1. Read `CLAUDE.md` first — it covers the directory map, skill anatomy, cross-reference convention, and `.temp/` working-artifact rules.
2. For any specific skill, read `skills/<name>/SKILL.md` plus its `references/` folder.
3. For repo-local skills (e.g. doc-site refresh), read `.claude/skills/<name>/SKILL.md`.

## Cross-reference convention

When a memory file or `SKILL.md` references another skill, use the Claude-invocable form:

> Hand off to `/adk:plan-spec`.

When referencing a subagent, use its file path: `agents/<role>.md` (no prefix).

## Source

`CLAUDE.md` at repo root.
