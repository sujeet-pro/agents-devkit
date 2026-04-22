# build-test Validator

The validator gate `adk-build-test` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/build-test-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Test target identified | Behavior under test is named; not "add tests" without a target | BLOCKER — vague tests are anti-pattern |
| Test framework + location detected | Repo's test framework (vitest/jest/pytest/go test) and test directory convention identified | BLOCKER if no framework — propose adding one or stop |
| Existing coverage read | Prior tests for the area inspected (do not re-test what is already covered) | Coverage map snapshot |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-commit validation (test quality)

Run after the new tests are written; verify they fail when they should and pass when they should.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Tests fail before fix (when locking in a bug fix) | If the test is for a bug fix: revert the fix; tests fail; re-apply the fix; tests pass | Pre-fix run output + post-fix run output |
| Tests pass on green path | Every new test passes on the current commit | Test runner output per case |
| No flakes | Run the new tests N times (default 3); all runs identical | N-run stability report |
| Behavior over implementation | Tests assert observable behavior; not internal data shapes / private fields / mock-call counts in isolation | Per-test review (mock-coupling rate) |
| Test names describe behavior | Test names read like sentences ("renders fallback when profile is null"), not ("test1") | Test-name list |
| No `.skip` / `.only` left in | No selective-run helpers committed | Grep result (should be empty) |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Tests committed | New tests in repo; commit message says "test: ..." | git log entry |
| Coverage delta documented (when relevant) | If the team tracks coverage: before/after numbers in the report | Coverage report |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/build-test-<slug>-validator.md` for audit. Format:

```
## Phase 1
- <check>: OK | WARN | BLOCKER (<one-line evidence>)
- ...

## Phase 2
- <gate>: OK (<evidence>)
- ...

## Phase 3
- <check>: OK | WARN | BLOCKER (<one-line evidence>)
- ...

## Phase 4
- <check>: OK | WARN (<evidence>)
- ...

Final report: .temp/reports/build-test-<slug>.md
```
