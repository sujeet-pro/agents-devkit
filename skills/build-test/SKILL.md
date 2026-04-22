---
name: build-test
description: Author or expand automated tests - unit, integration, end-to-end - to cover behavior, raise coverage, lock in a bug fix, or convert manual checks into repeatable validation. Use when the deliverable is test code, not implementation. Do not use when implementation is also changing in the same pass (use adk-build-feature, which can include tests inline).
metadata:
  category: build
  kind: task
  layer: 4
  modes: [auto]
---

# ADK Build / Test

Standalone task skill under the `@adk:build` (a.k.a. `adk-build`) category router. Produces tests that actually exercise the behavior they claim to cover, using the repo's existing test stack.

## When to use

- Author tests for an under-tested module.
- Add a regression test that locks in a bug fix.
- Convert a manual / one-off check into a repeatable test.
- Raise coverage on a specific surface (with rationale, not as a blanket %).

## When NOT to use

- Implementation also changes in the same pass -> `@adk:build-feature` (a.k.a. `adk-build-feature`) (write the test alongside)
- Refactor only -> `@adk:build-refactor` (a.k.a. `adk-build-refactor`) (use existing tests as the safety net)
- Test infrastructure migration (Jest -> Vitest) -> `@adk:build-migrate` (a.k.a. `adk-build-migrate`)
- Audit / analysis of test gaps without authoring -> `@adk:audit-repo` (a.k.a. `adk-audit-repo`)

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<target>` | yes | What to test (file, module, behavior, bug) |
| `<level>` | optional | `unit` / `integration` / `e2e` |
| `<framework>` | optional | Override repo default (vitest, jest, pytest, etc.) |
| `<scope>` | optional | Path to limit |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Confirm intent** - restate target, level, and framework. Approval gate unless `--auto`.
2. **Discover stack** - read `package.json` / `pyproject.toml` / config files to identify the test framework, runner, conventions, and existing test layout.
3. **Read target** - read the code under test and its dependencies; identify branches, edge cases, and side effects.
4. **Plan cases** - list test cases (happy path, edge cases, failure modes, regression for any reported bug). Approval gate unless `--auto`.
5. **Author** - write tests using the repo's existing patterns (helpers, fixtures, factories, naming convention). Each test asserts one thing where possible.
6. **Run** - run the tests. They must pass. They must also fail when the relevant code is broken (mutation check by hand or quick edit-revert).
7. **Validate (per `build-test-validator.md`)** - run the four-phase validator gate; capture evidence in `.temp/notes/build-test-<slug>-validator.md` before the final report.
8. **Coverage check** - if a coverage target was set, report before/after; otherwise report which branches are now exercised.
8. **Report** - test files added/changed, run output, coverage delta, gaps still open.

## Test design rules

- **AAA**: Arrange, Act, Assert. Keep them visually separated.
- **One reason to fail per test**. Multiple assertions are fine when they describe one behavior.
- **Test the public surface**. Avoid asserting on private implementation details that will churn.
- **Deterministic**. No flaky time / random / network calls; use fakes or fixed seeds.
- **Fast by default**. Slow tests go to a tagged integration / e2e layer.
- **Real failure mode**. A regression test must reproduce the bug *before* the fix and pass *after*.

## Coverage discipline

Coverage targets are not goals. Use coverage as a *map* of what is exercised, not a *score* to chase.

- Add tests where the gap matters (entrypoints, error paths, parsers, security boundaries).
- Do not add tests for trivial getters/setters just to raise the number.
- If the repo has a coverage gate, respect it; if it does not, do not invent one.

## Output format

```
## Tests authored: <target>

## Files
- `path/to/test.spec.ts` - <one-line description>

## Cases
- Happy path: <bullets>
- Edge cases: <bullets>
- Failure modes: <bullets>
- Regression: <bullet, with bug ref>

## Run
<command output>
- <N> passed
- <M> failed (must be 0)

## Coverage Delta (if measured)
- Before: <X%>
- After: <Y%>

## Gaps Still Open
- <bullet>

Need more detail on any section?
```

## Anti-patterns

- Tests that pass when the code is deleted (no real assertion).
- Mocking the system under test (test contracts, not implementations).
- Sleeping for time. Use fake timers.
- Snapshots over real assertions for behavior. Snapshots are for shape, not correctness.
- "Coverage farming": tests that touch lines without verifying behavior.
- Disabling failing tests. Either fix them or document why they were removed.

## Examples

```
adk-build-test "Cover the rate limiter edge cases" --target src/middleware/rate-limit.ts --level unit
```

```
adk-build-test "Lock in fix for issue #842 (auth header dropped on retry)" --level integration
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-test-clarifying-questions.md`) and reports the choices.

1. **What test type: unit, integration, end-to-end, contract, regression?** — _How to pick:_ Unit = pure functions / isolated modules. Integration = collaborating modules + real adapters. E2E = full user flow through deployed surface. Contract = API consumer/provider agreement. Regression = locks down a fixed bug.
2. **Is the work test-only, or are tests part of a larger feature/fix?** — _How to pick:_ Test-only → this skill. Tests-with-feature → adk-build-feature, with tests written in the same change.
3. **What coverage target — by line, by branch, by behavior?** — _How to pick:_ Behavior > branch > line. State the behaviors that must be covered, not a percent.

**Default report:** Scenario table (TC<n>: name / type / status / evidence) + coverage delta + blocked items.

**Detailed report (on request or `--verbose`):** Add: per-scenario setup/action/expected/actual, mock topology, fixture data sources, flake history if known.

**Artifact:** `test-suite` — Test files committed to the repo (matching project conventions) + scenario log in .temp/notes/.

**Artifact path:** .temp/notes/tests-<slug>-scenarios.md (scenario plan + evidence). Tests themselves land in tests/, src/__tests__/, etc., as repo conventions dictate.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-test-clarifying-questions.md`) and reports the choices.

1. **What test type: unit, integration, end-to-end, contract, regression?** — _How to pick:_ Unit = pure functions / isolated modules. Integration = collaborating modules + real adapters. E2E = full user flow through deployed surface. Contract = API consumer/provider agreement. Regression = locks down a fixed bug.
2. **Is the work test-only, or are tests part of a larger feature/fix?** — _How to pick:_ Test-only → this skill. Tests-with-feature → adk-build-feature, with tests written in the same change.
3. **What coverage target — by line, by branch, by behavior?** — _How to pick:_ Behavior > branch > line. State the behaviors that must be covered, not a percent.

## Default vs detailed output

**Default report:** Scenario table (TC<n>: name / type / status / evidence) + coverage delta + blocked items.

**Detailed report (on request or `--verbose`):** Add: per-scenario setup/action/expected/actual, mock topology, fixture data sources, flake history if known.

**Artifact:** `test-suite` — Test files committed to the repo (matching project conventions) + scenario log in .temp/notes/.

**Artifact path:** .temp/notes/tests-<slug>-scenarios.md (scenario plan + evidence). Tests themselves land in tests/, src/__tests__/, etc., as repo conventions dictate.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/build-test-anti-patterns.md` | Things to avoid when running this skill. |
| `references/build-test-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/build-test-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/build-test-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/build-test-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/build-test-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/build-test-persona.md` | The agent persona that drives this skill. |
| `references/build-test-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/build-test-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/build-test-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
