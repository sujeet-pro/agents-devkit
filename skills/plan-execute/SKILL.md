---
name: plan-execute
description: Use when you have a written implementation plan and want to execute it carefully with review checkpoints and optional child-agent support
arguments:
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
---

# Executing Plans

## Plan Location

Look for plans in `.temp/plans/` in the current working directory. If the user provides a specific plan file path, use that instead.

## Resuming Plans

Before starting, scan the plan for the first unchecked step (`- [ ]`). Resume from there instead of restarting. This enables interrupted plans to be continued across sessions.

## Flow

1. Read the plan critically from `.temp/plans/<plan-id>.md`
2. Find the first unchecked step (`- [ ]`) to determine resume point
3. **Dependency analysis**: scan tasks for dependencies (file references, imports, sequential markers)
4. **Wave grouping**: independent tasks go in the same wave, dependent tasks wait for prior waves
5. Group tasks into waves and present:

```text
## Execution Plan - N waves

Wave 1 (parallel, N tasks): <task list>
Wave 2 (parallel, N tasks, depends on Wave 1): <task list>
Wave 3 (sequential, 1 task, depends on Wave 2): <task list>

Action: [P]roceed | [A]djust grouping | [R]eview plan
```

6. Ask about gaps before coding
7. Execute tasks wave by wave, marking each as done (`- [x]`) in the plan file after completion
8. Between waves, present a checkpoint:

```text
## Wave [N] Complete

Completed:
- [x] Task A ✓ (committed: abc123f)
- [x] Task B ✓ (committed: def456a)

Wave [N+1] ready (M tasks):
- [ ] Task C
- [ ] Task D

Action: [P]roceed | [R]eview changes | [A]djust plan | [S]ave & pause
```

9. Verify each task using the verification command specified in the plan
10. Update the plan's `updated` timestamp and `status` field as you progress
11. Finish with branch review and cleanup

## Child Agent Support

When child agents are available, use the following pattern for each planned task:

1. Launch one implementation child agent with full context (requirements, plan, architectural context)
2. After implementation, launch review child agents in parallel:
   - a spec/requirement review pass to verify what was built matches what was requested
   - a code quality review pass for correctness, tests, and maintainability
3. Fix issues surfaced by reviewers before moving to the next task
4. Run review passes in parallel when they do not edit the same files

Use `skills/_references/agentic-teams.md` for standard team shapes.

When child agents are not available, execute sequentially and still keep review checkpoints.

See prompt templates in `skills/plan-execute/prompts/` for implementer, spec-reviewer, and code-quality-reviewer dispatch.

## Deviation Rules

Child agents must follow these numbered rules when encountering unexpected issues during execution:

1. **Auto-fix bugs** -- broken behavior, errors, incorrect output caused by the current task. No user permission needed.
2. **Auto-add missing critical** -- missing error handling, auth checks, validation directly required by the task. No user permission needed.
3. **Auto-fix blocking** -- missing dependencies, wrong types, broken imports preventing task completion. No user permission needed.
4. **STOP and ask** -- architectural changes (new DB tables, framework switches, API contract changes). Present to user:

```text
## Deviation Detected - Architectural Change

Task: <current task>
Issue: <what was discovered>
Proposed change: <what the agent wants to do>

Action: [A]pprove | [R]eject (skip) | [M]odify approach
```

Only auto-fix issues DIRECTLY caused by the current task. Pre-existing issues go to the deferred-items section in the plan.

## Analysis Paralysis Guard

If a child agent makes 5+ consecutive Read/Grep/Glob calls without any Edit/Write/Bash action:

- Force a decision: write code (enough context gathered) OR report blocked with specific missing info
- Surface to user if the agent reports blocked

## Session Handoff Support

When the user selects "Save & pause" at a wave checkpoint:

1. Save handoff state to `.temp/handoff/<plan-id>.md`
2. Include in the handoff file:
   - Completed waves and their commit hashes
   - Current wave progress (which tasks finished, which remain)
   - Remaining waves and their task lists
   - Decisions made during execution
   - Blocked items and deferred issues

## Updating the Plan

After completing each task:
1. Mark the step as done: change `- [ ]` to `- [x]`
2. Create an atomic commit: `git commit -m "<type>(<plan-id>-<task-num>): <task description>"`
3. Update the `updated` timestamp in the frontmatter
4. If the task revealed new work, add new steps to the plan
5. When all steps are done, set `status: completed`
