# `auto` — anti-patterns

## Process

- **Skipping Phase A.** Going straight from prompt to subagent dispatch loses the slug, the context-gather opportunity, and the approval surface.
- **Skipping context-gather when links are present.** The user pasted that Jira link because they expect you to read it. Always at least pull the title + status + acceptance criteria.
- **Skipping requirements + scoping.** Especially under `--auto`. The user can override at the gate but the agent never decides "the prompt is clear enough".
- **Implementing UI without 5 mockups.** This is the #1 reason designs feel "AI-slop". The 5-sample loop is the design step.
- **Skipping validate-browser after UI changes.** A green typecheck is not a working UI.
- **Skipping review-local before publish-commit.** The local self-review catches things the per-skill validators miss.
- **Auto-merging.** Never. Even under `--auto`. The PR is for humans to review.

## Reporting

- Mixing decisions + results + validation in one paragraph. Use the structured report.
- Hiding decisions made under `--auto`. List every one.
- Saying "validated" without a path to evidence.

## Subagent dispatch

- Spawning more than ~4 parallel subagents. Diminishing returns; coordination overhead grows.
- Spawning a subagent without a clear skill loaded. Always pass the skill name explicitly.
- Letting a subagent write outside `.temp/task-<slug>/`. Pass the path explicitly when spawning.

## Loop control

- Looping forever on a flaky validator. After 3 failures of the same kind, stop and ask the user.
- Treating CI yellow (warnings, not failures) as red. Surface yellows in the report; do not auto-loop.
