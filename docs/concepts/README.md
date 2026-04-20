---
title: Concepts
description: The mental model behind ADK — philosophy, skills, agents, hooks, and MCP
order: 1
---

# Concepts

ADK is an opinionated kit that your coding agent (Claude Code, Cursor, Codex, Gemini CLI, Antigravity, Junie) can use to work on real repositories. The surface you install is small. The ideas behind it are what make it consistent.

Read these pages in order if you are new. Each one answers a single question.

| Page | Question it answers |
| --- | --- |
| [Philosophy](./philosophy.md) | What values does every ADK skill and agent follow? |
| [Skill Anatomy](./skill-anatomy.md) | What is a skill, what is inside one, and what workflow does every skill run? |
| [Agent Personas](./agents.md) | What subagents exist, and why are they duplicated per harness (Claude, Cursor, Codex)? |
| [Hooks](./hooks.md) | What automatic safety and lifecycle checks run around agent sessions? |
| [MCP Servers](./mcp.md) | When should a skill use an MCP server, and what falls back to manual work? |

## One-Paragraph Summary

ADK treats a coding agent as a junior teammate. A **skill** is the playbook for one kind of job (plan, build, review, document, audit). Every skill follows the same six-phase workflow, dispatches focused **agent personas** when work is non-trivial, and stays self-contained so it keeps working even if a helper is missing. **Hooks** add non-negotiable safety rails around every session. **MCP servers** are optional power-ups — if they are installed ADK uses them, if not ADK falls back to manual behavior. Everything above the harness (skills, personas, shared guidance) is authored once; ADK then **projects** it into Claude, Cursor, and Codex runtimes so every tool sees the same playbook in its native format.

## Where To Go Next

- If you just want to use ADK in your repo, read [Philosophy](./philosophy.md) and then the [Public Skills reference](../reference/skills/).
- If you want to extend ADK (add a skill, add a persona, edit shared guidance), read [Skill Anatomy](./skill-anatomy.md) and [`AGENTS.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/AGENTS.md).
- If you want to understand why the same persona ships as Markdown for Claude and TOML for Codex, read [Agent Personas](./agents.md).
