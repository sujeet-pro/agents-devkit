---
title: 'build-bugfix'
description: '|'
skill_name: build-bugfix
category: router
---
# build-bugfix — root-cause + minimal patch + regression test

## When to use

- "X is broken." / "X returns the wrong value." / "X crashes when Y." / "Customer reports Z."
- A failing test that needs the underlying bug fixed (not just the test re-baselined).

## When NOT to use

- New behavior request → `@adk:build-feature` (a.k.a. `adk-build-feature`).
- Code shape change with no bug → `@adk:build-refactor` (a.k.a. `adk-build-refactor`).
- Test-only change → `@adk:build-test` (a.k.a. `adk-build-test`).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<bug description>` | yes | What's broken |
| `<repro>` | yes | Steps to reproduce, OR a failing test, OR a Slack/Jira link (call `@adk:context-gather` first) |
| `<scope>` | optional | Path filter |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Phase 1 validator.** Repro is concrete (not "sometimes it doesn't work").
2. **Reproduce.** Run the repro steps. Confirm the bug is observable. If you can't reproduce, STOP and ask the user.
3. **Root-cause analysis.** Read code along the failing path. Trace inputs to outputs. Form a hypothesis. Confirm by adding a temporary `console.log` or `debugger` if needed (remove before commit). Write the root cause in `.temp/task-<slug>/root-cause.md`.
4. **Minimal patch.** Write the smallest correct change. Resist the urge to "while I'm here, also clean up X" — that goes in a separate PR.
5. **Regression test.** Write a test that FAILS without the patch and PASSES with it. Commit the test in the same PR.
6. **Browser verify (UI bugs only).** Call `@adk:validate-browser --mode verify-fix --repro .temp/task-<slug>/root-cause.md`.
7. **Phase D1 self-review.** `@adk:review-local`.
8. **Report.** Root cause, patch summary, test added, browser verification (if UI), residual risk.

## Mode

- `auto` (default): full loop with approval gates between phases.
- `fix`: same as auto but no approval gate (fully unattended). Intended for CI / `--auto` chains.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/root-cause.md` | The root-cause analysis |
| `.temp/task-<slug>/plan.md` | The minimal patch plan |
| `.temp/task-<slug>/browser-validation/verify-fix/` | Browser evidence (if UI) |
| `.temp/task-<slug>/report.md` | Final report |

## Anti-patterns

- "Fixing" by re-baselining a test.
- Removing an assertion to make a test pass.
- Patching the symptom not the cause.
- Mixing the bugfix with unrelated cleanup.
- Skipping the regression test ("the original failing test covers it" — only true if there WAS a failing test).
- Not verifying the bug is reproducible BEFORE patching.

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Bug → root-cause → patch → test → verify flow |
| `references/modes.md` | auto + fix |
| `references/persona.md` | The bugfixer |
| `references/workflow.md` | Detailed steps |
| `references/clarifying-questions.md` | Repro confirmation, UI/non-UI |
| `references/root-cause-template.md` | Shape of root-cause.md |
| `references/output-format.md` | Final report shape |
| `references/artifact-format.md` | Where outputs live |
| `references/validator.md` | Four-phase gate (incl. test-fails-without-patch check) |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | Worked bugfix examples |
| `references/interaction-contract.md` | Synced from canonical |
