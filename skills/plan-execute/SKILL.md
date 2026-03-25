---
name: plan-execute
description: Use when you have a written implementation plan and want to execute it carefully with review checkpoints and optional child-agent support
---

# Executing Plans

## Plan Location

Look for plans in `.temp/plans/` in the current working directory. If the user provides a specific plan file path, use that instead.

## Resuming Plans

Before starting, scan the plan for the first unchecked step (`- [ ]`). Resume from there instead of restarting. This enables interrupted plans to be continued across sessions.

## Flow

1. Read the plan critically from `.temp/plans/<plan-id>.md`
2. Find the first unchecked step (`- [ ]`) to determine resume point
3. Ask about gaps before coding
4. Execute tasks in order, marking each as done (`- [x]`) in the plan file after completion
5. Verify each task using the verification command specified in the plan
6. Update the plan's `updated` timestamp and `status` field as you progress
7. Finish with branch review and cleanup

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

## Updating the Plan

After completing each task:
1. Mark the step as done: change `- [ ]` to `- [x]`
2. Update the `updated` timestamp in the frontmatter
3. If the task revealed new work, add new steps to the plan
4. When all steps are done, set `status: completed`
