---
title: 'scoping'
description: '|'
skill_name: scoping
category: standalone
---
# scoping — turn requirements into scope + milestones

## When to use

- After `requirements.md` is signed off.
- Before `plan-spec` / `plan-design` / `plan-roadmap`.

## When NOT to use

- Requirements are not yet captured. Run `@adk:requirements` first.
- The work is a one-line trivial change. Just do it.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<requirements.md>` | yes | Output of requirements skill |
| `<change-tolerance>` | optional | `surgical` / `bounded` / `transformative` (default: bounded) |
| `--auto` | optional | Pick documented defaults |

## Workflow

1. Read `.temp/task-<slug>/requirements.md` end-to-end.
2. Identify **blast radius**: which files / packages / repos / services touched. Use `rg` / `fd` / `gh` to be precise.
3. Confirm **change tolerance** with user (or `--auto` default = `bounded`).
4. Produce **in-scope list** (specific files / endpoints / components).
5. Produce **out-of-scope list** (every "non-goal" from requirements + anything tempting that the agent might drift into).
6. Define **success criteria** (testable; from requirements but specific to the slice).
7. Define **milestones**. 1-5 of them. Each is independently mergeable + reviewable.
8. Identify **dependencies** (other repos, other teams, infra).
9. Define **rollback plan** (how to revert; revert PR or feature flag).
10. Write `.temp/task-<slug>/scope.md`.
11. Approval gate: user signs off.

## Mode

`auto` only.

## Output

`.temp/task-<slug>/scope.md` (see `references/artifact-format.md`).

## Anti-patterns

- "Scope: everything in this folder." Be specific.
- Out-of-scope list with 0 items. Always think of one tempting drift to call out.
- Milestones that are too big to ship independently.
- No rollback plan.

## References

Standard set + `references/blast-radius-recipes.md` for the per-stack rg/fd snippets that map a requirement to touched files.
