# build-deps Validator

The validator gate `adk-build-deps` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/build-deps-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Action scoped | Inventory / upgrade / dedupe / audit / remove — one action at a time | BLOCKER if mixing actions |
| Lockfile present | Repo has a lockfile and it parses | BLOCKER otherwise — without lockfile, hygiene is not meaningful |
| Risk classification | Each proposed change classified: patch / minor / major / removal; risk per change | Per-change risk table |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-commit validation (dependency hygiene)

Run after the dep change is applied; verify the lockfile is clean and the install is reproducible.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Lockfile updated cleanly | Lockfile reflects the change; no spurious churn | Lockfile diff size |
| Install reproducible from a clean cache | `<package-manager> install --frozen` (or equivalent) succeeds from a clean state | Install command output |
| No security advisories at HIGH or above | `<package-manager> audit` (or equivalent); HIGH+ surfaced as BLOCKER unless explicitly accepted | Audit output |
| Build + test still green | Build + smoke test passes after the change | Build + test output |
| No removed-package call sites left | Grep for any usage of a removed package | Grep result (should be empty) |
| Major bumps reach a safe baseline | Major bumps either land with a migration plan OR are deferred (do NOT silently ship majors) | Per-major decision in the report |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Lockfile + manifest committed together | One commit covering both files; message says "chore(deps): ..." or repo's convention | git log entry |
| Validator log written | All four phases captured | File path + size |
| Manual follow-up captured | Any deferred upgrade or accepted advisory surfaces in the report | Follow-up list |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/build-deps-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/build-deps-<slug>.md
```
