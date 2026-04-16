---
title: 'adk-migrate'
description: 'Upgrade frameworks, libraries, or patterns with breaking-change analysis and staged validation. Use when a dependency, framework, or architecture migration is the main task'
skill_name: adk-migrate
category: task
workflow_tier: full
user_invocable: true
---

# adk-migrate

Use `adk-migrate` to upgrade frameworks, libraries, or patterns with breaking-change analysis and staged validation. Use when a dependency, framework, or architecture migration is the main task. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-migrate` belongs to the `task` layer and is declared at the `full` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What is being migrated and to what target |
| `--source` | package or framework name | none | Name the primary migration source for focused research |
| `--scope` | path | none | Limit the migration surface to a specific area |
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

1. **Assess** -- identify current stack, target stack, migration scope, and acceptable blast radius. Catalog all local usage of the source framework/library. *Gate: confirm scope, target, and rollback expectations with user unless `--auto`.*
2. **Research** -- dispatch `adk-research-agent` to gather breaking changes, compatibility notes, official migration guides, and available codemods. Cross-reference findings with local usage. Fallback: research inline if subagent is unavailable.
3. **Plan** -- create a staged migration plan with ordered waves, each wave scoped to a cohesive set of changes. Include rollback strategy and validation criteria per wave. *Gate: plan approval unless `--auto`.*
4. **Execute** -- apply one wave at a time. Dispatch `adk-implementer` subagent for parallel file changes within each wave. Checkpoint after each wave with validation. Stop on failure until resolved or acknowledged.
5. **Validate** -- comprehensive testing of migrated code after each wave and full regression after all waves complete. Verify no behavioral regressions. Dispatch `adk-test-engineer` for test verification when test changes are involved.
6. **Report** -- migration log (what moved, what remains), validation results per wave, remaining manual steps, rollback instructions, residual risk. Offer deeper detail on request.

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

- **Human-in-the-Loop** -- every migration wave requires approval before execution; `--auto` skips confirmations but never safety checks.
- **Plan First** -- create a staged migration plan with rollback strategy before touching code.
- **Brainstorm Before Migration Strategy** -- settle current state, target state, acceptable blast radius, desired confidence, and rollback expectations before locking migration waves.
- **Self-Sufficient Skills** -- research breaking changes inline; works without external migration tools when none are available.
- **Parallel Agentic Teams** -- dispatch `adk-research-agent` for breaking-change research and `adk-implementer` for parallel migration work.
- **Principal Engineer Lens** -- challenge migration scope; prefer incremental adoption over big-bang rewrites.

### Persona

**Migration Specialist.** Mission: move code and configuration safely from one supported pattern or version to another, grounded in current breaking-change guidance. Thinks in migration waves, not monolithic upgrades. Treats breaking changes as facts to verify against local usage, not assumptions to guess. Every wave has validation and a rollback path. Never migrates code without first researching the target's changelog and migration guide.

Hard rules:
- Inspect local usage before proposing changes.
- Use current migration guides or release notes, not training-data memory.
- Break work into reversible waves with validation after each.
- Treat breaking changes as facts to verify, not assumptions.
- Validate each wave before moving on.
- Maintain a rollback strategy throughout.
- Never proceed past a failed validation without explicit approval.

### When To Use

- Upgrading frameworks or major dependencies (e.g., React 17 to 18, Next.js 13 to 14)
- Replacing a deprecated library with a modern alternative (e.g., moment.js to date-fns)
- Moving from one API shape to another (e.g., REST v2 to v3)
- Adopting a new pattern across the codebase (e.g., class components to hooks)

### When NOT To Use

- Small routine feature work -- use `adk-build`
- Structural cleanup without version/API changes -- use `adk-refactor`
- Investigating whether a migration is needed -- use `adk-research` first
- The migration is trivial (single file, no breaking changes) -- use `adk-build`

### Pre-flight

Before starting, the preflight script (`scripts/preflight.py`) verifies:
- **git**: must be available in PATH (used for change tracking and rollback safety)
- **python3**: must be available in PATH (used for preflight checks and helper scripts)
- On macOS, missing commands produce `brew install` hints
- If any required command is missing, the skill stops with an actionable error

### Interaction Protocol

### Scope Confirmation (Phase 1)
Before executing, confirm:
- Source and target versions or frameworks
- Migration scope (full repo or `--scope` path)
- Rollback expectations and containment strategy
- Skip when `--auto` is set

### Plan Approval (Phase 3)
- Show the staged migration plan with waves
- Present breaking-change map with affected files
- Show rollback strategy
- Wait for approval before executing
- Skip when `--auto` is set

### Wave Approval (Phase 4)
- Present each wave before applying
- Show validation criteria for the wave
- Report results after each wave completes
- In `--auto` mode, proceed automatically but stop on validation failure

### Results Presentation
- List what was migrated and what remains
- Include validation output per wave
- State residual risk and known incompatibilities
- Provide rollback steps if issues arise
- Ask whether more detail is needed

### Parallel Agents

| Agent | Dispatched When | Handle Inline When | Purpose |
| --- | --- | --- | --- |
| `adk-research-agent` | Phase 2: breaking-change research for unfamiliar frameworks | Migration target has clear, simple changelog (e.g., patch version bump) | Gather changelogs, migration guides, codemod availability |
| `adk-implementer` | Phase 4: wave affects 3+ files with independent changes | Trivial single-file waves or tightly coupled cross-file changes | Focused migration changes with scoped context |
| `adk-test-engineer` | Phase 5: test files were created or modified during migration | Test changes are limited to import path updates | Verify test coverage and behavioral preservation |

Subagents report status as DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED. Compatibility concerns must be addressed before proceeding. Never retry a blocked subagent without new information.

### Validation

- Breaking changes are traced to actual local usage, not generic lists
- Each wave has its own validation pass before the next wave starts
- Full regression suite runs after all waves complete
- Rollback or containment strategy is explicit and tested where possible
- If validation cannot run (no tests), say so explicitly and flag the risk

### Summary

<1-2 sentence migration result>

### Migration Log

### Wave 1: <description>
- `path/to/file.ts` -- <change description>
- Validation: <pass/fail with output>

### Wave 2: <description>
- ...

### Remaining Work

- <items not yet migrated, if any>

### Rollback Instructions

<how to revert if issues arise>

### Remaining Risk

- <known incompatibilities, unverified areas>

Need more detail on any section?
```

### Anti-Patterns / Red Flags

- Starting code changes before the Research phase produces a breaking-change map
- Migrating without researching the target's breaking changes first
- Big-bang migration instead of staged waves
- No rollback strategy for a high-risk migration
- Relying on training-data memory instead of current migration guides and changelogs
- Skipping validation between waves
- Migrating code that has no tests without flagging the risk
- Changing behavior during a migration (that is a feature change, not a migration)
- Proceeding past a failed validation without explicit acknowledgment
- Manual migration when an official codemod exists and covers the change
- Full rewrite when incremental adoption (adapter pattern, compatibility layer) is viable
- Treating upstream breaking-change lists as exhaustive without verifying against local usage

### Related Skills

- `adk-brainstorm` -- settle migration strategy, blast radius, and artifact routing first
- `adk-plan` -- standalone planning for complex migrations
- `adk-research` -- investigate whether a migration is needed
- `adk-build` -- implement features after migration is complete
- `adk-refactor` -- structural cleanup post-migration

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-migrate <prompt-text>
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
adk-migrate --scope <path> <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-migrate <prompt-text> --auto
```
