---
title: 'scoping'
description: 'Converts confirmed requirements into a tight scope: in/out lists, blast radius, success criteria, milestones, dependencies, and rollback plan.'
artifact_kind: skill
skill_name: scoping
category: standalone
---
# scoping

Converts confirmed requirements into a tight scope: in/out lists, blast radius, success criteria, milestones, dependencies, and rollback plan. Produces `.temp/task-<slug>/scope.md`. Run after `@adk:requirements` (a.k.a. `adk-requirements`) is signed off, before any spec/design/build. Do not use to author the spec itself (use `@adk:plan-spec` (a.k.a. `adk-plan-spec`)).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-scoping` form via `agents-skills/`.

```text
/adk:scoping            # interactive run (Claude Code)
/adk:scoping --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-scoping` (resolved through the
`agents-skills/adk-scoping/` symlink).

## Source

Direct from `skills/scoping/SKILL.md` — this page is auto-generated.

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


## Related skills

- [`auto`](./skill-auto.md) — `@adk:auto` (a.k.a. `adk-auto`)
- [`plan-design`](./skill-plan-design.md) — `@adk:plan-design` (a.k.a. `adk-plan-design`)
- [`plan-roadmap`](./skill-plan-roadmap.md) — `@adk:plan-roadmap` (a.k.a. `adk-plan-roadmap`)
- [`plan-spec`](./skill-plan-spec.md) — `@adk:plan-spec` (a.k.a. `adk-plan-spec`)
- [`requirements`](./skill-requirements.md) — `@adk:requirements` (a.k.a. `adk-requirements`)
