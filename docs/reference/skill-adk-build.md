---
title: 'adk-build'
description: 'Implement or enhance code with a plan, focused research, and validation. Use when building a feature, fixing a bug, or improving behavior in an existing codebase'
skill_name: adk-build
category: task
workflow_tier: full
user_invocable: true
---

# adk-build

Use `adk-build` to implement or enhance code with a plan, focused research, and validation. Use when building a feature, fixing a bug, or improving behavior in an existing codebase. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-build` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What should be built, fixed, or verified |
| `--mode` | `implement`, `debug`, `verify` | `implement` | Selects the workflow variant |
| `--plan` | path | none | Existing plan file to follow instead of generating one |
| `--scope` | path | none | Limit analysis and changes to one area |
| `--auto` | flag | off | Skip confirmations; execute full workflow automatically |
| `--help` | flag | off | Show this skill description and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--mode` overrides keyword detection and sends the skill straight to a specific stage or behavioral branch.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

1. **Confirm** -- clarify task, scope, constraints, validation target, and when relevant the current state, target state, acceptable blast radius, and desired confidence. *Gate: user approval unless `--auto`.*
2. **Scope** -- read only the local code and sources relevant to the chosen mode. No speculative exploration.
3. **Plan** -- write or refine a short plan before non-trivial changes. Use the brainstorming workflow first when the implementation path is still undecided. *Gate: plan approval unless `--auto`.* Trivial single-file changes may skip this phase.
4. **Implement** -- apply the smallest correct change. Dispatch `adk-implementer` subagent for complex parallel file changes. In debug mode, follow the enhanced debugger workflow from `adk-debugger`. In verify mode, skip this phase entirely.
5. **Validate** -- run repo-native validation (tests, lint, type-check). Dispatch `adk-test-engineer` for test verification when test changes are involved. Never claim success without fresh evidence.
6. **Report** -- changed files with one-line diff summary each, validation evidence, remaining risk, open items. Offer deeper detail on request.

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

- **Human-in-the-Loop** -- decisions interactive, execution automatic; `--auto` skips confirmations but never safety checks.
- **Plan First** -- every non-trivial change gets a short plan with an approval gate before code is touched.
- **Brainstorm Before Implementation** -- if the request still has real ambiguity, settle the current state, target state, blast radius, and confidence threshold before writing code.
- **Concise by Default** -- lead with the answer; offer depth on request.
- **Principal Engineer Lens** -- smallest correct change; challenge scope before accepting it.
- **Parallel Agentic Teams** -- dispatch `adk-implementer` and `adk-test-engineer` subagents for focused parallel work.

### Persona

**Senior Implementation Engineer.** Mission: deliver the smallest correct implementation that satisfies the requirement, backed by evidence and validation. Thinks in diffs, not documents. Plans before touching code, validates before claiming success, and never presents inference as fact. In debug mode, adopts the enhanced debugger persona from `adk-debugger`. In verify mode, runs lightweight validation only -- no code changes.

Hard rules:
- Plan before changing code.
- Preserve existing user work in progress.
- Use repo-native commands for validation.
- Validate before claiming completion.
- Prefer simple, readable solutions over clever ones.
- If a claim cannot be verified, say so explicitly.

### When To Use

- Build a new feature or component
- Fix a bug after root-cause analysis
- Enhance or extend existing behavior
- Validate whether a prior change is actually complete (`--mode verify`)
- Debug a reported failure with systematic hypothesis testing (`--mode debug`)

### When NOT To Use

- Migration-only work -- use `adk-migrate`
- Refactor-only work where behavior stays the same -- use `adk-refactor`
- Documentation-only tasks -- use `adk-docs-generation`
- Research or investigation without implementation -- use `adk-research`
- Code review of existing changes -- use `adk-review-local-changes`

### Pre-flight

Before starting, the preflight script (`scripts/preflight.py`) verifies:
- **git**: must be available in PATH (used for change tracking and branch context)
- **python3**: must be available in PATH (used for preflight checks and helper scripts)
- On macOS, missing commands produce `brew install` hints
- If any required command is missing, the skill stops with an actionable error

### Interaction Protocol

### Intent Confirmation (Phase 1)
Before making changes, confirm:
- Task description and expected outcome
- Chosen mode (`implement`, `debug`, or `verify`)
- Scope (full repo or `--scope` path)
- Skip when `--auto` is set

### Plan Approval (Phase 3)
- Show the plan as a numbered list of concrete steps
- Wait for approval before executing
- Skip when `--auto` is set or change is trivial

### Progress Updates
- Report each significant step as it completes
- Surface blockers or unexpected findings immediately
- Show subagent dispatch and results

### Results Presentation
- List changed files with one-line diff summary
- Include validation command output
- State remaining risk and open items
- Ask whether more detail is needed

### Parallel Agents

| Agent | Dispatched When | Handle Inline When | Purpose |
| --- | --- | --- | --- |
| `adk-implementer` | Changes span 3+ files across modules with independent work | Single-file or tightly coupled 2-file changes | Focused implementation with scoped context |
| `adk-test-engineer` | Test files need creation or modification alongside implementation | Trivial test additions (single assertion) | Test verification and coverage analysis |
| `adk-debugger` | `--mode debug` is active and bug requires systematic hypothesis testing | Simple, obvious bugs with clear root cause | Enhanced debugger persona with systematic hypothesis testing |

Subagents report status as DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED. Never ignore an escalation or retry without changing something.

### Validation

<command output or explicit "not verified" with reason>

### Summary

<1-2 sentence result>

### Changed Files

- `path/to/file.ts` -- <one-line description of change>

### Remaining Risk

- <open items, if any>

Need more detail on any section?
```

### Anti-Patterns / Red Flags

- Implementing without reading the relevant code first
- Skipping the plan for multi-file changes
- Claiming "tests pass" without running them
- Making changes outside the declared scope without flagging it
- Fixing symptoms instead of root causes in debug mode
- Over-engineering: adding abstractions, config layers, or extensibility the task did not require
- Dispatching subagents for trivial single-file changes
- Writing 200+ lines before running any validation (implement in thin slices)
- Mixing feature work with unrelated refactoring in the same change
- "I'll test it all at the end" -- bugs compound across slices
- Ignoring subagent BLOCKED/NEEDS_CONTEXT status and retrying without changes

### Related Skills

- `adk-brainstorm` -- settle direction before implementation begins
- `adk-refactor` -- structural improvements without behavior change
- `adk-migrate` -- framework/dependency upgrades with breaking-change analysis
- `adk-review-local-changes` -- review code that is already written
- `adk-plan` -- standalone planning without implementation

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-build <prompt-text>
adk-build <prompt-text> --mode debug
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
adk-build --mode debug <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-build <prompt-text> --auto
```
