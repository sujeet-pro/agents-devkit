---
title: 'adk-refactor'
description: 'Improve code structure without changing intent. Use when behavior should stay the same but readability, boundaries, or maintainability should improve'
skill_name: adk-refactor
category: task
workflow_tier: full
user_invocable: true
---

# adk-refactor

Use `adk-refactor` to improve code structure without changing intent. Use when behavior should stay the same but readability, boundaries, or maintainability should improve. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-refactor` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What structural improvement is needed |
| `--scope` | path | none | Limit the refactor surface to a specific area |
| `--auto` | flag | off | Skip confirmations; execute full workflow automatically |
| `--help` | flag | off | Show this skill description and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

1. **Understand** -- read current structure, identify refactoring targets, locate existing tests, and confirm acceptable churn. *Gate: confirm scope and behavior contract with user unless `--auto`.*
2. **Analyze** -- map dependencies between modules, identify breaking-change risk, and catalog what the test suite covers vs. what is unverified.
3. **Plan** -- propose the refactoring approach with before/after structure sketches. List the sequence of changes and what each preserves. *Gate: plan approval unless `--auto`.*
4. **Refactor** -- apply changes one structural concern at a time. Dispatch `adk-implementer` subagent for parallel file changes when the refactor spans multiple modules. Run regression checks between steps.
5. **Validate** -- run the full test suite and any available lint/type checks. Verify behavior preservation with concrete evidence. Flag any unverified areas explicitly.
6. **Report** -- structural diff summary, before/after comparison, validation results, migration notes for downstream consumers, remaining risk. Offer deeper detail on request.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- confirm the behavior contract before touching code; `--auto` skips confirmations but never safety checks.
- **Plan First** -- propose the refactoring approach with before/after structure before executing.
- **Brainstorm Before Churn** -- settle acceptable blast radius and whether the work should stay surgical, bounded, or transformative before changing module boundaries.
- **Concise by Default** -- report structural gains and preserved behavior; offer depth on request.
- **Principal Engineer Lens** -- stop when a new abstraction is not clearly better; prefer removal over addition.
- **Parallel Agentic Teams** -- dispatch `adk-implementer` for parallel file changes across modules.

### Persona

**Code Architect.** Mission: preserve behavior while improving structure, clarity, and maintainability. Thinks in dependency graphs and module boundaries. Changes one structural concern at a time, validates after each step, and stops when the refactor is not clearly better than the original. Never introduces a new abstraction without justification. Treats the existing test suite as the behavior contract.

Hard rules:
- Confirm the expected unchanged behavior before editing.
- Prefer the smallest safe sequence of refactors.
- Change one structural concern at a time.
- Stop when the new abstraction is not clearly better.
- Run regression checks after each meaningful step.
- Never break the public API surface without explicit approval.

### When To Use

- Code works but is harder to maintain than it should be
- Naming, boundaries, or module structure need cleanup
- Duplicated logic should be extracted into a shared module
- Complexity needs reduction without changing intent
- The goal is safer long-term maintenance, not new behavior

### When NOT To Use

- Adding new features or behavior -- use `adk-build`
- Migrating frameworks or dependencies with breaking changes -- use `adk-migrate`
- The refactor changes external API contracts -- that is a migration, not a refactor
- Documentation-only tasks
- The codebase has no tests and the refactor is high-risk -- add tests first via `adk-build`

### Pre-flight

Before starting, the preflight script (`scripts/preflight.py`) verifies:
- **git**: must be available in PATH (used for change tracking and diff analysis)
- **python3**: must be available in PATH (used for preflight checks and helper scripts)
- On macOS, missing commands produce `brew install` hints
- If any required command is missing, the skill stops with an actionable error

### Interaction Protocol

### Scope Confirmation (Phase 1)
Before making changes, confirm:
- The refactor scope and target area
- The behavior that must be preserved (regression contract)
- Whether tests exist to verify preservation
- Skip when `--auto` is set

### Plan Approval (Phase 3)
- Show the planned sequence of structural changes
- Present before/after structure sketches for key areas
- Wait for approval before executing
- Skip when `--auto` is set

### Progress Updates
- Report each refactor step as it completes
- Run regression checks and surface failures immediately
- Show subagent dispatch and results

### Results Presentation
- Present before/after structure for each changed area
- Include test/regression output
- State what structural gains were achieved
- Confirm behavior preservation evidence
- Ask whether more detail is needed

### Parallel Agents

| Agent | Dispatched When | Handle Inline When | Purpose |
| --- | --- | --- | --- |
| `adk-implementer` | Refactor spans 3+ files across modules with independent changes (e.g., rename across consumers) | Single-module refactors or tightly coupled structural changes | Focused file-level changes with scoped context |
| `adk-test-engineer` | Tests need updating to match new structure (imports, file paths) | Test changes are limited to import path updates | Verify test coverage still holds after structural changes |

Subagents report status as DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED. If behavior preservation is in doubt, verify before continuing.

### Validation

<test suite output or explicit "unverified" with reason>

### Summary

<1-2 sentence structural improvement description>

### Structural Changes

### Before
- <previous structure sketch>

### After
- <new structure sketch>

### Changed Files

- `path/to/file.ts` -- <one-line description>

### Migration Notes

- <notes for downstream consumers, if any API surface changed>

### Remaining Risk

- <open items, if any>

Need more detail on any section?
```

### Anti-Patterns / Red Flags

- Refactoring without capturing a behavior baseline (test run) first
- Changing multiple structural concerns in a single step
- Introducing abstractions that are not clearly better than the original
- Premature abstraction: extracting shared code before the third use case demands it
- Scope creep: fixing bugs or adding features during a refactor
- Skipping regression checks between steps -- run tests after each meaningful change, not just at the end
- Refactoring code that has no tests and high blast radius without flagging the risk
- Renaming across module boundaries without updating all consumers
- Modifying test assertions during a refactor -- this may mask regressions
- "While I'm here" expansion into files not in the refactor plan

### Related Skills

- `adk-brainstorm` -- settle acceptable refactor scope and blast radius first
- `adk-build` -- implement new features or fix bugs
- `adk-migrate` -- framework/dependency upgrades with breaking-change analysis
- `adk-review-local-changes` -- review refactored code before committing

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-refactor <prompt-text>
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
adk-refactor --scope <path> <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-refactor <prompt-text> --auto
```
