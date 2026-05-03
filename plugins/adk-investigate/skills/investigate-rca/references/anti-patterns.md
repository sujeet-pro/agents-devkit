# `investigate-rca` — anti-patterns

## Naming an individual as root cause

- "Alice's PR caused the outage." Wrong shape. Alice is one of the people whose work was in the deploy; she's not the root cause. The root cause is the system gap that allowed her PR to ship without catching the bug.
- **Fix:** the root cause sentence is system-shaped: "The new query path had no integration test for column-rename scenarios; the renamed column reference passed code review unnoticed."
- Author + reviewer go in the timeline (they're metadata cited for context), never in the root cause.

## Skipping the timeline

- A root cause without a chronology is just an opinion. The timeline is the foundation: time → event → source link.
- **Fix:** the RCA has a `Timeline` section per `rca-template.md`. Each row has all three fields.

## Treating the latest deploy as the cause

- "Deploy at 12:58 was 4 min before the symptom; cause = deploy." Maybe — but the multi-source protocol from `investigate-incident` is what actually establishes that. The RCA inherits the rule.
- **Fix:** root cause must be supported by ≥2 corroborating sources from `incident.md`. If only 1 source agrees, the root cause is "leading candidate, pending further investigation".

## Action items that aren't testable

- "Be more careful in code review." How do we know we've done it? We can't.
- "Improve our incident response." Same problem.
- **Fix:** every action item is testable. Examples:
  - "Add integration test for column-rename scenarios in `checkout-api/src/test/integration/`. Test fails today; passes once the test is committed."
  - "Reduce on-call alert fan-out from 4 monitors to 1 grouped monitor. Test: trigger a synthetic checkout error; one page, not four."
  - "Document the deploy rollback runbook at `docs/runbooks/checkout-api-rollback.md`. Test: a new on-call engineer can rollback in <5 min using only the runbook."

## Pasting raw timelines without evidence links

- "13:02: error rate spiked." Where's the link to the DD graph?
- **Fix:** every timeline entry has a source link (DD UI, Slack permalink, GH PR URL).

## Skipping "what worked"

- The RCA only talks about what failed. The team learns half the lesson.
- **Fix:** the RCA's `Detection` and `Mitigation` sections include positive notes ("paged in 4 minutes" / "rollback applied in 7 minutes"). The team learns what to keep.

## Auto-publishing

- The RCA needs human review before it goes to Confluence — politics, accuracy, narrative all matter.
- **Fix:** this skill stops at `.temp/task-<slug>/investigation/rca.md`. The operator runs `/adk-docs:docs-publish-confluence` (or similar) after review.

## Inflating confidence

- "Root cause: the deploy. Confidence: high." But only logs and the deploy timeline correlated; PR diff wasn't inspected; no Slack pre-knowledge.
- **Fix:** the RCA inherits the confidence anchoring from `investigate-incident`'s `confidence-language.md`. High confidence requires ≥3 corroborating sources.

## Naming the action item too narrowly

- "Fix the NullPointerException in OrderService.line47." That's the symptom; the action item should address the system gap.
- **Fix:** "Add integration test that fails when ANY query references a renamed column. Apply to all repos; track in `.github/CODEOWNERS` for the migration ledger." This addresses the class of problem, not just the instance.

## Forgetting to cite the contributing factors

- "Root cause: missing integration test. Action: add the test." But the alert system also fired 4 redundant pages, the runbook was outdated, and the team's on-call rotation had a gap.
- **Fix:** `Contributing factors` section is mandatory. List every system gap that made the impact larger / longer, even if not the primary cause. Each gets its own action item.

## Quoting Slack chatter at length

- 30 messages of "anyone seeing 500s?" pasted verbatim is noise.
- **Fix:** ≤15 words per message; preserve thread permalinks. The RCA summarizes; the operator clicks through for detail.
