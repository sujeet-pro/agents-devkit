---
name: workflow
description: "adk - [helper] [framework] Helper skill providing 4 workflow families — Quick Action, Standard Task, Complex Build, Investigative Loop. Invoked by all task skills with --family flag."
user-invocable: false
argument-hint: "--family quick-action|standard-task|complex-build|investigative-loop [--auto]"
allowed-tools: [Read]
workflow-tier: helper
maturity: stable
---

# Workflow Families

This skill provides workflow definitions that task skills invoke with a `--family` flag. Each family matches a natural task shape — skills choose the family that fits their work, rather than skipping phases from a universal template.

---

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--family` | `quick-action`, `standard-task`, `complex-build`, `investigative-loop` | (required) | Which workflow family to load |
| `--auto` | flag | off | Skip user confirmations. All steps still execute but without waiting for human input. |

### Examples

```
(invoked by task skills, not directly by users)
/adk:workflow --family quick-action
/adk:workflow --family complex-build --auto
```

---

## Families

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

## Shared Behavior Across All Families

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
