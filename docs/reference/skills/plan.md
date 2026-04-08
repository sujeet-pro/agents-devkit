---
title: "plan"
description: Brainstorm, write, execute, and track implementation plans
skill_name: plan
category: task
workflow_tier: full
---

# plan

Creates, executes, and tracks implementation plans with explicit human checkpoints before execution.

## When to Use

- Brainstorm approaches to a problem
- Write a structured implementation plan
- Execute an approved plan step by step
- Track progress of an in-progress plan

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `brainstorm`, `write`, `execute`, `track` | auto-detect | Planning mode |
| `--spec` | file path | — | Reference specification |
| `--plan` | file path | — | Existing plan (for execute/track) |
| `--format` | `markdown`, `checklist` | `markdown` | Plan output format |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Modes

| Mode | Purpose | Modifies Code? |
|------|---------|----------------|
| `brainstorm` | Explore approaches, pros/cons | No |
| `write` | Create a detailed plan | No |
| `execute` | Execute an approved plan | Yes |
| `track` | Show progress of an in-progress plan | No |

### Hard Gates

- `brainstorm` does not implement anything
- `write` does not execute anything
- `execute` requires an approved plan

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Detect mode, confirm goal |
| 1. Research | Analyze codebase, gather context (brainstorm/write) |
| 2. Approach | Present approaches (brainstorm/write) |
| 3. Planning | Create detailed task breakdown (write) |
| 4. Execute | Implement plan tasks (execute only) |
| 5. Validate | Verify results, update progress (all modes) |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer` (medium+), `agentic-teams` (medium+), `interaction`.

## Examples

```text
/adk:plan --mode brainstorm caching strategy for the API
/adk:plan --mode write --spec ./docs/specs/caching.md implement caching
/adk:plan --mode execute --plan ./.temp/caching-plan/plan.md
/adk:plan --mode track --plan ./.temp/caching-plan/plan.md
/adk:plan --mode write --format checklist database migration steps
```
