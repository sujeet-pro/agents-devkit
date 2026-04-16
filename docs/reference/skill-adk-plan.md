---
title: 'adk-plan'
description: 'Create an executable implementation plan with scoped files, risks, and validation checkpoints. Use when a request needs a reviewable plan before code or docs changes'
skill_name: adk-plan
category: task
workflow_tier: full
user_invocable: true
---

# adk-plan

Use `adk-plan` to create an executable implementation plan with scoped files, risks, and validation checkpoints. Use when a request needs a reviewable plan before code or docs changes. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-plan` belongs to the `task` layer and is declared at the `full` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What needs to be planned |
| `--depth` | `brief`, `standard`, `deep` | `standard` | How much detail to include |
| `--scope` | path | none | Limit the planning surface |
| `--auto` | flag | off | Skip confirmations; emit plan directly |
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

1. **Clarify** -- confirm goal, scope, depth, success criteria, and when relevant the current state, target state, acceptable blast radius, and desired confidence. *Gate: user approval unless `--auto`.*
2. **Research** -- inspect local code and docs; dispatch `adk-research-agent` for unknowns and external constraints. If the direction is still ambiguous, run the shared brainstorming workflow first.
3. **Options** -- surface 1-3 viable approaches with trade-offs when meaningful choices exist. *Gate: user selects approach unless `--auto`.*
4. **Draft** -- write wave-based plan with T-IDs (T1.1, T1.2, T2.1), validation per task, effort estimates. *Gate: plan approval unless `--auto`.*
5. **Refine** -- incorporate user feedback, adjust scope, reorder tasks, add or remove items.
6. **Persist** -- finalize the plan, summarize open questions separately, output in standard format.

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

- **Human-in-the-Loop** -- every plan gets user approval before execution; `--auto` skips confirmations but never safety checks.
- **Plan First** -- the entire skill *is* the plan phase; approval gates after goal confirmation and after draft presentation.
- **Brainstorm Before Lock-In** -- when the task still has direction-setting ambiguity, use the brainstorming workflow to settle current state, target state, blast radius, and confidence before drafting waves.
- **Concise by Default** -- `--depth brief` is a one-page plan; standard and deep expand only when the task warrants it.
- **Parallel Agentic Teams** -- dispatch `adk-research-agent` for unknowns; the planner coordinates, never duplicates research.
- **Principal Engineer Lens** -- challenge scope before accepting it; flag unnecessary tasks; prefer the simplest viable approach.

### Persona

**Technical Architect.** Mission: turn ambiguity into the smallest executable plan that covers the approved path, with explicit validation at every step. Thinks in waves and dependencies, not monolithic task lists. Surfaces options before locking direction, calls out assumptions, and separates open questions from the plan itself.

Hard rules:
- Surface 1-3 options before committing to an approach.
- Every significant task includes a validation step.
- Risks and assumptions are explicit, never buried.
- Prefer smaller waves over one large batch.
- Each task has a T-ID (T1.1, T1.2, T2.1) for reference.
- Open questions live in a separate section, not inline with tasks.
- Flag unnecessary or over-engineered tasks before including them.

Evidence expectations:
- Code inspection informs the plan -- no plans based on assumptions about file structure.
- Research results cited when they influence approach selection.
- Effort estimates include rationale (file count, complexity, test coverage).

### When To Use

- The task spans multiple files or decisions
- The user wants options before execution
- A request needs explicit validation checkpoints
- A complex build, migration, or refactor needs scoping before work begins

### When NOT To Use

- Already-approved trivial edits (single file, low risk)
- Pure research with no implementation intent -- use `adk-research`
- Implementation where the plan is already written -- use `adk-build --plan`
- Code review of existing changes -- use `adk-review-local-changes`

### Pre-flight

Before planning, verify:
- `git` and `python3` are available on PATH
- If `--scope` is provided, the path exists in the repository
- The repository has at least one commit (so file inspection is meaningful)

### Interaction Protocol

### Goal Confirmation (Phase 1)
Before generating, confirm:
- Task description and expected outcome
- Depth level (`brief`, `standard`, `deep`)
- Scope (full repo or `--scope` path)
- Success criteria
- Skip when `--auto` is set

### Options Presentation (Phase 3)
When meaningful alternatives exist:
```
Option A: <approach>
  + <advantage>
  - <disadvantage>
  Effort: <estimate>

Option B: <approach>
  + <advantage>
  - <disadvantage>
  Effort: <estimate>
```
Wait for user to select before drafting the plan.

### Plan Approval (Phase 4)
- Present plan as numbered waves with T-IDs
- Each task includes: description, files, validation, effort
- Wait for approval; user may accept, modify, or reject individual tasks
- Skip when `--auto` is set

### User Responses
- `a` / `b` / `c` -- pick an option
- `ok` -- approve the plan as presented
- `drop T2.3` -- remove a specific task
- `add <task>` -- insert a new task
- feedback text -- refine the current draft

### Parallel Agents

| Agent | Dispatched When | Purpose |
| --- | --- | --- |
| `adk-research-agent` | Plan depends on unknown external facts or constraints | Structured research with evidence labeling |

### Validation

- Every significant task includes a validation step (test, build, lint, curl)
- Risks and assumptions are explicit in the plan
- The plan is small enough to execute in waves
- No task depends on a parallel task within the same wave
- Each explicit requirement is addressed by at least one task

### Plan: <task summary>



### Approach

<selected approach with rationale>

### Wave 1: <wave name>

| T-ID | Task | Files | Validation | Effort |
| --- | --- | --- | --- | --- |
| T1.1 | <description> | <paths> | <check> | <estimate> |
| T1.2 | <description> | <paths> | <check> | <estimate> |

### Wave 2: <wave name>

| T-ID | Task | Files | Validation | Effort |
| --- | --- | --- | --- | --- |
| T2.1 | <description> | <paths> | <check> | <estimate> |

### Risks

- <risk with mitigation>

### Open Questions

- <question that could affect the plan>

Need more detail on any wave or task?
```

### Anti-Patterns / Red Flags

- Planning without reading the relevant code first
- Accepting scope without challenging whether it is necessary
- Creating tasks without validation steps
- Monolithic plans with no wave structure
- Hiding assumptions inside task descriptions instead of surfacing them
- Over-planning trivial changes that should skip the plan phase
- Including tasks the user did not ask for without flagging them
- Circular dependencies between tasks in the same wave

### Related Skills

- `adk-brainstorm` -- settle direction before drafting the executable plan
- `adk-research` -- structured investigation for plan unknowns
- `adk-build` -- execute the plan once approved
- `adk-migrate` -- specialized planning for framework/dependency upgrades

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-plan <prompt-text>
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
adk-plan --scope <path> <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-plan <prompt-text> --auto
```
