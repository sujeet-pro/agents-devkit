# `investigate-experiment` — worked examples

## Example 1 — clear iterate (guardrail veto)

**Prompt:** `/adk-investigate:investigate-experiment "checkout_funnel_v3"`

**Phase 0:**
- Experiment: `checkout_funnel_v3` → id `exp_a3f9...`. Linked repo: `acme/storefront`. Linked service: `storefront-web`.
- Window: `since experiment_start` (9 days).

**Phase 2 — three parallel reads:**
- Statsig: primary `checkout_completed` lift +4.2% (p=0.014, n=18,401 per arm); guardrail `p99_latency_ms` +85ms (p=0.002).
- Mixpanel: project-level `checkout_completed` +3.8% over same 9d window vs prior 9d. Direction agrees.
- DD: `error_rate` +1.1% (p=0.45, within tolerance); `p99_latency_ms` +85ms (p=0.001, REGRESSION).

**Phase 3 — Reconciliation:**

| Metric | Statsig (T vs C) | Mixpanel (project) | DD (service) | Verdict |
| --- | --- | --- | --- | --- |
| primary `checkout_completed` | +4.2% (p=0.014) | +3.8% | n/a | agree |
| guardrail `error_rate` | n/a | n/a | +1.1% (p=0.45) | within tolerance |
| guardrail `p99_latency_ms` | +85ms (p=0.002) | n/a | +85ms (p=0.001) | **REGRESSION (veto)** |

**Phase 4:**

```markdown
## Verdict: iterate

**Reason:** Primary metric `checkout_completed` lifted +4.2% (Statsig p=0.014, Mixpanel project-level +3.8% — direction confirmed). However, p99 latency regressed +85ms (DD p=0.001), which exceeds the guardrail threshold. The latency cost is a user-experience regression that vetoes ship even though conversion improved. Iterate: find a less-expensive implementation of v3 (cache, async, lighter computation) before re-running.

**Confidence:** high
- 3 sources agree on direction of primary metric.
- Sample size satisfies power (n=18,401 per arm > 7,800 target).
- Days-in-experiment 9 ≥ 7.
- Veto unambiguous (DD p99 regression at p<0.01).
```

---

## Example 2 — clear ship

**Prompt:** `/adk-investigate:investigate-experiment "pdp_image_carousel"`

**Phase 2:**
- Statsig: primary `add_to_cart` +6.8% (p=0.008, n=24,103 per arm); guardrails clear.
- Mixpanel: `add_to_cart` +6.5% project-level. Agrees.
- DD: `error_rate` -0.1% (p=0.71, neutral); `p99_latency_ms` +5ms (p=0.32, neutral).

**Phase 3 — Reconciliation:** all three agree. No guardrail miss.

**Phase 4:**

```markdown
## Verdict: ship

**Reason:** Primary metric `add_to_cart` lifted +6.8% (Statsig p=0.008, Mixpanel project-level +6.5%). All DD guardrails clear (`error_rate` -0.1% neutral; `p99_latency_ms` +5ms neutral). Sample size satisfies power (n=24,103 per arm); days-in-experiment 12 ≥ 7. No veto active.

**Confidence:** high
- All 3 sources agree direction + magnitude.
- Power and duration thresholds satisfied.
- Zero guardrail risk.
```

---

## Example 3 — iterate (Mixpanel disagreement)

**Prompt:** `/adk-investigate:investigate-experiment "search_v2"`

**Phase 2:**
- Statsig: primary `search_to_click` +8.2% (p=0.011, n=12,801 per arm).
- Mixpanel: project-level `search_to_click` +0.4% (essentially flat).
- DD: all guardrails clear.

**Phase 3 — Reconciliation:**

| Metric | Statsig | Mixpanel | DD | Verdict |
| --- | --- | --- | --- | --- |
| `search_to_click` | +8.2% (p=0.011) | +0.4% | n/a | **DISAGREE** |
| guardrail `error_rate` | n/a | n/a | -0.05% | within tolerance |
| guardrail `p99_latency_ms` | n/a | n/a | +2ms | within tolerance |

**Phase 4:**

```markdown
## Verdict: iterate

**Reason:** Statsig reports +8.2% on `search_to_click` but Mixpanel sees only +0.4% at the project level. This 20x discrepancy suggests one of:
1. **Metric-definition divergence:** Statsig and Mixpanel may compute `search_to_click` differently (different filter rules, different attribution windows).
2. **Splice imbalance:** the experiment cohort may be unrepresentative (e.g. heavily skewed toward a high-converting segment).
3. **Mixpanel tracking change:** an event-tracking change (rename, SDK version) may be hiding the lift in Mixpanel.

Investigate before shipping. DD guardrails are clear, so latency / error risk is low — the question is whether the Statsig win is real.

**Confidence:** medium
- DD guardrails clear (no veto).
- Statsig sample size satisfies power.
- BUT Mixpanel cross-check fails — direction agrees but magnitudes diverge by 20x.

## Recommended probes (before re-running this verdict)
- Pull both metric definitions: `/adk-investigate:investigate-statsig "search_to_click" --use metrics-catalog` and the Mixpanel Lexicon.
- Compare splice composition: who's in the experiment cohort? Are they higher-converting on average?
- Check Mixpanel tracking history: `/adk-investigate:investigate-statsig --use audit-log` for any related changes.
```

---

## Example 4 — kill (no significant lift)

**Prompt:** `/adk-investigate:investigate-experiment "homepage_redesign_v2"`

**Phase 2:**
- Statsig: primary `signup_completed` +0.6% (p=0.41, n=15,200 per arm).
- Mixpanel: project-level +0.3% (flat).
- DD: all guardrails clear.

**Phase 3:** sample size satisfies power; lift is not significant.

**Phase 4:**

```markdown
## Verdict: kill

**Reason:** Sample size satisfies power (n=15,200 per arm > 7,800 target) and 14 days in experiment. Despite this, primary lift is +0.6% with p=0.41 — not significant. Mixpanel project-level +0.3% confirms (no real movement). DD guardrails clear, but with no detectable lift, there's no signal to iterate on.

**Confidence:** high
- All 3 sources agree: no real movement.
- Sufficient power and duration.
- Free up the experiment slot for the next test.
```
