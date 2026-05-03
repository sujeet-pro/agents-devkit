# `investigate-rca` — RCA template

The canonical structure for `.temp/task-<slug>/investigation/rca.md`. All eight sections are mandatory; sections 4 and 5 (Detection, Mitigation) are MUST INCLUDE "what worked" bullets even when most of the RCA is critical.

## Section 1 — Summary

One paragraph for an exec audience. Answer:

- **What** happened (in user-facing terms).
- **When** (start, mitigation, fully resolved).
- **Who** was affected (number of users, services, regions).
- **What we did** (mitigation summary).
- **Current state** (resolved / monitoring / partial).

Example:

> "On 2026-05-02 at 13:02 UTC, the `checkout-api` service began returning 500s at 4.1% error rate (10x baseline). The cause was deploy `a3f9c2e` at 12:58 UTC, which referenced a column renamed last week. The on-call paged at 13:03 (1 min after symptom) and applied a rollback at 13:11 (8 min total to mitigate). 1,847 users were unable to complete checkout during the 9-minute window. No data loss; service fully recovered post-rollback."

## Section 2 — Timeline

Chronological table. Each row has:
- Time (UTC, ISO).
- Event (one sentence).
- Source (clickable link — DD UI, Slack thread, PR, etc.).

The first row may pre-date the symptom by hours / days if it's part of the causal chain (e.g. the migration that set up the bug).

## Section 3 — Detection

- **Time to alert:** symptom_time → first page.
- **Time to acknowledge:** first page → on-call ack.
- "What worked" bullets: alerts that fired correctly, monitors with no false-positive history, etc.
- "What didn't work" bullets: alert that fired late, page that went to wrong person, etc.

## Section 4 — Mitigation

- **Time to mitigate:** acknowledge → metrics back to baseline.
- **Action taken:** rollback / flag-off / restart / escalate.
- "What worked" bullets: rollback workflow that worked first try, runbook that was current, etc.
- "What didn't work" bullets: time wasted on wrong hypothesis, communication delays, etc.

## Section 5 — Root cause

One paragraph, system-shaped. Anchored to ≥2 corroborating sources cited in the timeline.

The paragraph ends with a sentence: **"The system gap: <one sentence naming the structural issue>."**

NEVER name an individual. Author + reviewer of implicated PRs are in the timeline as metadata, NOT in this paragraph.

Example:

> "The new query path in `OrderService.computePrice` referenced the column `is_active`, which was renamed to `active_at` in DB migration `0421` on 2026-04-25. The query failed with a NullPointerException because the column no longer existed under that name. **The system gap: there was no integration test that asserted query column references resolve against the current schema for the new query path.**"

## Section 6 — Contributing factors

Numbered list. Each factor is another system gap (or a process gap). Examples:

1. No integration test for renamed-column scenarios.
2. Migration ledger not surfaced during code review.
3. Statsig audit log not pulled during initial triage (4 min lost).
4. No deploy soak time between merge and prod promotion.

If there are no contributing factors beyond the root cause, write "No contributing factors beyond the root cause."

## Section 7 — Action items (5W frame)

Numbered list. Each action item:

```
N. **<short title>** [WHO: <owner>] [WHAT: <concrete deliverable>] [WHEN: <date>] [WHERE: <path or system>] [WHY: <one sentence>]
```

### 5W rules

- **WHO** is a team or named owner. Not "the team" without specifying which.
- **WHAT** is a concrete deliverable that you can write a test for. NOT "be more careful".
- **WHEN** is a specific date (typically within 30 days; longer requires justification).
- **WHERE** is a file path / system / runbook location. Not "in the codebase".
- **WHY** ties back to the root cause / contributing factor.

### Testability examples

| WHAT (BAD) | WHAT (GOOD) |
| --- | --- |
| Be more careful in code review | Add a CI check that comments on PRs whose queries reference recently-renamed columns |
| Improve our incident response | Reduce on-call alert fan-out from 4 monitors to 1 grouped monitor (configured in `monitors/checkout-api.tf`) |
| Document the rollback better | Document the rollback runbook at `docs/runbooks/checkout-api-rollback.md`; new on-call engineer can rollback in <5 min using only the runbook |
| Watch for column renames more carefully | Add integration test in `checkout-api/src/test/integration/QueryColumnReferenceIntegrationTest.kt` that scans every query against the migration ledger |

## Section 8 — References

Bulleted list. Every artifact cited in the body has a link. Examples:

- Incident.md path
- Statsig audit path
- Git blame path
- Mixpanel impact path (if applicable)
- PR / commit URLs
- Migration history URLs (if applicable)
- Slack thread permalinks
- Datadog dashboard at incident time (with anchored time range)
- Statsig audit entry URLs
- Vendor status pages (if applicable)
- Existing runbook URLs
- Related prior RCAs (if applicable)

## Tone rules

- Past tense throughout.
- Specific timestamps over relative ("at 13:02 UTC", not "at the time").
- Specific numbers over qualifiers ("4.1% error rate, 10x baseline", not "very high error rate").
- Calm. The RCA is a learning artifact; urgency belongs in the live incident, not in the post-mortem.

## What NOT to include

- Speculation. Every claim is sourced.
- Blame. The author + reviewer of an implicated PR appear in the timeline as metadata; they NEVER appear in the root cause sentence.
- Vague action items.
- Indirect language about who did what wrong. Plain language: "the implementation referenced a renamed column" (system-shaped) is fine; "Alice referenced a renamed column" (person-shaped) is not.
