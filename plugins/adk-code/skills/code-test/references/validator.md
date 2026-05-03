# `code-test` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/code-test.md`.

## Phase 0 — pre-execution

- [ ] `.temp/task-<slug>/` exists; `.temp/` is gitignored.
- [ ] User's prompt captured in `prompt.txt`.
- [ ] Repo resolved.
- [ ] Target identified (file / module / endpoint / flow).
- [ ] Test framework + runner identified from `package.json` / `pyproject.toml` / `build.gradle`.
- [ ] Test type (unit / integration / e2e) decided (forced by flag or auto-picked).
- [ ] Slug derived.

## Phase 1 — preflight

- [ ] `git status` clean. Dirty → ask.
- [ ] Branch captured. Protected → branch-creation prompt.
- [ ] Test command resolved.
- [ ] Tests pass on HEAD (baseline = green). If red, STOP.

## Phase 2 — read

- [ ] Target read end-to-end.
- [ ] Existing tests for the target read.
- [ ] AGENTS.md / CLAUDE.md / CONTRIBUTING.md read for testing rules.
- [ ] Mock policy + assertion style + naming conventions identified.

## Phase 3 — enumerate behaviors

- [ ] `behaviors.md` exists with: Target, Test type, Behaviors (numbered), Behaviors NOT covered.
- [ ] Per behavior: happy / boundary / error trio listed.
- [ ] Each test case in the trio is described in one sentence (input/state → expected output/effect).
- [ ] Behaviors NOT covered have a documented reason.
- [ ] Approval gate fired (unless `--auto`).

## Phase 4 — author tests

For each new test:

- [ ] Test name describes BEHAVIOR, not function.
- [ ] Test asserts on observable behavior (return value, status, side effect, log) — not internal state.
- [ ] Test does not mock the SUT itself (mocks at IO boundary only).
- [ ] **Fail-first transition observed and documented**:
    - Mutation applied to SUT.
    - Test ran red.
    - Mutation restored.
    - Test ran green.
- [ ] Per-test evidence captured in `validation/per-skill/code-test.md` (or grouped per behavior when mutation pattern is identical across the trio).
- [ ] Test assertion is non-vacuous (would fail on a wrong implementation).

## Phase 5 — validate

- [ ] New tests run individually: green.
- [ ] Full affected-package suite: green. Test count = baseline + new tests (+/- bookkeeping).
- [ ] Typecheck on the test files: green.
- [ ] Lint on the test files: green.
- [ ] (If `--coverage`) Coverage ran; before/after captured for the target file.

## Phase 6 — pre-handoff

- [ ] `report.md` covers: Result, Tests added, Behaviors covered, Behaviors NOT covered, (optional) Coverage delta, Validation evidence, Decisions, Residual risk, NOT done, Next steps.
- [ ] Every artifact referenced in `report.md` exists.
- [ ] Decisions table includes every auto-pick.
- [ ] No remote write.
- [ ] Final status banner printed.
- [ ] Offer-depth question asked.

## Hard checks

1. `behaviors.md` exists with at least 1 behavior listed.
2. Per new test, fail-first evidence is recorded in `validation/per-skill/code-test.md`.
3. Test names use behavior-named pattern (auditor: spot-check a few; should NOT contain `()` or be just function names).
4. No SUT-mocking detected (auditor: spot-check the new test files for `vi.mock(target-module)` / `jest.mock(target-module)` patterns).
5. Full affected-package suite is green.
6. No existing test was disabled / skipped without a documented reason.

If any hard check fails:

- The skill is BLOCKED.
- The status banner shows `validation=red` and the report is not generated.

## On any check failure

1. Log the failure under `## Validator failures`.
2. Block the next phase.
3. After 3 attempts to make a test green, STOP — re-read the target; the assertion may be wrong.
4. After 2 attempts where fail-first didn't show red, STOP — the mutation may not exercise the test path.
5. Disabled-existing-test detected → STOP, surface; require operator approval to proceed.
