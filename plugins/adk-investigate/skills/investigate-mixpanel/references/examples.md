# `investigate-mixpanel` — worked examples

## Example 1 — funnel signup → first_export

**Prompt:** `/adk-investigate:investigate-mixpanel "funnel signup → first_export last 7d"`

**Phase 0:**
- Resolved entities:
  | Kind | Surface | Resolved | Source |
  | --- | --- | --- | --- |
  | event | `signup` | `signup_completed` | `mixpanel.md.common_events` |
  | event | `first_export` | `first_export` | `common_events` (literal) |
  | funnel | (steps) | `signup_to_first_export` | `common_funnels[].steps` exact match |
  | window | "last 7d" | `2026-04-26..2026-05-03` | NL parse |
  | use | (omitted) | `funnel` | prompt match |

**Phase 1:** preflight green; Mixpanel workspace connector `Connected`.

**Phase 2:**
1. `Get-Report --report-id signup_to_first_export --window last 7d`.
2. Same against `last 7d ending 2026-04-26` (prior 7d) for baseline.
3. Low-traffic check: step 1 = 8,419 users; step 2 = 1,514 users → both > 100, no warning.

**Phase 4 excerpt:**

```markdown
# Mixpanel: funnel signup → first_export last 7d

## Resolved entities
(table)

## Funnel
| Step | Event | Users (last 7d) | % of prior | % of step 1 | Baseline (prior 7d) | Delta |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | signup_completed | 8,419 | — | 100% | 8,901 | -5.4% |
| 2 | first_export | 1,514 | 18.0% | 18.0% | 1,602 | -5.5% |

## Trends
- Step 1 (signup_completed) down 5.4% — within typical week-over-week noise.
- Step 2 (first_export) down 5.5% — proportional to step 1; conversion rate stable at 18.0%.
- No funnel-rate regression.

## Low-traffic warnings
- None.

## Follow-up queries
- `/adk-investigate:investigate-mixpanel "DAU last 7d vs prior 7d"` — confirm the upstream traffic dip.
- `/adk-investigate:investigate-deploy acme/storefront --window 7d` — check whether a marketing change is at play.
```

---

## Example 2 — DAU drop suspected

**Prompt:** `/adk-investigate:investigate-mixpanel "DAU yesterday vs same day last week" --use usage-summary`

**Phase 0:** day-aligned baseline: yesterday vs 7-day-prior same-day.

**Phase 2:**
1. `Run-Query "DAU"` for yesterday.
2. Same for 7d-prior same-day.

**Phase 4 excerpt:**

```markdown
# Mixpanel: DAU yesterday vs same day last week

## Result
| Metric | 2026-05-02 | 2026-04-25 | Delta |
| --- | --- | --- | --- |
| DAU | 47,210 | 48,940 | -3.5% |

## Trends
- Day-on-day -3.5% is within typical week-over-week noise.
- Top-event mix unchanged from baseline.

## Low-traffic warnings
- None (DAU at 47k is well above thresholds).

## Follow-up queries
- `/adk-investigate:investigate-mixpanel "top events yesterday vs same day last week" --use usage-summary` — drill into which event class shifted.
```

---

## Example 3 — cohort retention with low-traffic warning

**Prompt:** `/adk-investigate:investigate-mixpanel "retention of beta_users cohort last 30d" --use cohort`

**Phase 0:**
- `beta_users` cohort resolved from `mixpanel.md.common_cohorts` (definition: `users with property is_beta=true`).
- Window: `last 30d`.

**Phase 2:**
1. Cohort size at start of window: 23 users.
2. Retention at D1, D7, D30: 19, 14, 11.
3. Compare to control cohort `all_users`: D1=72%, D7=44%, D30=28%.

**Phase 4 excerpt:**

```markdown
# Mixpanel: retention of beta_users cohort last 30d

## Cohort
- Definition: users with property `is_beta=true`.
- Size: 23.
- Window: 2026-04-03..2026-05-03.

## Retention
| Day | beta_users | beta_users % | all_users % | Delta |
| --- | --- | --- | --- | --- |
| D1 | 19 | 82% | 72% | +10pt |
| D7 | 14 | 60% | 44% | +16pt |
| D30 | 11 | 47% | 28% | +19pt |

## Low-traffic warnings
- **n=23 — small cohort; retention numbers are directional, not conclusive.**
  - For a ship/iterate decision, wait for n ≥ 100.

## Trends
- Beta cohort retains better than all-users at every checkpoint, but the delta confidence is low at this n.

## Follow-up queries
- `/adk-investigate:investigate-mixpanel "top events for beta_users vs all_users last 30d" --use usage-summary` — see what the betas do differently.
```
