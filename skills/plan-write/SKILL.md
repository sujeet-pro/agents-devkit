---
name: plan-write
description: Use when turning requirements into an execution plan that can be carried out by engineers or child-agent teams with minimal ambiguity
user_invocable: true
arguments:
  - name: feature
    description: "Feature or task to plan"
    required: true
  - name: scope
    description: "Plan scope: full, incremental (default: full)"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default, confirms at each step), auto-approve (proceeds without confirmation)"
    required: false
---

# Writing Plans

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

Plans should be executable by a human or by DevKit child-agent teams with minimal ambiguity.

## Preflight

Before creating a plan, run:

`zsh scripts/check-skill-deps.zsh plan-write`

## Plan Storage

Save all plans to `.temp/plans/<plan-id>.md` in the current working directory. If `.temp/` does not exist, create it and ensure it is listed in `.gitignore`.

Use this plan file format:

```markdown
---
plan_id: <short-id>
created: <ISO-8601>
updated: <ISO-8601>
skill: <skill-that-created-this>
status: draft | approved | in-progress | completed
---

# <Plan Title>

## Context
<Why this plan exists, what triggered it>

## Tasks

- [ ] Task 1: <description>
  - Files: <exact paths>
  - Verification: <command or check>
- [ ] Task 2: <description>
  ...
```

## Phase 0: Interactive Discussion

Before any planning work begins, identify "gray areas" — implementation decisions where the user's intent is unclear or ambiguous. This phase resolves uncertainty upfront so the plan is built on solid assumptions.

### Gray Area Categories

Look for ambiguity in these categories:

- **API shape** — endpoint design, request/response contracts, versioning
- **UI layout** — component structure, responsive behavior, interaction patterns
- **Error handling** — failure modes, retry strategies, user-facing messages
- **Naming conventions** — variables, files, modules, routes
- **Data flow** — state management, caching, synchronization
- **Architecture boundaries** — service boundaries, module ownership, shared code

### Capped Clarification

Ask a maximum of **5 questions**, prioritized by `Impact x Uncertainty` (highest first). If there are fewer than 5 gray areas, ask only what is needed.

Present each gray area interactively using this format:

```
## Clarification [N/total] - [category]

Context: <what part of the feature this affects>

Options:
A) <option with tradeoff>
B) <option with tradeoff>
C) <user-specified>

Your choice: [A] | [B] | [C] | [S]kip
```

### Bulk Skip

Support bulk resolution: if the user replies "skip all remaining", use the AI's best judgment for every unresolved gray area.

### Decision Log

Save all discussion outcomes to `.temp/plans/<plan-id>-context.md` with three sections:

```markdown
## Decisions
<!-- Locked — the user explicitly chose these -->

## Discretion
<!-- AI chooses — the user skipped or bulk-skipped these -->

## Deferred
<!-- Out of scope — acknowledged but not addressed in this plan -->
```

This context file is written alongside the plan file and should be referenced during task breakdown.

## Required Child Agents

Run at least these child agents in parallel:

- **Scope analyst**: reads the repository to identify affected files, existing patterns, and dependencies. Produces a scope brief with file inventory and dependency map.
- **Task planner**: breaks the feature into discrete, verifiable tasks with clear boundaries. Ensures tasks can be parallelized where possible and sequential where dependencies exist.
- **Review agent**: reviews the plan for gaps, missing dependencies, unclear ownership, and testability. Flags tasks that lack verification commands.

## Workflow

1. **Discussion.** Run Phase 0 to identify and resolve gray areas interactively. Save decisions to `.temp/plans/<plan-id>-context.md`.
2. **Analyze scope.** Launch the scope analyst to read the codebase and identify affected areas.
3. **Break down tasks.** Launch the task planner to create discrete, ordered tasks.
4. **Add verification.** Ensure every task has a verification command or check.
5. **Review.** Launch the review agent to check for gaps and feasibility.
6. **Write plan file.** Save the plan to `.temp/plans/<plan-id>.md`.
7. **Present for approval.** Show the plan to the user before execution.

## Plan Requirements

- Exact files and responsibilities per task
- Clear task boundaries so tasks can be parallelized
- Verification commands for each task
- Docs and migration follow-ups
- Review checkpoints after groups of related tasks

### Scope Categorization

Every item discovered during analysis must be categorized into one of three scope boundaries:

- **v1 (must-have)** — required for this plan; will be broken into tasks
- **v2 (future enhancement)** — tracked in the plan file under a "Future Work" section but not planned into tasks
- **out-of-scope** — explicitly excluded; listed so stakeholders know what was considered and rejected

Present the scope categorization to the user for interactive approval before proceeding to task breakdown. In `auto-approve` mode, present the categorization but continue without waiting for confirmation.

## Output

A plan file saved to `.temp/plans/` with the format above, ready for execution by `/devkit:plan-execute`.

## Adjacent Skills

- `/devkit:plan-brainstorm` for exploring options before planning
- `/devkit:plan-execute` for executing the plan
- `/devkit:plan-track` for monitoring plan progress
- `/devkit:dev-implement` for full implementation with built-in planning
