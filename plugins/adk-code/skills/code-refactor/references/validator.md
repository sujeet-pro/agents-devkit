# `code-refactor` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/code-refactor.md` under a `## Validator` heading.

## Phase 0 — pre-execution

- [ ] `.temp/task-<slug>/` exists; `.temp/` is gitignored.
- [ ] User's prompt captured in `prompt.txt`.
- [ ] Repo resolved.
- [ ] The move named in one sentence (extract / rename / dedupe / split / inline / move).
- [ ] Slug derived from move + area.

## Phase 1 — preflight

- [ ] `git status` clean.
- [ ] Branch captured. If protected, branch-creation prompt fired.
- [ ] Validation commands resolved.
- [ ] **Baseline = green**: typecheck + lint + tests on HEAD all green. A refactor on red baseline is BLOCKED.
- [ ] Test count recorded (used to verify "no test count change" at end).

## Phase 2 — read first

- [ ] Target code read end-to-end.
- [ ] Grep for symbols-about-to-move ran; call-site count + file list captured.
- [ ] Existing tests for the area read.
- [ ] AGENTS.md / CLAUDE.md read (no "don't refactor X" rules being violated).
- [ ] Recent commits checked for high-churn flag.

## Phase 3 — plan

- [ ] `plan.md` exists with: Move (one sentence), Scope, Existing test coverage, Micro-steps (numbered), Validation plan, Out of scope.
- [ ] Each micro-step is small enough that the suite stays green after it (verifiable by reading the step description; if a step says "edit 14 files at once", reconsider).
- [ ] If existing test coverage is thin, the recommendation to do `code-test` first is surfaced.
- [ ] No micro-step changes public API surface.
- [ ] Approval gate fired (unless `--auto`).

## Phase 4 — execute the micro-steps

For each step:

- [ ] Step applied.
- [ ] Affected-package tests ran.
- [ ] Suite green AFTER the step (the green-between-steps invariant).
- [ ] Test count matches the baseline (or differs only in expected ways, e.g. "moved 4 tests to a new file" — count is the same overall).
- [ ] Output captured to `validation/per-skill/code-refactor.md` under that step's section.

If RED:

- [ ] Cause identified.
- [ ] Smallest possible micro-step-fix applied (or REVERT).
- [ ] Re-run; green.
- [ ] If 2 failed-and-reverted attempts on the same step → STOP and surface.

## Phase 5 — validate (final)

- [ ] **Full affected-package suite**: green. Test count matches baseline.
- [ ] **Typecheck**: green.
- [ ] **Lint**: green.
- [ ] **No snapshot test required `--update`**. If any did, STOP — re-categorize the change.
- [ ] All step outputs captured in `validation/per-skill/code-refactor.md`.

## Phase 6 — pre-handoff

- [ ] `report.md` covers: Move, Files changed, Micro-steps (with post-step suite size per step), Validation evidence, Decisions, Residual risk, NOT done, Next steps.
- [ ] Every step in `report.md` has a recorded suite-size after.
- [ ] Decisions table includes every auto-pick.
- [ ] No remote write.
- [ ] Final status banner printed.
- [ ] Offer-depth question asked.

## Hard checks (the skill cannot pass without these)

1. Baseline was green BEFORE editing.
2. Suite was green AFTER every micro-step (recorded in the validation log).
3. Test count is unchanged (or changes are documented and consistent with the move — e.g. moving tests between files).
4. No snapshot tests required `--update`.
5. No public API surface symbol was renamed / changed.

If any hard check fails:

- The skill is BLOCKED.
- The status banner shows `validation=red` and the report is not generated.
- Surface to the operator with the specific check that failed and the suggested next action.

## On any check failure

1. Log the failure under `## Validator failures`.
2. Block the next phase.
3. Two failed-and-reverted micro-step attempts → STOP, surface.
4. Snapshot-test-changed → STOP immediately; this signals behavior change.
5. Test count changes unexpectedly → STOP, investigate.
