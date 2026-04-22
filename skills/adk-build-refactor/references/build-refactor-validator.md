# build-refactor Validator

The validator gate `adk-build-refactor` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/build-refactor-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Behavior baseline captured | Tests pass on the pre-refactor commit; behavior boundaries documented | BLOCKER — without baseline, equivalence cannot be checked |
| Refactor scope bounded | User-stated scope is a single refactor pattern (rename / extract / inline / dedupe / shape); not multiple at once | BLOCKER if mixed; ask the user to split |
| Repo conventions read | Style / naming / module-boundary rules from `AGENTS.md` / config | WARN if missing |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-commit validation (behavior preservation)

Run after the restructure is complete; verify NOTHING observable changed.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Same behavior | Every test that passed pre-refactor still passes post-refactor (no test added or modified to compensate) | Test diff comparison |
| No public API changes | Exported types / functions / props unchanged (or change is documented in scope) | Public-API diff (should be empty) |
| Lint + typecheck still pass on full module(s) touched | Full-module lint / typecheck (not just changed lines) | Command output |
| Smaller / clearer code | Diff actually reduces complexity (lines, cognitive load, cyclomatic) — not just churn | Before/after metric snapshot |
| No new abstractions added | No new layer / dependency / config introduced (or it's the explicit goal of the refactor) | Abstraction diff |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Diff committed atomically | One commit per refactor pattern; commit message says "refactor: ..." | git log entry |
| Validator log written | `.temp/notes/<task>-<slug>-validator.md` exists | File path + size |
| Test suite green on result | Full suite (or smallest provably-relevant subset) green | Suite output |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/build-refactor-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/build-refactor-<slug>.md
```
