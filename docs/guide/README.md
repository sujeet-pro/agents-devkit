---
title: Guide
description: How adk works — philosophy, install, multi-agent setup, project-scoped overrides, and the concepts that make every skill behave consistently.
order: 1
---

# Guide

`adk` is opinionated, single-operator-shaped, multi-agent. This guide explains why it works the way it does, how to install it, how to configure it once, and the few concepts every skill leans on.

## Start here

| Read | Why |
|---|---|
| [Philosophy](./philosophy.md) | The operating principles. One page. |
| [Installation](./getting-started/installation.md) | Clone + `install.sh --target <agent>`. |
| [Multi-agent setup](./usage/multi-agent.md) | Capability matrix for Claude / Cursor / Codex / Junie. |
| [overrides.yaml](./usage/overrides-yaml.md) | The one config file you maintain. |
| [Project-scoped overrides](./usage/project-scoped.md) | `<repo>/.adk/`, `<repo>/ai-guidelines/`, `<repo>/.temp/<task-slug>/`. |

## Concepts (in priority order)

| Concept | What it gives you |
|---|---|
| [Question-first](./concepts/question-first.md) | Every skill asks up to 3 questions before any execution. Each Q&A is training data. |
| [Advisor strategy](./concepts/advisor-strategy.md) | Plan → clarify → present options → defer → execute → validate → report. Hand-off to `/adk-explain` when the user is unsure. |
| [Decision logs](./concepts/decision-logs.md) | Append-only JSONL of every fork. Consumed by `/adk-improve` to refine your defaults. |
| [Plan/Act mode](./concepts/plan-act-mode.md) | `--plan` literally restricts the implementer to read-only tools. Tool-level enforcement, not advisor-prose. |
| [Edit format](./concepts/edit-format.md) | SEARCH/REPLACE block discipline for `/adk-implement`. Prevents whole-file rewrites. |
| [Hooks](./concepts/hooks.md) | PreToolUse:Bash safety + PostToolUse:Edit validator + SessionStart banner. Deterministic enforcement of the constitution. |
