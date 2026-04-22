---
title: 'plan-roadmap'
description: 'Turn a settled goal into an ordered, file-aware implementation plan with milestones, dependencies, and validation gates.'
artifact_kind: skill
skill_name: plan-roadmap
category: plan
---
# plan-roadmap

Turn a settled goal into an ordered, file-aware implementation plan with milestones, dependencies, and validation gates. Use when direction and design are settled and the next step is to execute work in slices that can be reviewed, validated, and committed independently. Do not use when direction is still open (use adk-plan-brainstorm) or when an architecture write-up is needed (use adk-plan-design).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-plan-roadmap` form via `agents-skills/`.

```text
/adk:plan-roadmap            # interactive run (Claude Code)
/adk:plan-roadmap --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-plan-roadmap` (resolved through the
`agents-skills/adk-plan-roadmap/` symlink).

## Source

Direct from `skills/plan-roadmap/SKILL.md` — this page is auto-generated.

Standalone task skill under the `@adk:plan` (a.k.a. `adk-plan`) category router. Produces an ordered, file-aware implementation plan that an engineer (or `@adk:build-feature` (a.k.a. `adk-build-feature`)) can execute slice by slice.

## When to use

- The goal and approach are settled; only the *order* and *scoping* are open.
- The work is too large for a single sitting and must be broken into slices.
- Multiple contributors or sessions will pick up the work and need shared milestones.
- The deliverable is a plan markdown that drives subsequent build skills.

## When NOT to use

- Direction or design is still open -> `@adk:plan-brainstorm` (a.k.a. `adk-plan-brainstorm`) / `@adk:plan-design` (a.k.a. `adk-plan-design`)
- The change is one file and trivial -> just do it with `adk-build-feature` directly
- The plan exists already and reviewers want a critique -> use `@adk:review-local` (a.k.a. `adk-review-local`) against the plan

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
6. **Validate (per `plan-roadmap-validator.md`)** - run the four-phase validator gate; capture evidence in `.temp/notes/plan-roadmap-<slug>-validator.md` before the final report.
7. **Risk pass** - mark slices that touch risky areas, third parties, or migrations.
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

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/plan-roadmap-clarifying-questions.md`) and reports the choices.

1. **What is the source spec or design we are planning from?** — _How to pick:_ Pass a path to the spec/design markdown. If none, ask the user to run `@adk:plan-spec` (a.k.a. `adk-plan-spec`) or adk-plan-design first.
2. **What is the slice size you want: thin vertical slices (one user-visible behavior at a time) or layered (model → API → UI)?** — _How to pick:_ Vertical = ship value continuously, simpler review, harder coordination. Layered = easier per-team handoff, slower user value, riskier integration. Default = vertical for ≤5 engineers.
3. **Are there hard deadlines or external dependencies to respect?** — _How to pick:_ List them. Steps that depend on external parties get marked with a blocker tag and a fallback path.

**Default report:** Ordered step list (id, summary, files, validation, dependencies, effort).

**Detailed report (on request or `--verbose`):** Add: per-step risks, rollback strategy per step, parallelization graph (which steps can run concurrently), test-coverage delta per step.

**Artifact:** `implementation-roadmap` — Markdown roadmap. Sections: Source (spec/design link), Goals, Steps (numbered table: id/summary/files/validation/dependencies/effort), Parallelization, Open Risks, Rollback Strategy.

**Artifact path:** .temp/plans/roadmap-<slug>.md

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/plan-roadmap-clarifying-questions.md`) and reports the choices.

1. **What is the source spec or design we are planning from?** — _How to pick:_ Pass a path to the spec/design markdown. If none, ask the user to run adk-plan-spec or adk-plan-design first.
2. **What is the slice size you want: thin vertical slices (one user-visible behavior at a time) or layered (model → API → UI)?** — _How to pick:_ Vertical = ship value continuously, simpler review, harder coordination. Layered = easier per-team handoff, slower user value, riskier integration. Default = vertical for ≤5 engineers.
3. **Are there hard deadlines or external dependencies to respect?** — _How to pick:_ List them. Steps that depend on external parties get marked with a blocker tag and a fallback path.

## Default vs detailed output

**Default report:** Ordered step list (id, summary, files, validation, dependencies, effort).

**Detailed report (on request or `--verbose`):** Add: per-step risks, rollback strategy per step, parallelization graph (which steps can run concurrently), test-coverage delta per step.

**Artifact:** `implementation-roadmap` — Markdown roadmap. Sections: Source (spec/design link), Goals, Steps (numbered table: id/summary/files/validation/dependencies/effort), Parallelization, Open Risks, Rollback Strategy.

**Artifact path:** .temp/plans/roadmap-<slug>.md

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/plan-roadmap-anti-patterns.md` | Things to avoid when running this skill. |
| `references/plan-roadmap-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/plan-roadmap-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/plan-roadmap-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/plan-roadmap-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/plan-roadmap-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/plan-roadmap-persona.md` | The agent persona that drives this skill. |
| `references/plan-roadmap-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/plan-roadmap-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/plan-roadmap-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->


## Related skills

- [`build-feature`](./skill-build-feature.md) — `@adk:build-feature` (a.k.a. `adk-build-feature`)
- [`plan`](./skill-plan.md) — `@adk:plan` (a.k.a. `adk-plan`)
- [`plan-brainstorm`](./skill-plan-brainstorm.md) — `@adk:plan-brainstorm` (a.k.a. `adk-plan-brainstorm`)
- [`plan-design`](./skill-plan-design.md) — `@adk:plan-design` (a.k.a. `adk-plan-design`)
- [`plan-spec`](./skill-plan-spec.md) — `@adk:plan-spec` (a.k.a. `adk-plan-spec`)
- [`review-local`](./skill-review-local.md) — `@adk:review-local` (a.k.a. `adk-review-local`)
