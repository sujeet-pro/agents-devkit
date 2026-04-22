# frontend-design Validator

The validator gate `adk-frontend-design` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/frontend-design-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work.

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Inputs resolved | Every required input from `SKILL.md` "Inputs" table is present and well-formed | BLOCKER — ask the user (default-ask) or stop with a clear message (under `--auto`) |
| Permissions / dependencies | Tools, MCP servers, or auth required to do the work are reachable | BLOCKER — point at the install pointer in this skill's mcp-fallback (if present) or ask the user |
| Working tree state | Acceptable for the operation (no in-progress merge if a write is planned, etc.) | BLOCKER — surface the conflict |
| Approval gate (default-ask) | If the operation is non-trivial: user has approved the plan | BLOCKER — wait for approval |
| Scope sanity | The work is bounded; if user-input scope is huge, propose batching | WARN — surface and proceed (or block under explicit user direction) |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-handoff validation

Run after the main work completes but before declaring success.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Output shape compliance | The deliverable matches the shape from this skill's `*-output-format.md` and `*-artifact-format.md` | Per-section presence map |
| Repo-native validation runs | Lint / typecheck / test (or this skill's analogues) executed; output captured | Command output (stored in validator log) |
| No silent skips | Every input and every advertised step has an outcome (done / skipped-with-reason / blocked) | Outcome table |
| Verdict / status honest | The status banner matches the actual state of the work | Verdict justification |
| Side-effecting actions gated | Any push / publish / posting requires explicit approval (or `--auto`) AND has been logged | Approval log |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Final artifact present | The deliverable from `*-artifact-format.md` is at the documented path (or remote location) | Artifact path / remote ID |
| Report written | `.temp/reports/frontend-design-<slug>.md` (or this skill's analogue) exists with full content | File path + size |
| Validator log written | `.temp/notes/frontend-design-<slug>-validator.md` exists with all four phases' outcomes | File path + size |
| Manual follow-up captured | Every WARN from Phases 1-3 is in the manual follow-up list | Follow-up list |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Common shapes:

- `<TASK>-DRAFT` — Phases 1-2 passed; mid-flow / report-only.
- `<TASK>-DONE` — Phases 1-4 passed; deliverable shipped.
- `AWAITING-APPROVAL` — Phase 2 `plan-approved` is pending user input.

(Use the actual status labels from this skill's persona; the four-phase contract is the same.)

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/frontend-design-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/frontend-design-<slug>.md
```
