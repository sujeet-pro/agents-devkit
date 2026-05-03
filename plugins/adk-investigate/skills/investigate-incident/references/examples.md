# `investigate-incident` — worked examples

## Example 1 — checkout 500s, deploy is the leading candidate

**Prompt:** `/adk-investigate:investigate-incident "checkout 500s since 13:00" --service checkout`

**Phase 0:**
- Service: `checkout` → `checkout-api` (resolved from `datadog.md.service_aliases`).
- Repos: `acme/checkout-api`, `acme/order-service` (both map to `checkout` in `repos.md`).
- Window: `[2026-05-03T12:30Z, 2026-05-03T14:30Z]` (since-13:00 + 30min buffer).
- Slack channel: `#incidents` (default).

**Phase 1:** preflight green; DD MCP, Slack workspace MCP, `gh` all reachable.

**Phase 3 — DD passes (parallel):**
- Logs: `PaymentTimeout` jumped from 38/hr baseline to 412/hr at 13:02. New error class `NullPointerException at OrderService.line47` first seen at 13:02.
- Metrics: error rate 0.4% → 4.1% at 13:02 (10x). p99 220ms → 880ms.
- Traces: top errored span = `OrderService.computePrice`; first occurrence at 13:02.
- Monitors: 4 firing, all triggered 13:02 ± 1min: error-rate, p99, success-rate, webhook-delivery.

**Phase 4 — Deploy timeline:**
- `acme/checkout-api`: 4 deploys in window. **Near-symptom: `a3f9c2e` at 12:58 (-4 min) by Alice — "deploy v3 checkout funnel"**.
- `acme/order-service`: 0 deploys in window.

**Phase 5 — Slack scrape:**
- 12 messages in `#incidents` since 13:02. Thread by Carol: "checkout broken" → 4 replies; "looks like the v3 deploy" by Bob.
- Team's leading hypothesis: deploy `a3f9c2e`.

**Phase 6 — Correlate:**
- Signal 1: deploy at 12:58 (4 min before symptom).
- Signal 2: new error class `NullPointerException at OrderService.line47` first seen 13:02.
- Signal 3: PR diff (one-line `gh pr view 2841`): touches `OrderService.computePrice` to use a renamed column.
- Signal 4: Slack pre-knowledge from Bob agrees.
- 4 independent signals → high confidence.

**Phase 7 — Hypothesis:**

```markdown
**Hypothesis:** Deploy `a3f9c2e` (PR #2841 by Alice, "deploy v3 checkout funnel") introduced a NullPointerException at OrderService.line47 by referencing a column renamed last week (`is_active` → `active_at`). Symptom: 412/hr PaymentTimeout + 88/hr NPE; p99 880ms vs 220ms baseline.

**Evidence:**
- Datadog logs: 412 PaymentTimeout (vs 38 baseline) + 88 NPE first seen at 13:02 [DD link]
- Datadog metrics: error rate 0.4% → 4.1%; p99 220ms → 880ms at 13:02 [DD link]
- Deploy timeline: a3f9c2e at 12:58 UTC by Alice [PR #2841]
- PR diff (gh pr view 2841): touches OrderService.computePrice; references `is_active` column
- Slack: Bob in #incidents thread named the same deploy [Slack link]

**Confidence:** high — 4 independent signals agree (logs + metrics + diff overlap + Slack pre-knowledge).
```

**Phase 8 — Next actions (prioritized):**

```markdown
## Next actions
1. **Rollback `a3f9c2e`** (lowest blast radius; reversible in <5 min)
   Command: `gh workflow run rollback.yml -f sha=<previous-sha> --repo acme/checkout-api`
   Cost: ~5 min. Reversible.
2. **If rollback unavailable:** restart `checkout-api` pods using the prior image tag.
3. **After rollback confirms diagnosis:** queue `/adk-code:code-bugfix "OrderService.line47 references renamed column is_active; expected active_at" --repo acme/checkout-api`.
```

**Phase 9 — Output:** `.temp/task-checkout-500s-since-13/investigation/incident.md`.

---

## Example 2 — no leading hypothesis (third-party outage suspected)

**Prompt:** `/adk-investigate:investigate-incident "users see slow checkout" --service checkout`

**Phase 3 — DD:** error rate normal, but p99 spiked to 1.5s at 13:00. Logs show no new error classes; just "downstream timeout".

**Phase 4 — Deploys:** 0 deploys in window for any checkout-related repo.

**Phase 5 — Slack:** team confused; no leading hypothesis from team.

**Phase 6 — Correlate:** only one signal (latency). No deploy correlation. No Slack pre-knowledge.

**Phase 7:**

```markdown
**Hypothesis:** No leading hypothesis. p99 latency spiked to 1.5s at 13:00 with no correlated deploy, log error class, or Slack pre-knowledge. The "downstream timeout" log line suggests an upstream / third-party dependency.

**Evidence:**
- Datadog metrics: p99 1.5s vs 220ms baseline at 13:00 [DD link]
- Datadog logs: no new error class; "downstream timeout" prevalent [DD link]
- Deploy timeline: 0 deploys in window across [acme/checkout-api, acme/order-service] [report]
- Slack: no team-named cause; multiple "anyone else seeing this?" threads [Slack link]

**Confidence:** low (for any code-cause) — only one signal correlates; no second source agrees.
```

**Phase 8:**

```markdown
## Next actions
1. **Check upstream dependency status pages.** The "downstream timeout" log suggests a 3rd-party outage. Check:
   - Stripe status (https://status.stripe.com)
   - The internal payment-gateway dashboard
2. **Datadog event stream for non-deploy events** in window — `gh` covers deploys; the DD event stream covers infra events (Kafka rebalances, scheduled jobs).
3. **Escalate to the on-call channel** if the upstream outage isn't visible — the symptom is real (latency 7x baseline) but the cause is opaque.
```

---

## Example 3 — Statsig gate flip is the cause (RCA scenario)

**Prompt:** `/adk-investigate:investigate-incident "checkout error spike at 13:01"`

**Phase 3 — DD:** error rate jumped 13:01.

**Phase 4 — Deploys:** 0 deploys in window. **No** correlation here.

**Phase 5 — Slack:** team aware; one thread mentions "did anyone change the gate?".

**Phase 6 — Correlate:** with no deploy correlation but a Slack hint, this skill suggests pulling the Statsig audit log.

```markdown
## Notes
- No near-symptom deploys.
- Slack chatter mentions "gate change". Recommend:
  - `/adk-investigate:investigate-statsig "what changed in last 60m?" --use audit-log`

This skill cannot itself name a Statsig flip as cause without the audit log. Surface the suggestion; if the operator runs the follow-up and finds a gate flip at 13:01, treat that as the second signal and re-run this skill with the new evidence.
```

**Phase 7:**

```markdown
**Hypothesis:** Possible Statsig gate flip near symptom; audit log not yet pulled (this skill doesn't pull Statsig by default — see `investigate-rca` for the composite that does).

**Confidence:** low — single signal (DD error spike); needs Statsig audit log corroboration.
```

**Phase 8:**

```markdown
## Next actions
1. **Pull Statsig audit log:** `/adk-investigate:investigate-statsig "what changed in last 60m?" --use audit-log`. If a gate flip at 13:01 ± 5min is found, that's the second signal.
2. If Statsig audit shows a flip: **flag-off** is the lowest blast radius (one toggle in the Statsig console, reversible).
3. For a full RCA composite that runs DD + deploys + Statsig audit + git blame in one shot: `/adk-investigate:investigate-rca "checkout error spike at 13:01"`.
```
