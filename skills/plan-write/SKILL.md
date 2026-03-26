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

## Required Child Agents

Run at least these child agents in parallel:

- **Scope analyst**: reads the repository to identify affected files, existing patterns, and dependencies. Produces a scope brief with file inventory and dependency map.
- **Task planner**: breaks the feature into discrete, verifiable tasks with clear boundaries. Ensures tasks can be parallelized where possible and sequential where dependencies exist.
- **Review agent**: reviews the plan for gaps, missing dependencies, unclear ownership, and testability. Flags tasks that lack verification commands.

## Workflow

1. **Analyze scope.** Launch the scope analyst to read the codebase and identify affected areas.
2. **Break down tasks.** Launch the task planner to create discrete, ordered tasks.
3. **Add verification.** Ensure every task has a verification command or check.
4. **Review.** Launch the review agent to check for gaps and feasibility.
5. **Write plan file.** Save the plan to `.temp/plans/<plan-id>.md`.
6. **Present for approval.** Show the plan to the user before execution.

## Plan Requirements

- Exact files and responsibilities per task
- Clear task boundaries so tasks can be parallelized
- Verification commands for each task
- Docs and migration follow-ups
- Review checkpoints after groups of related tasks

## Output

A plan file saved to `.temp/plans/` with the format above, ready for execution by `/devkit:plan-execute`.

## Adjacent Skills

- `/devkit:plan-brainstorm` for exploring options before planning
- `/devkit:plan-execute` for executing the plan
- `/devkit:plan-track` for monitoring plan progress
- `/devkit:dev-implement` for full implementation with built-in planning
