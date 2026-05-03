# `investigate-mixpanel` — output format

## Per-turn status banner

```
[adk-investigate:investigate-mixpanel] task=<slug> use=<usage-summary|funnel|cohort> phase=<0|1|2|3|4> mode=<auto|interactive>
```

## Final report

Written to `.temp/task-<slug>/investigation/mixpanel.md`. Sections in this exact order:

```markdown
# Mixpanel: <one-line restatement>

## Question
<verbatim user question>

## Resolved entities
| Kind | Surface | Resolved | Source |
| --- | --- | --- | --- |
| event | "signup" | signup_completed | mixpanel.md.common_events (verified) |
| funnel | (steps) | signup_to_first_export | common_funnels (verified) |
| cohort | "power_users" | power_users | common_cohorts (verified) |
| window | "last 7d" | 2026-04-26..2026-05-03 | NL parse |

## Results

### --use usage-summary
| Metric | Now | Baseline | Delta | Status | Mixpanel UI |
| --- | --- | --- | --- | --- | --- |
| DAU | 47,210 | 48,940 | -3.5% | normal | [link] |

### --use funnel
| Step | Event | Users | % of prior | % of step 1 | Baseline | Delta | Mixpanel UI |
| --- | --- | --- | --- | --- | --- | --- | --- |

### --use cohort
| Day | Cohort | % | Control % | Delta | Mixpanel UI |
| --- | --- | --- | --- | --- | --- |

## Trends
- <bullet per significant trend with a number, baseline, and link>

## Low-traffic warnings
- <explicit list of any step / cohort with n below threshold (100 / 30); empty section if none>

## Mixpanel UI links
- [<short label>](https://mixpanel.com/...?from=...&to=...)

## Follow-up queries
- `/adk-investigate:<skill> "<concrete next query>"` — <one-sentence reason>
```

## Rules

1. **Every numeric result has a baseline column.** If no baseline can be computed, write `n/a — first window`.
2. **Every result row has a Mixpanel UI link.**
3. **Low-traffic warnings are explicit and prominent.** Never bury an `n < 100` step in a footnote.
4. **No raw event lists.** Use Mixpanel UI for the row-level detail; the report aggregates.
5. **Confidence statement** when a likely cause is named: end with `Confidence: <low|medium|high> — <one-sentence rationale>`.
6. **Follow-up queries** are concrete `/adk-investigate:<skill> "<query>"` invocations, not vague suggestions.

## Example header

```markdown
# Mixpanel: funnel signup → first_export last 7d

Run at 2026-05-03T14:00Z by `/adk-investigate:investigate-mixpanel --use funnel --time "last 7d"`.
```
