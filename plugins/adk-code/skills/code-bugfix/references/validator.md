# `code-bugfix` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/code-bugfix.md` under a `## Validator` heading.

## Phase 0 — pre-execution

- [ ] `.temp/task-<slug>/` exists; parent `.temp/` is gitignored.
- [ ] User's prompt + any pasted stack trace captured verbatim in `prompt.txt`.
- [ ] Repo resolved to a single entry in `repos.md`.
- [ ] System under suspicion identified (file or module name).
- [ ] Slug derived from prompt.

## Phase 1 — preflight

- [ ] `git status` captured. State: `clean | dirty`.
- [ ] Branch captured. If protected, branch-creation prompt fired.
- [ ] Validation commands resolved.
- [ ] **Baseline check**: typecheck + lint + tests on HEAD. The baseline must be green except for any user-supplied failing test that captures the bug.
- [ ] If unexpected red (not the bug-related): STOP, do not proceed.

## Phase 2 — REPRODUCE

- [ ] `reproducer.md` exists and contains: Symptom, Pre-conditions, Failing test, Failing output, Notes.
- [ ] The failing test was actually written and lives in the repo's correct test location.
- [ ] The failing test was executed; its FAILING output is captured verbatim in `reproducer.md`.
- [ ] If the test passed unexpectedly: STOP, the reproducer is wrong (or the bug is gone).
- [ ] Test name describes BEHAVIOR, not function (`it("returns 400 on empty cart")`, not `it("checkout()")`).

## Phase 3 — DIAGNOSE

- [ ] `plan.md` exists with `## Root cause` heading containing ONE sentence.
- [ ] The root cause is falsifiable — names a specific line / commit / mechanism, not "we should be more defensive".
- [ ] `## Patch` lists files + lines + WHY.
- [ ] `## Regression test` references the file::name from `reproducer.md`.
- [ ] `## Validation plan` lists exact commands + expected exit codes.
- [ ] If the cause is upstream / out-of-repo, the workaround is documented and a follow-up is listed.
- [ ] Approval gate fired (unless `--auto`).

## Phase 4 — PATCH

- [ ] Implementer subagent ran with `plan.md` + `reproducer.md`.
- [ ] Each edited file was re-read after the agent claimed done.
- [ ] No file outside the planned set was touched (or scope-creep was re-confirmed).
- [ ] **Reproducer test re-run** post-patch: now PASSES. Output captured.
- [ ] If still failing: STOP — diagnosis is wrong; loop back to Phase 3 (don't keep patching).
- [ ] No drive-by refactors / renames in the patch (auditor: visually scan the diff).

## Phase 5 — VALIDATE

- [ ] **Reproducer test** runs alone: green. Captured.
- [ ] **Full affected-package suite** runs: green. Test count + scope captured.
- [ ] **Typecheck** runs: green.
- [ ] **Lint** runs (with the repo's `--max-warnings` policy): green.
- [ ] If any test that was green before is now red → STOP. That's a regression. Don't ship.
- [ ] If the same kind of failure is seen 3 times consecutively → STOP, surface to the user.

## Phase 6 — pre-handoff

- [ ] `report.md` covers: Symptom, Root cause, Patch, Regression test red→green, Validation evidence, Decisions, Residual risk, NOT done, Next steps.
- [ ] Every artifact referenced in `report.md` actually exists at the cited path.
- [ ] Decisions table includes every auto-pick (under `--auto`).
- [ ] No remote write happened.
- [ ] Final status banner printed: `reproducer=green patch=applied regression=green`.
- [ ] Offer-depth question asked.

## Hard checks (the skill cannot pass without these)

1. `reproducer.md` exists and shows red output captured verbatim.
2. `plan.md` has `## Root cause` with one sentence (length 1-300 chars; longer = restate).
3. The regression test exists in the repo's test tree.
4. The regression test was observed RED before the patch.
5. The regression test was observed GREEN after the patch.
6. The full affected-package suite is green.

If any of these fail, the skill is BLOCKED. The status banner shows `regression=red` or `patch=pending` and the report is not generated.

## On any check failure

1. Log the failure to `validation/per-skill/code-bugfix.md`.
2. Block the next phase.
3. If the same check fails 3 times in this session, surface to the user.
4. If the failure is structural (e.g. the reproducer test passes unexpectedly), STOP immediately — do not continue diagnosing on a flawed base.
