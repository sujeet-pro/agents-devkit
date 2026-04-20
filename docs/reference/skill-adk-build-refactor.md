---
title: 'adk-build-refactor'
description: 'Restructure code without changing observable behavior - rename, extract, inline, dedupe, simplify, reshape modules - while keeping tests green throughout. Use when the goal is a cleaner shape, not a new behavior or bug fix. Do not use when behavior changes (use adk-build-feature), framework versions change (use adk-build-migrate), or only tests change (use adk-build-test).'
skill_name: adk-build-refactor
category: task
---

# adk-build-refactor

Restructure code without changing observable behavior - rename, extract, inline, dedupe, simplify, reshape modules - while keeping tests green throughout. Use when the goal is a cleaner shape, not a new behavior or bug fix. Do not use when behavior changes (use adk-build-feature), framework versions change (use adk-build-migrate), or only tests change (use adk-build-test).

## Skill body

# ADK Build / Refactor

Standalone task skill under the `adk-build` category router. Improves code structure with a behavior-preserving sequence of small, individually validated steps.

## When to use

- Rename, extract, inline, or move code while preserving behavior.
- Deduplicate parallel implementations.
- Simplify a tangled module without changing what it does.
- Replace an internal abstraction with a clearer one (signatures change, behavior does not).

## When NOT to use

- Behavior changes -> `adk-build-feature`
- Framework / runtime / library version migration -> `adk-build-migrate`
- Only tests change -> `adk-build-test`
- Dependency cleanup only -> `adk-build-deps`
- UI / frontend restructure -> `adk-frontend-feature`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<refactor>` | yes | What to restructure (e.g. "extract auth helpers from controllers") |
| `<scope>` | optional | Path to limit reads and changes |
| `<safety bar>` | optional | `tests-required` (default) / `manual-only` (when no tests exist) |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Confirm intent** - restate what changes structurally and what must NOT change behaviorally. Approval gate unless `--auto`.
2. **Baseline** - run the existing test suite (or document the manual baseline) and capture green status. No refactor starts on red.
3. **Map** - inventory call sites, public APIs, and dependents that the refactor will touch. Read; do not guess.
4. **Plan** - cut into small behavior-preserving steps (rename -> move -> extract -> inline). Each step ends with passing tests.
5. **Step-by-step execute** - apply one step, run tests, commit (or stage), repeat. Never batch two structural changes between validations.
6. **Diff review** - re-read the cumulative diff for accidental behavior changes (extra checks added, error messages changed, defaults changed).
7. **Report** - changed files; final test status; what was renamed / moved / extracted; what callers must update if any public API changed.

## Behavior-preservation rules

- Tests must be green before, between, and after each step.
- Do not "improve" error messages or default values during refactor; that is a feature change - extract it.
- If you must change a public API, list every external caller in the report.
- New abstractions added during refactor must be used somewhere right now; do not leave dead code "for future use".
- If a refactor exposes a real bug, stop, surface it, and let the user choose to fix in a separate `adk-build-feature` pass.

## Common refactor patterns

| Pattern | When | Notes |
| --- | --- | --- |
| Rename | Naming is misleading | Keep semantic meaning; update all call sites in one step |
| Extract function / module | Unit is too large or duplicated | Verify behavior preserved by tests at each extraction |
| Inline | Indirection adds no value | Inline first, then simplify |
| Move | File is in the wrong place | Move alone; do not also rename in the same step |
| Replace conditional with polymorphism | Branch explosion on type tag | Tests must cover each branch first |
| Introduce parameter object | Long parameter list with cohesion | Migrate callers one at a time |
| Dedupe | Two near-identical code paths | Extract common, keep differences explicit |

## Output format

```
## Refactor: <summary>

## Behavior Preserved
- Tests: <command> - PASS
- Manual checks: <bullets if any>

## Changed Files
- `path/to/file.ts` - <one-line description>

## Public API Changes
- <none, or list with caller impact>

## Steps Taken
1. <step>
2. <step>

## Remaining Risk
- <open item>

Need more detail on any section?
```

## Anti-patterns

- Mixing a behavior change into a refactor pass. Split it.
- Refactoring on red. Stabilize tests first.
- Renaming and moving in the same step. One change per validation.
- Adding "extension points" or interfaces with one implementation. YAGNI.
- Marking the refactor done while the diff still has commented-out code.
- Skipping the baseline test run. Without it you cannot prove behavior preservation.

## Examples

```
adk-build-refactor "Extract HTTP retry helper from each controller into src/http/retry.ts" --scope src/controllers/
```

```
adk-build-refactor "Inline the single-call AuthFacade and delete it" --scope src/auth/
```

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
