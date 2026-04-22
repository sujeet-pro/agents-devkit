# build-migrate Validator

The validator gate `adk-build-migrate` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/build-migrate-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Migration target valid | `<from>` and `<to>` versions exist; official migration guide located | BLOCKER if no upstream guide for breaking changes |
| Breaking-change inventory captured | Every breaking change documented with usage count from the actual repo | BLOCKER — generic guidance not enough |
| Rollback strategy | Per-group rollback path documented (revert commit, version pin) | BLOCKER — never start without a rollback |
| Baseline tests green | Pre-migration test suite is green; this is the parity baseline | Suite output (commit SHA + result) |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-merge validation (per migration group)

Run after each migration group + a final pass after all groups; verify behavior parity and no compatibility shims left.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Group migrated cleanly | All call sites in the group updated to the new API | Per-group diff + grep for old-API usages (should be empty in group scope) |
| Compatibility shims removed at the end | After the LAST group: zero `// TODO: remove after migration` markers; shims gone | Grep for shim markers |
| Behavior parity | Test suite still green after each group + after the final group | Per-group + final suite output |
| Build + typecheck pass on the full repo | Not just the changed files | Build + typecheck output |
| Performance not regressed (where measurable) | If the change has a measurable perf surface: smoke benchmark before/after | Benchmark numbers (or N/A with reason) |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Per-group commits | One commit per group, descriptively named | git log of the migration branch |
| Migration report written | `.temp/reports/<task>-<slug>.md` documents what changed, why, what could not be migrated | Report path |
| Rollback steps tested or documented | Rollback path actually exercised once OR documented step-by-step in the report | Report section |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/build-migrate-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/build-migrate-<slug>.md
```
