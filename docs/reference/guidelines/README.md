---
title: Guidelines Reference
description: How shared guidance is now inlined inside each ADK skill.
order: 4
---

# Guidelines Reference

ADK no longer ships a separate `ai-guidelines/` folder or any `_shared/` directory. Every public skill is fully standalone: the constitution, working-artifacts rule, output format, research protocol, brainstorming workflow, review-comment format, persona, anti-patterns, and examples each live as a copy inside the skill's own `references/` folder.

## What every skill ships

Each skill in `skills/<name>/` owns a flat `references/` directory. The vocabulary it picks from:

| Reference file | Used by |
| --- | --- |
| `references/persona.md` | every task skill (the agent persona that drives it) |
| `references/workflow.md` (when authored) | every task skill (the step-by-step protocol) |
| `references/output-format.md` | every task skill |
| `references/constitution.md` | every skill (non-negotiable rules subset) |
| `references/working-artifacts.md` | most task skills (the `.temp/` rule) |
| `references/research-protocol.md` | research / audit / brainstorm skills |
| `references/brainstorming-workflow.md` | `adk-plan-brainstorm` |
| `references/review-comment-format.md` | review / audit / docs-review skills |
| `references/mcp-fallback.md` | skills that prefer an MCP server (with a manual fallback) |
| `references/anti-patterns.md` | every skill |
| `references/examples.md` | most skills |

## Why no shared sources

- **Portability.** A skill folder can be copied out of this repo into any other agent setup and continue to work without dragging shared files along.
- **No drift.** There is no auto-propagation script and no shared "canonical" source whose updates have to be replayed into 37 places.
- **Predictable footprint.** What you see in a skill folder is what the skill uses; nothing is hidden in `_shared/` or `ai-guidelines/`.

## How to update a skill's guidance

Edit the file directly inside the skill's `references/`. Changes do not propagate to other skills. If you want a change everywhere, edit it inside every skill that uses that file. Use `npm run validate` to confirm structure stays clean.
