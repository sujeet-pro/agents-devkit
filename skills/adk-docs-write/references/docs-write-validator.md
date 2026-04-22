# docs-write Validator

The validator gate `adk-docs-write` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/docs-write-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Doc type chosen | README / runbook / API ref / ADR / onboarding / migration / radar — picked deliberately | BLOCKER if unclear |
| Source-of-truth identified | The code / config the doc describes is named (file paths or repo URLs) | BLOCKER without |
| Audience named | The reader of this doc is named (new joiner / on-call / external dev) | BLOCKER without — drives tone and depth |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-handoff validation (doc readiness)

Run after the doc is drafted; verify every command, schema, and link in it actually works against the live source.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Every command works | Every shell / CLI command in the doc runs and produces the documented output | Per-command run-result |
| Every schema / env-var matches code | Field names + types + env-var names verified against the source | Per-schema cross-check |
| Every link resolves | Internal links resolve; external links return 200; anchors exist on target page | Link-check report |
| Examples are runnable | Code examples copy-paste run cleanly | Per-example run-result |
| Sections per doc-type present | Doc-type's expected sections all present (Quick Start in README, rollback in runbook, etc.) | Section presence map |
| Stale claims caught | "As of X" claims still true; version-specific instructions still apply | Per-claim freshness check |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Doc written to its destination | Doc file lands at the requested path (or `.temp/drafts/` if no destination) | File path |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/docs-write-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/docs-write-<slug>.md
```
