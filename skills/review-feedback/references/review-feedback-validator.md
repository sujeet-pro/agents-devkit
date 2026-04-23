# review-feedback Validator

The validator gate `adk-review-feedback` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/review-feedback-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| PR + comments fetched | PR diff + every existing comment / reply / task pulled | BLOCKER if MCP / CLI fails |
| Comment classification | Each comment classified per the reconciliation rules (apply / pushback / accept-and-defer / clarify) | Per-comment classification map |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-reply validation

Run after each comment is addressed; verify the code change actually addresses the concern OR the reply is a justified pushback.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Code changes match concerns | For each `apply`: the diff actually addresses the concern (re-read both) | Per-comment evidence: file:line + diff hunk |
| Pushbacks have evidence | For each `pushback`: cites the source-of-truth file:line that justifies the position | Per-pushback citation |
| Local validation passes | Lint / typecheck / smallest-relevant test green after the changes | Command output |
| No silent skips | Every existing comment has a planned outcome (no comment left without a reply) | Coverage map |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Replies posted to remote | Every reply landed; comment IDs returned | Provider-returned reply IDs |
| Tasks reconciled (Bitbucket) | Tasks resolved / reopened / created per plan | Task action log |
| Post-confirmation pass | After waiting 5s, every reply / summary receipt ID re-appears in a fresh fetch of the PR's comment + reply graph. On miss, retry at 10s and 20s (3 attempts total, 35s budget). All confirmed → OK. Any unconfirmed after the budget → WARN with the ID + html_url surfaced in the report. NEVER re-post a missing reply automatically — the API said 2xx; a re-post would create a real duplicate if the comment is just propagation-lagged. The user can re-run this skill (which will re-classify and detect the duplicate) if they want to retry. | Per-receipt match map (`confirmed` / `missing`), wall-clock spent, retry count |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/review-feedback-<slug>-validator.md` for audit. Format:

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
- Replies posted: 5 (IDs: ...)
- Post-confirmation: OK after 1 retry (5s), 5/5 receipts re-appeared
   | WARN: 1 unconfirmed after 35s — id=12345 kind=reply url=https://github.com/...#discussion_r12345
- ...

Final report: .temp/reports/review-feedback-<slug>.md
```
