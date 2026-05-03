# `investigate-statsig` — worked examples

## Example 1 — pulse for an experiment

**Prompt:** `/adk-investigate:investigate-statsig "checkout_funnel_v3" --use pulse`

**Phase 0:**
- Resolved entities:
  | Kind | Surface | Resolved | Source |
  | --- | --- | --- | --- |
  | experiment | `checkout_funnel_v3` | `exp_a3f9c2e_checkout_funnel_v3` | `statsig.md.common_experiments` (verified) |
  | repo | (from common_experiments) | `acme/storefront` | linked |
  | window | (omitted) | `since experiment_start` | default for pulse |
  | use | "pulse" | `pulse` | explicit |

**Phase 2:**
1. `Get_Experiment_Results --experiment-id exp_a3f9c2e_checkout_funnel_v3`.
2. Surface primary, secondary, guardrails, sample size, time in experiment.
3. Apply pulse-evaluation rubric.

**Phase 4 excerpt:**

```markdown
# Statsig: pulse for checkout_funnel_v3

## Resolved entities
(table)

## Recommendation: iterate
**Reason:** Primary lift +4.2% (n=18,401 per arm; p=0.014) is significant, BUT guardrail `p99_latency_ms` moved +85ms (control 220ms → treatment 305ms; p=0.002). The latency regression vetoes ship; iterate to find a less-expensive implementation.

## Primary metric
| Metric | Control | Treatment | Delta | p-value | Significant? |
| --- | --- | --- | --- | --- | --- |
| checkout_completed | 12.1% | 12.6% | +4.2% (rel) | 0.014 | yes (p<0.05) |

## Secondary metrics
| Metric | Control | Treatment | Delta | p-value |
| --- | --- | --- | --- | --- |
| revenue_per_session | $14.20 | $14.85 | +4.6% | 0.022 |
| time_to_checkout (s) | 47 | 51 | +8.5% | 0.041 |

## Guardrails
| Metric | Control | Treatment | Delta | p-value | Verdict |
| --- | --- | --- | --- | --- | --- |
| error_rate | 0.42% | 0.45% | +7.1% | 0.31 | within tolerance |
| p99_latency_ms | 220 | 305 | +38.6% | 0.002 | **REGRESSION (veto)** |

## Sample
- n per arm: 18,401
- Days in experiment: 9
- Allocation: 50/50

## Linked repo
acme/storefront. Recent commits since experiment start:
- `a3f9c2e` Alice: "implement v3 checkout flow with new pricing engine"
- `b4d1e83` Bob: "fix v3 funnel telemetry"
- `c1a2f7d` Alice: "v3: add fallback for legacy session"

## Statsig console links
- [Experiment overview](https://console.statsig.com/.../experiments/exp_a3f9c2e_checkout_funnel_v3)
- [Pulse view](https://console.statsig.com/.../experiments/.../pulse)

## Follow-up queries
- `/adk-investigate:investigate-experiment "checkout_funnel_v3"` — full three-source verdict (Statsig + Mixpanel + DD).
- `/adk-investigate:investigate-datadog "p99 on checkout last 9d"` — confirm DD sees the latency regression.
```

---

## Example 2 — audit log for incident triage

**Prompt:** `/adk-investigate:investigate-statsig "what changed in last 60m?" --use audit-log`

**Phase 0:**
- Window: `last 60m` (default for `audit-log`).

**Phase 2:**
1. `Get_Audit_Logs --since now-60m --until now`.
2. Filter to `gate_change`, `experiment_change`, `config_change`, `metric_change`.
3. Group by object + actor.

**Phase 4 excerpt:**

```markdown
# Statsig: audit log last 60m

## Timeline (4 changes)

| Time (UTC) | Object | Action | Actor | Statsig |
| --- | --- | --- | --- | --- |
| 13:01:42 | gate `checkout_redesign` | targeting rule updated (rolled out 50% → 100%) | alice | [link] |
| 12:48:11 | experiment `pdp_image_carousel` | started | bob | [link] |
| 12:31:55 | metric `revenue_per_session` | definition edited (added refund subtraction) | carol | [link] |
| 12:15:08 | gate `search_v2` | killswitch triggered | dave | [link] |

## Most likely incident-relevant
The `checkout_redesign` rollout from 50% to 100% at **13:01:42 UTC** correlates strongly with the symptom timestamp.

## Confidence
**Medium** — temporal correlation is strong (13:01:42 vs 13:02 symptom), but no DD/log signal cross-checked yet from this skill alone. Recommend chaining with `/adk-investigate:investigate-incident` for the multi-source view.

## Follow-up queries
- `/adk-investigate:investigate-statsig "checkout_redesign" --use gates-detail` — see exposures and check counts.
- `/adk-investigate:investigate-datadog "errors in checkout last 1h"` — confirm the symptom is from the new code path.
```

---

## Example 3 — gates list filtered by stale

**Prompt:** `/adk-investigate:investigate-statsig "stale gates for storefront" --use gates-list --tag service:storefront-web`

**Phase 2:**
1. `Get_List_of_Gates --tag service:storefront-web --stale 30`.
2. Render as a sorted-by-staleness table.

**Phase 4 excerpt:**

```markdown
# Statsig: stale gates (service:storefront-web)

## Result (5 stale gates, last evaluated > 30d)

| Gate | Owner | Last evaluated | Last modified | Status |
| --- | --- | --- | --- | --- |
| pdp_redesign_v1 | alice | 2025-03-15 | 2025-03-15 | passing (100%) |
| search_legacy_killswitch | bob | 2025-04-02 | 2025-04-02 | disabled |
| holiday_banner_2025 | marketing | 2025-12-26 | 2025-12-26 | passing (0%) |
| ab_test_homepage_v2 | carol | 2025-08-09 | 2025-08-09 | passing (100%) |
| feature_flag_legacy_cart | dave | 2025-06-21 | 2025-06-21 | disabled |

## Trends
- 3 gates at 100% rollout that haven't been touched in months — candidates for removal (clean up the dead-code branch).
- 2 disabled gates that may be reactivated if needed; check repo for code that still references them.

## Follow-up queries
- For each "passing 100%" stale gate: `/adk-investigate:investigate-statsig "<gate>" --use gates-detail` to confirm before flagging for removal in code.
```
