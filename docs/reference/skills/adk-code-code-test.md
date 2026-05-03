---
title: 'adk-code:code-test'
description: '  Author or expand automated tests — unit, integration, end-to-end — to cover behavior, raise coverage on a target module, lock in a previously-shipped fix, or convert manual checks into repeatable validation. Each test is named by behavior (not by function), fails first (red), then is committed (green); covers happy path + at least one boundary + at least one error per behavior. Use when the deliverable is test code, not implementation. Do NOT use to fix a bug (use `/adk-code:code-bugfix` — it adds the regression test as part of the fix), to write production code (use `/adk-code:code-write`), to design an API surface (use `/adk-code:code-api`), to migrate a framework (use `/adk-code:code-migrate`), to tune perf (use `/adk-code:code-perf`), or to add security tests for an unfixed CVE (use `/adk-code:code-security`).'
plugin: 'adk-code'
skill: 'code-test'
source: 'plugins/adk-code/skills/code-test/SKILL.md'
group: 'code-skills'
order: 1107
---
# adk-code:code-test

## Source

`plugins/adk-code/skills/code-test/SKILL.md`

## Skill Body

# code-test — author or expand automated tests

A Principal Engineer's "tests are evidence" skill. Behavior-named tests, fail-first then green, observable assertions, no SUT mocks, no vacuous coverage.

## When to use

- "backfill tests for the order-state machine"
- "raise coverage on the discount calculator"
- "convert the manual smoke checks for `/api/orders` into automated tests"
- "add e2e tests for the checkout flow"
- "write tests for the new exporter module that doesn't have any"

## When NOT to use

| If the prompt is about | Use instead |
| --- | --- |
| Fix a bug | `/adk-code:code-bugfix` (it adds the regression test as part of the fix) |
| Write new production code | `/adk-code:code-write` (the test-engineer agent helps with the new tests) |
| Design / evolve an API surface | `/adk-code:code-api` |
| Migrate a framework | `/adk-code:code-migrate` |
| Performance regression | `/adk-code:code-perf` |
| Security mitigation | `/adk-code:code-security` (boundary-test the mitigation) |
| Refactor without behavior change | `/adk-code:code-refactor` (existing tests are the safety net; don't add new ones in the same diff) |

## Common prompts (auto-route triggers)

| Prompt pattern | Notes |
| --- | --- |
| "add tests for X" / "backfill tests for X" | Default match. |
| "raise coverage on X" / "X coverage is too low" | |
| "convert manual checks for X to tests" | |
| "lock in the fix for X with a test" | Standalone — if mid-bugfix, that's `code-bugfix`. |
| "add e2e for the … flow" | E2E variant. |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<target>` | yes | the module / endpoint / flow to cover |
| `--unit` | optional | force unit tests |
| `--integration` | optional | force integration tests |
| `--e2e` | optional | force e2e tests |
| `--coverage` | optional | run coverage at the end + report delta |
| `-i` / `--interactive` | optional | per-phase approval; mutually exclusive with `--auto` |
| `--auto` | optional | (default) skip per-phase approval gates |

If no `--unit/--integration/--e2e` flag, the skill picks based on the target's nature:

- A pure helper / function → unit.
- An HTTP endpoint / DB-touching service → integration.
- A user-facing flow → e2e (only if the repo has an e2e harness).

## Workflow

```
Phase 0 — prompt expand
  - Restate target. Identify scope (unit / integration / e2e).
  - Resolve repo via repos.md. Identify the test framework + runner from
    package.json / pyproject.toml / build.gradle.
  - Pick task slug; create .temp/task-<slug>/.

Phase 1 — preflight
  - git status clean (dirty → ask).
  - test command resolved + tests pass on HEAD.

Phase 2 — read the target + existing tests
  - Read the target module end-to-end.
  - Read every existing test file for the target (test conventions cue).
  - Read AGENTS.md / CLAUDE.md for testing rules.

Phase 3 — enumerate behaviors
  - List the behaviors to cover. For each:
      - Happy path (one).
      - Boundary (one — the one that matters most).
      - Error (one — the one that matters most).
  - Save to .temp/task-<slug>/behaviors.md.
  - Approval gate unless --auto.

Phase 4 — author tests (test-engineer subagent)
  - For each behavior trio, author the tests.
  - Verify fail-first (mutate SUT → red → restore → green) for every test.
  - Capture the red→green transition to validation log.

Phase 5 — validate
  - Run the new tests; iterate until green.
  - Run the full affected-package suite; confirm no regressions.
  - (Optional) Run coverage; capture delta.

Phase 6 — report
  - .temp/task-<slug>/report.md: tests added, behaviors covered, behaviors
    NOT covered (with reason), coverage delta (if --coverage).
```

See `references/workflow.md` for the detailed step list.

## Persona

> "Tests are evidence." Each test is named after the behavior it asserts. Each test fails first (commented-out implementation, run, observe red) before being committed. Coverage is a side-effect, not the goal. Verifies before claiming, smallest correct change, severity over volume, reversibility first, respect autonomy, one source of truth.

See `references/persona.md`.

## Constitution

**Must do:**

1. Name tests after the behavior they assert, not the function name.
2. For every new test, verify the fail-first transition (mutate SUT → red → restore → green) and document it.
3. Per behavior: cover happy path + at least one boundary + at least one error.
4. Assert on observable behavior (return value, status code, side effect), not internal state.
5. Match the repo's test idioms (file location, naming, framework dialect).

**Must not do:**

1. Test private internals (testing the implementation, not the behavior).
2. Mock the system under test.
3. Write trivially-passing tests for coverage numbers ("vacuous coverage").
4. Disable / skip an existing test to make a new one pass.
5. Push, commit, or open a PR.
6. Add tests in the same diff as a bug fix (that's `code-bugfix`).

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- 100% coverage with vacuous assertions.
- Tests that pass without the implementation (didn't fail-first).
- Mocks of the system under test.
- One giant test asserting 17 things.
- Snapshot tests on a 5-page object.
- Tests named after functions, not behaviors.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/prompt.txt` | Verbatim user prompt + ISO timestamp |
| `.temp/task-<slug>/behaviors.md` | Behavior list + the trio per behavior |
| `.temp/task-<slug>/validation/per-skill/code-test.md` | Test-engineer hand-off + fail-first evidence |
| `.temp/task-<slug>/report.md` | Final report with tests added + coverage delta (if `--coverage`) |

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Tests-are-evidence persona + status banner |
| `references/workflow.md` | Detailed Phase 0–6 stage list |
| `references/modes.md` | What `--auto` and `-i` mean for `code-test` |
| `references/interaction-contract.md` | Canonical interaction contract |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 4 worked examples (unit, integration, e2e, coverage) |
| `references/output-format.md` | Shape of `behaviors.md`, `report.md` |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase validation gates (esp. fail-first verification) |
| `references/how-it-works.md` | Mermaid diagrams: phase flow + behavior-enumeration tree |
| `references/clarifying-questions.md` | Questions Phase 0/3 may ask under `-i` |
| `references/test-naming-conventions.md` | Behavior-named test naming guide (across frameworks) |

## Additional links

The skill may WebFetch these for extra context when relevant:

- The test framework's docs (Vitest, Jest, pytest, JUnit, etc.) for idiomatic patterns.
- The repo's CONTRIBUTING.md for any documented testing rules.
