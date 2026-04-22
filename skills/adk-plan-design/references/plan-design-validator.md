# plan-design Validator

The validator gate `adk-plan-design` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/plan-design-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Design level chosen | HLD / LLD / ADR / TDD — picked deliberately for the audience | BLOCKER if unclear |
| Source-of-truth read | Existing code / ADRs / sibling designs read first | BLOCKER if skipped |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-handoff validation (design completeness)

Run after the architecture write-up is drafted; verify it covers components, interfaces, data flow, failure modes, and trade-offs.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Components + interfaces named | Each component named; each public interface signed | Per-component spec |
| Data flow traced | Request / event / batch flow drawn end-to-end | Flow diagram (mermaid / drawio / inline) |
| Sequencing covered | Order of operations for non-trivial flows; concurrency model explicit | Sequence section |
| Failure modes enumerated | What can fail at each step; how the system degrades | Failure-mode table |
| Trade-offs explicit | Why this design vs the alternatives that were considered | Trade-off matrix |
| Migration path (when replacing) | If superseding existing design: how the cutover happens | Migration section |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Design artifact written | `.temp/drafts/design-<slug>.md` (or ADR file) in the documented shape | File path + size |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/plan-design-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/plan-design-<slug>.md
```
