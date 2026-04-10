---
title: 'dev-refactor'
description: 'Refactor code — extract, rename, restructure, simplify, or modernize patterns across files with safe, tested transformations'
skill_name: dev-refactor
category: task
workflow_tier: full
user_invocable: true
---

# dev-refactor

Use `dev-refactor` to refactor code — extract, rename, restructure, simplify, or modernize patterns across files with safe, tested transformations. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`dev-refactor` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<description>` | free text | required | What to refactor and why |
| `--scope` | `<path>` | auto-detect | Limit refactoring to specific files/directories |
| `--pattern` | `extract`, `rename`, `restructure`, `simplify`, `modernize` | auto-detect | Force a specific refactoring pattern |
| `--auto` | flag | off | Skip confirmations |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--pattern` is the fastest way to tell a transformation skill what kind of change you want instead of relying on intent inference.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family standard-task` | always | Standard Task workflow: confirm → research → execute → validate. For tasks with known approach that benefit from context scan. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents for parallel analysis and refactoring. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |

---

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If any declared dependency is missing, stop and tell the user what to install before proceeding.

### Refactoring Process

### 1. Scope Analysis

- Identify all files and symbols affected by the refactoring
- Map dependencies and usage sites
- Estimate blast radius — how many files, tests, and downstream consumers are impacted
- Check for existing test coverage on affected code

### 2. Safety Baseline

- Run the existing test suite and record results
- Note any pre-existing failures to avoid false attribution
- If test coverage is low on affected code, suggest adding tests first

> **Gate**: Present safety assessment to user. If tests are missing, get approval to add them first. Skip if `--auto`.

### 3. Transformation Plan

Generate ordered steps, each independently verifiable:

```

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **`extract`**: Extract functions, classes, modules, or components from existing code
- **`rename`**: Rename symbols across the codebase (variables, functions, classes, files)
- **`restructure`**: Reorganize file/directory structure, move modules, update imports
- **`simplify`**: Reduce complexity — flatten nested logic, remove dead code, consolidate duplicates
- **`modernize`**: Update to modern patterns — replace deprecated APIs, adopt new language features
- **Auto-detect** (default): analyzes the request and picks the best pattern

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```markdown
# Refactoring Report

## Related Skills

### Adjacent Skills

- `/adk:dev-build` for implementing new features after refactoring
- `/adk:code-review-pr` for reviewing the refactoring PR
- `/adk:audit` for identifying refactoring opportunities
- `/adk:coding` for loading language-specific refactoring patterns

## Additional Reference

### Safety Guarantees

1. **Test first**: verify existing tests pass before any changes
2. **Incremental**: apply changes in small, reversible steps
3. **Validate after each step**: run tests between transformation steps
4. **Preserve behavior**: refactoring must not change observable behavior
5. **Rollback ready**: every step can be reverted independently

---

### Refactoring Plan

**Pattern**: extract
**Scope**: 8 files, 3 modules
**Risk**: Low — all affected code has test coverage

| Step | Change | Files | Verify |
|------|--------|-------|--------|
| 1 | Create AuthService class | 1 new file | tests pass |
| 2 | Move auth methods from UserController | 2 files | tests pass |
| 3 | Update imports in consumers | 5 files | tests pass |
| 4 | Remove dead code from UserController | 1 file | tests pass |
```

> **Gate**: Present transformation plan to user for approval before execution. Skip if `--auto`.

### 4. Execution

- Apply each step sequentially
- Run tests after each step
- If a test fails, diagnose and fix before proceeding
- Track which steps are complete for resume capability

### 5. Validation

- Run full test suite
- Verify no new lint warnings
- Check that the refactored code is simpler (fewer lines, lower complexity, clearer naming)
- Produce a summary of what changed and why

---

### Summary

- **Pattern**: extract / rename / restructure / simplify / modernize
- **Files changed**: N
- **Lines added/removed**: +N / -N
- **Tests**: all passing

### Changes

1. Step 1: [description] — [files]
2. Step 2: [description] — [files]

### Quality Metrics

- Cyclomatic complexity: before → after
- Lines of code: before → after
- Test coverage on affected code: N%
```

---

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:dev-refactor <prompt-text>
/adk:dev-refactor extract the auth logic from UserController into a separate AuthService
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:dev-refactor --scope <path> <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:dev-refactor <prompt-text> --verbosity detailed
```
