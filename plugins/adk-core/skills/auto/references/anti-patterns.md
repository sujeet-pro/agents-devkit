# `auto` — anti-patterns

## Process

- **Skipping Phase 0.** Going straight from prompt to dispatch loses the slug, the context-gather opportunity, and the approval surface.
- **Skipping context-gather when links are present.** The user pasted that Jira link because they expect you to read it. Always at least pull title + status + acceptance criteria.
- **Skipping preflight.** A skill that fails because `DD_API_KEY` is missing is a poor user experience; the preflight catches it once at the top.
- **Inventing a skill name.** If the verb doesn't map, stop and ask — never dispatch to `/adk-code:fix-bug` (no such skill; the real one is `code-bugfix`).
- **Auto-merging.** Never. Even under `--auto`. The PR is for humans to review.

## Reporting

- Mixing decisions + results + validation in one paragraph. Use the structured report.
- Hiding decisions made under `--auto`. List every one in the Decisions table.
- Saying "validated" without a path to evidence.

## Subagent dispatch

- Spawning more than 4 parallel subagents. Coordination overhead grows; diminishing returns.
- Spawning a subagent without a skill loaded. Always pass the skill name explicitly.
- Letting a subagent write outside `.temp/task-<slug>/`. Pass the path explicitly when spawning.
- Re-spawning a failed subagent on the same input without changing the inputs.

## Loop control

- Looping forever on a flaky validator. After 3 failures of the same kind, stop and ask the user.
- Treating CI yellow (warnings, not failures) as red. Surface yellows in the report; do not auto-loop.
- Re-running `context-gather` on the same links — once is enough per session.

## Classification

- Defaulting to `code-write` when the prompt says "fix" — that's `code-bugfix`.
- Treating a bare PR URL as needing classification — it's always `review-pr`.
- Routing "ship the experiment" to `code-write` — it's `investigate-experiment` first, then a code change only if the verdict is "ship".
