---
title: 'adk-plan-roadmap'
description: 'Turn a settled goal into an ordered, file-aware implementation plan with milestones, dependencies, and validation gates. Use when direction and design are settled and the next step is to execute work in slices that can be reviewed, validated, and committed independently. Do not use when direction is still open (use adk-plan-brainstorm) or when an architecture write-up is needed (use adk-plan-design).'
skill_name: adk-plan-roadmap
category: task
---

# adk-plan-roadmap

Turn a settled goal into an ordered, file-aware implementation plan with milestones, dependencies, and validation gates. Use when direction and design are settled and the next step is to execute work in slices that can be reviewed, validated, and committed independently. Do not use when direction is still open (use adk-plan-brainstorm) or when an architecture write-up is needed (use adk-plan-design).

## Skill body

# ADK Plan / Roadmap

Standalone task skill under the `adk-plan` category router. Produces an ordered, file-aware implementation plan that an engineer (or `adk-build-feature`) can execute slice by slice.

## When to use

- The goal and approach are settled; only the *order* and *scoping* are open.
- The work is too large for a single sitting and must be broken into slices.
- Multiple contributors or sessions will pick up the work and need shared milestones.
- The deliverable is a plan markdown that drives subsequent build skills.

## When NOT to use

- Direction or design is still open -> `adk-plan-brainstorm` / `adk-plan-design`
- The change is one file and trivial -> just do it with `adk-build-feature` directly
- The plan exists already and reviewers want a critique -> use `adk-review-local` against the plan

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<goal>` | yes | What the plan delivers when fully executed |
| `<scope>` | optional | Path or system surface |
| `<output path>` | optional | Defaults to `.temp/plans/<slug>.md` |
| `<deadline>` | optional | Used to pace milestones |
| `--auto` | optional | Skip approval gate |

## Workflow

1. **Confirm intent** - restate goal, scope, deadline, and constraints. Approval gate unless `--auto`.
2. **Map** - enumerate the surface: which files, modules, services, configs, tests will change. Read code first; do not guess.
3. **Slice** - cut the work into vertical slices that each leave the codebase buildable, testable, and (ideally) committable.
4. **Order** - sequence slices by dependency; mark parallel-safe groups.
5. **Gate** - for each slice define the validation that proves it is done (test command, lint, type-check, manual check).
6. **Risk pass** - mark slices that touch risky areas, third parties, or migrations.
7. **Report** - return the plan path, slice count, parallel groups, and the first slice with its files.

## Plan template

```markdown
# Plan: <goal>

## TL;DR
<3 bullets>

## Scope
- In: <bullets>
- Out: <bullets>

## Slices
### Slice 1: <name>
- Goal: <one sentence>
- Files: `<path>`, `<path>`
- Steps:
  1. <action>
  2. <action>
- Validation: `<command>` should <expected>
- Risk: <none | low | medium | high>
- Depends on: <none | Slice X>

### Slice 2: <name>
...

## Parallel Groups
- Group A: Slice 2, Slice 4 (no shared files)
- Group B: Slice 5, Slice 6 (after Slice 3)

## Open Questions
- <question>

## Done When
- <criteria 1>
- <criteria 2>
```

## Slicing rules

- Each slice changes < ~200 lines and < ~5 files when possible.
- Each slice has its own validation step. No "we'll test at the end".
- Each slice is committable on its own; if not, document why.
- Mark a slice "spike" only when its outcome is information, not code.
- Never put a destructive irreversible step into the same slice as exploratory work.

## Output format

```
## Plan ready
- File: <path>
- Slices: <count>
- Parallel groups: <count>
- First slice: <name>
  - Files: <list>
  - Validation: <command>

Ready to hand off to `adk-build-feature`?
```

## Anti-patterns

- One giant "implement everything" slice. Cut harder.
- Slices that share the same file with circular dependencies between them.
- Validation steps like "looks right" or "no obvious errors". Be concrete.
- Hiding scope creep inside slice 9. Out-of-scope work goes to a follow-up plan.
- Authoring code in the plan. The plan describes; build executes.

## Examples

| User says | Plan shape |
| --- | --- |
| "Add SSO to the admin panel" | Slices: discover identity provider, add config, wire login flow, gate routes, tests, rollout flag. |
| "Migrate from Express 4 to 5" | Slices: pin Express 5, fix breaking middlewares per file group, regenerate types, run integration suite, remove shims. Mark middlewares group as parallel-safe. |

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/working-artifacts.md` | The .temp/ rule for intermediate artifacts. |

<!-- adk:references:end -->

## References shipped with this skill

- `references/anti-patterns.md`
- `references/constitution.md`
- `references/examples.md`
- `references/output-format.md`
- `references/persona.md`
- `references/working-artifacts.md`
