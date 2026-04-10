---
title: 'workflow'
description: 'Helper skill providing 4 workflow families — Quick Action, Standard Task, Complex Build, Investigative Loop. Invoked by all task skills with --family flag'
skill_name: workflow
category: guideline
workflow_tier: helper
user_invocable: false
---

# workflow

`workflow` is the shared contract that defines the standard workflow shapes other skills rely on. Most users meet it indirectly when another skill loads it to resolve a shared rule set or a reusable contract.

## Overview

`workflow` belongs to the `guideline` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The key design trade-off is indirection. This skill rarely owns an interactive workflow on its own, but it keeps cross-cutting behavior consistent so task skills do not each reinvent the same policy, formatting rule, or detection logic.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--family` | `quick-action`, `standard-task`, `complex-build`, `investigative-loop` | (required) | Which workflow family to load |
| `--auto` | flag | off | Skip user confirmations. All steps still execute but without waiting for human input. |

### Parameter Notes

- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.

## Modes & Variations

Most helpers do not have end-user modes in the same sense as task skills, but they still vary by scope, invoking context, selected family, or fallback behavior.


### Families

Each family is a complete workflow definition. The invoking skill specifies the family; this skill loads the matching reference file.

| Family | Shape | Reference File |
|--------|-------|---------------|
| **Quick Action** | confirm → execute → verify | `${CLAUDE_SKILL_DIR}/references/quick-action.md` |
| **Standard Task** | confirm → research → execute → validate | `${CLAUDE_SKILL_DIR}/references/standard-task.md` |
| **Complex Build** | confirm → research → select approach → plan → execute → validate | `${CLAUDE_SKILL_DIR}/references/complex-build.md` |
| **Investigative Loop** | confirm → loop(investigate → hypothesize → test → refine) → summarize | `${CLAUDE_SKILL_DIR}/references/investigative-loop.md` |

Load ONLY the single family reference file that matches the `--family` flag.

### Family Selection Guide

| Task Characteristics | Family |
|---------------------|--------|
| Clear intent, single execution path, no alternatives to evaluate | Quick Action |
| Known approach, benefits from context scan, no meaningful choices | Standard Task |
| Multiple valid approaches, architectural decisions, significant scope | Complex Build |
| Unknown scope, iterative discovery, loop until root cause found | Investigative Loop |

---

## Output

Helper skills usually return a rule set, a resolved reference list, or a normalized contract back to the calling skill rather than a standalone report.


## Additional Reference

### Shared Behavior Across All Families

### `--auto` Mode

When `--auto` is passed to a skill (or the skill passes it to this workflow):

- All confirmation steps state intent but do not wait for user approval — proceed immediately
- All steps still execute; `--auto` only removes human gates
- The invoking skill decides when `--auto` is appropriate

### Conditional Helper Loading

Not all shared skills are needed for every task. Load based on complexity:

- **Always**: `/adk:communication`, `/adk:preflight-check`, `/adk:interaction`
- **Medium and Large only**: `/adk:principal-engineer`, `/adk:agentic-teams`
- **When producing output**: `/adk:output-format`

### Complexity Detection

Estimate complexity by evaluating these factors:

| Factor | Trivial | Small | Medium | Large |
|--------|---------|-------|--------|-------|
| Files affected | 1 | 2-3 | 4-8 | >8 |
| Architectural decisions needed | No | No | Maybe | Yes |
| Requirements fully clear | Yes | Yes | Mostly | Partially |
| New abstractions required | No | No | Maybe | Yes |
| Discrete sub-tasks | 1 | 2-3 | 4-6 | >6 |

When uncertain, default to Medium.

### Self-Review Principles

Applied during validation steps across all families:

- Code must be human-readable, maintainable, and extensible
- Do only the minimum changes required — no gold-plating
- Do not implement features that might be needed in the future
- Three similar lines of code is better than a premature abstraction
- If it works and reads clearly, it is done

### Output Rules

- **Concise by default** — show the compact result first, then offer "Need a detailed breakdown?" at the end
- All output is **markdown by default** unless the user requests otherwise
- Follow `/adk:communication` for tone and structure
- Lead with the conclusion or result, then supporting detail
- After task completion, always offer to elaborate — do not dump detailed output unless the user asks for it or passes `--verbosity detailed`

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:workflow --family quick-action
/adk:workflow --family complex-build --auto
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:workflow --family complex-build --auto
```
