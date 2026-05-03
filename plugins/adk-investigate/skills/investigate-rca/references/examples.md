# `investigate-rca` — worked examples

## Example 1 — Code regression RCA

**Prompt:** `/adk-investigate:investigate-rca "checkout 500s on 2026-05-02" --window 4h --symptom-time 2026-05-02T13:00:00Z`

**Phase 2 — incident triage:** runs `/adk-investigate:investigate-incident`. Result: high-confidence hypothesis "deploy `a3f9c2e` (PR #2841 by Alice) introduced a NullPointerException at OrderService.line47 by referencing a renamed column".

**Phase 3 — Statsig audit (±2h around 13:00):** 1 unrelated config edit at 12:15. Not a contributing factor.

**Phase 4 — Git blame:**
- `git blame -L 40,55 -- checkout-api/src/main/java/com/acme/checkout/OrderService.kt` shows line 47 was last edited in commit `a3f9c2e` (PR #2841 by Alice; reviewed by Bob; merged 12:55).
- `gh pr view 2841` reveals: 4 files changed, 124 additions; description mentions "v3 checkout funnel"; no test file changed.

**Phase 5 — User impact (Mixpanel):**
- `/adk-investigate:investigate-mixpanel "funnel checkout_started → checkout_completed during 12:00-15:00"`.
- 1,847 fewer `checkout_completed` events during the incident window vs prior-week same hours. Recovery clean post-rollback.

**Phase 6 — Aggregate RCA:**

```markdown
# RCA: checkout 500s on 2026-05-02 13:00 UTC

## Summary
On 2026-05-02 at 13:02 UTC, the `checkout-api` service began returning 500s at 4.1% error rate (10x baseline). The cause was deploy `a3f9c2e` at 12:58 UTC, which introduced a NullPointerException via a reference to a column renamed last week (`is_active` → `active_at`). The on-call engineer was paged at 13:03 (1 min after symptom) and applied a rollback at 13:11 (8 min total to mitigate). 1,847 users were unable to complete checkout during the 9-minute incident window. No data loss; service fully recovered post-rollback.

## Timeline
| Time (UTC) | Event | Source |
| --- | --- | --- |
| 2026-04-25 | Column `is_active` renamed to `active_at` in `users` table (DB migration `0421_rename_active`) | [PR #2718] |
| 2026-05-02 11:00 | PR #2841 opened by Alice; 4 files changed; reviewed by Bob | [PR #2841] |
| 2026-05-02 12:55 | PR #2841 merged to main | [PR #2841] |
| 2026-05-02 12:58 | Deploy `a3f9c2e` started (`acme/checkout-api`) | [workflow run] |
| 2026-05-02 13:01 | Deploy completed; new code live | [workflow run] |
| 2026-05-02 13:02 | Error rate jumped 0.4% → 4.1%; first NullPointerException at `OrderService.line47` logged | [DD logs] [DD metrics] |
| 2026-05-02 13:03 | Datadog monitor `Checkout error rate > 1%` paged on-call (P1) | [DD monitor] |
| 2026-05-02 13:04 | On-call (Carol) acknowledged page; opened thread in `#incidents` | [Slack thread] |
| 2026-05-02 13:07 | Bob in `#incidents`: "looks like the v3 deploy" (4 min after symptom) | [Slack thread] |
| 2026-05-02 13:11 | Rollback to `prev-sha` triggered | [workflow run] |
| 2026-05-02 13:14 | Rollback completed; error rate returned to baseline within 2 min | [DD metrics] |

## Detection
- **Time to alert:** 1 min (13:02 → 13:03).
- **Time to acknowledge:** 2 min (13:03 → 13:04).
- The Datadog monitor `Checkout error rate > 1%` triggered as expected. **What worked: the alert was tuned correctly (no false positive in the prior 30 days).**

## Mitigation
- **Time to mitigate:** 8 min from page (13:03 → 13:11).
- Rollback applied to the prior known-good SHA. Recovery clean (2 min for metrics to return to baseline post-rollback).
- **What worked:** the rollback workflow was documented and worked first try. The runbook at `docs/runbooks/checkout-api-rollback.md` was followed.

## Root cause
The new query path in `OrderService.computePrice` (introduced in PR #2841 / commit `a3f9c2e`) referenced the column `is_active`, which was renamed to `active_at` in DB migration `0421_rename_active` on 2026-04-25 (one week before the deploy). The query failed with a NullPointerException because the column no longer existed under that name. **The system gap: there was no integration test that asserted query column references resolve against the current schema for the new query path.** The rename migration shipped first; the dependent code change did not catch the rename because the new code wasn't yet exercised against the new schema.

## Contributing factors
1. **No integration test for renamed-column scenarios.** The CI suite tests business logic but not column-existence at runtime against the migration ledger.
2. **The migration ledger is not surfaced during code review.** Reviewers don't see "this PR's queries reference columns that were renamed in the last 30 days".
3. **Statsig audit log was not pulled during the initial triage**, delaying the team's confirmation that the cause was the deploy and not a config flip. (Slack thread shows 4 min lost on this.)
4. **The deploy ran 3 minutes after merge**, leaving no soak time. (CI was green because the test suite didn't exercise the renamed code path at runtime.)

## Action items (5W frame)
1. **Add integration test for renamed-column scenarios** [WHO: platform team / Carol] [WHAT: a test that scans every query referencing tables in the migration ledger and asserts column resolution at runtime] [WHEN: by 2026-05-15] [WHERE: `checkout-api/src/test/integration/QueryColumnReferenceIntegrationTest.kt`] [WHY: prevent the column-rename class of failure]
2. **Surface migration ledger in code review** [WHO: platform team / Bob] [WHAT: a CI check that comments on PRs whose queries reference recently-renamed columns] [WHEN: by 2026-05-22] [WHERE: GitHub Action in `.github/workflows/migration-check.yml`] [WHY: catch column-rename mismatches at review time]
3. **Add Statsig audit log to the on-call runbook** [WHO: on-call rotation / Carol] [WHAT: the first command in the runbook is `/adk-investigate:investigate-statsig --use audit-log --window last 60m`] [WHEN: by 2026-05-08] [WHERE: `docs/runbooks/checkout-api-on-call.md`] [WHY: rule out config flips before chasing deploys]
4. **Add deploy soak time** [WHO: platform team / Alice] [WHAT: post-merge deploys wait 5 minutes before promotion to prod, allowing CI to run a full integration smoke] [WHEN: by 2026-05-29] [WHERE: `.github/workflows/deploy.yml`] [WHY: catch runtime issues that unit tests miss]

## References
- Incident.md: `.temp/task-checkout-500s-2026-05-02/investigation/incident.md`
- Statsig audit: `.temp/task-checkout-500s-2026-05-02/investigation/statsig.md`
- Git blame: `.temp/task-checkout-500s-2026-05-02/investigation/git-blame.md`
- Mixpanel impact: `.temp/task-checkout-500s-2026-05-02/investigation/mixpanel.md`
- PR #2841: https://github.com/acme/checkout-api/pull/2841
- Migration `0421_rename_active`: https://github.com/acme/checkout-api/pull/2718
- Slack thread: https://acme.slack.com/archives/C123/p1714638240
- Datadog dashboard at incident time: https://app.datadoghq.com/dashboard/abc-123-xyz?from_ts=...&to_ts=...
```

---

## Example 2 — Statsig gate flip RCA (no code regression)

**Prompt:** `/adk-investigate:investigate-rca "search latency spike 2026-05-01 14:30" --window 2h`

**Phase 2:** incident triage finds latency spike but no near-symptom deploy.

**Phase 3 — Statsig audit:** **gate `search_v2` was rolled out 50% → 100% at 14:29 by Dave.** Audit log entry timestamp matches symptom within 1 minute.

**Phase 4 — git blame skipped** (no code regression; the cause is a config flip, not a code change). Note in RCA.

**Phase 5 — Mixpanel impact:** search-funnel conversion dropped from 38% to 31% during the 14:30-15:30 window.

**Phase 6 excerpt:**

```markdown
## Root cause
Statsig gate `search_v2` was rolled out from 50% to 100% at 14:29 UTC by Dave. The v2 search backend has higher p99 latency than v1 (a known performance trade-off documented in the experiment design). At 50% rollout, the average latency was acceptable. At 100%, all users hit the slower backend, pushing p99 from 480ms to 1,200ms. **The system gap: the rollout convention is "50% for 7 days, then 100%"; this rollout went 50% → 100% in one step without the soak period.**

## Contributing factors
1. **Rollout convention not enforced by tooling.** Statsig allows any % step; the team's "50→100 with soak" rule is policy, not policy-enforced.
2. **No latency guardrail on the gate** at the Statsig level. The latency regression was visible in DD but not in the gate's own pulse.
3. **Code deep dive was unnecessary** for this incident — the cause was a config flip, not a code regression. (Phase 4 of the RCA workflow was skipped.)

## Action items
1. **Enforce rollout cadence** [WHO: platform team / Erin] [WHAT: a Statsig pre-commit hook that rejects rollout jumps > 25% without an override flag] [WHEN: by 2026-05-22] [WHERE: Statsig API integration in our control plane] [WHY: prevent step-jumps that skip the soak period]
2. **Add p99_latency guardrail to gate `search_v2`** [WHO: search team / Dave] [WHAT: configure the guardrail in the Statsig console; verdict-eligible-to-flip blocked if guardrail fires] [WHEN: by 2026-05-08] [WHERE: Statsig console] [WHY: catch latency regressions at the gate level, not just at DD]
```

---

## Example 3 — third-party outage RCA

**Prompt:** `/adk-investigate:investigate-rca "checkout intermittent failures 2026-04-29 09:00-10:30" --window 3h`

**Phase 2:** incident triage finds latency + error spike, no near-symptom deploy, no Statsig flip. Hypothesis: external dependency.

**Phase 4 skipped** (no code-cause).

**Phase 5:** Mixpanel impact ~3% checkout drop during window.

**Phase 6 excerpt:**

```markdown
## Root cause
Stripe API experienced intermittent 5xx responses between 09:02 and 10:18 UTC (per status.stripe.com timeline). Our checkout flow's payment-intent creation calls Stripe synchronously and propagates the failure to the user. The system gap: **we have no graceful degradation for transient upstream failures — every 5xx becomes a user-visible error.**

## Contributing factors
1. **No retry-with-exponential-backoff on Stripe calls.** The synchronous call fails fast on the first 5xx.
2. **No circuit breaker.** A 1.3-hour upstream incident propagated 1:1 to user errors.
3. **No graceful degradation messaging.** Users saw a generic 500 page; ideally they'd see "we're experiencing temporary delays — try again in a moment".

## Action items
1. **Add retry-with-backoff to Stripe payment-intent creation** [WHO: platform team / Frank] [WHAT: 3 retries with exponential backoff; max 4-second total wait] [WHEN: by 2026-05-22] [WHERE: `checkout-api/src/main/java/com/acme/checkout/PaymentService.kt`] [WHY: ride out transient upstream blips]
2. **Add circuit breaker for Stripe** [WHO: platform team / Grace] [WHAT: open the breaker after 50% failure rate over 30s; half-open every 10s] [WHEN: by 2026-05-29] [WHERE: same file as above] [WHY: stop hammering Stripe during their outages]
3. **Improve error UX for upstream failures** [WHO: storefront team / Henry] [WHAT: detect the Stripe 5xx error class and render a "temporary delay" message instead of generic 500] [WHEN: by 2026-06-05] [WHERE: `storefront/src/checkout/ErrorBoundary.tsx`] [WHY: better UX during upstream incidents]
```
