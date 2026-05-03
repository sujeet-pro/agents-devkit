# `investigate-mixpanel` — funnel vs cohort vs saved report

A common modeling mistake is reaching for the wrong primitive. Decision rubric:

## Funnel

> "What % of users move from A to B (to C)?"

- Time-ordered sequence of events per user.
- Each step has a conversion window (default 1 day; some flows need 7d or 30d).
- Output: per-step count + drop-off + overall conversion.
- **Use when:** measuring conversion through a known sequence (signup → first_export, add_to_cart → checkout_completed).
- **Don't use when:** the sequence is loose (no strict order) — use a cohort instead.
- **Failure mode:** funnel hides the *time-to-convert*. If you need "median time from signup to first_export", use `Run-Query` with a `time_to_event()` formula, not a funnel.

## Cohort

> "How does a defined population behave over time?"

- A defined set of users (`users with property X` or `users who did event Y in window`).
- Measured against return events at fixed checkpoints (D1, D7, D30 by default).
- Output: retention curve.
- **Use when:** measuring stickiness, comparing two populations (beta vs control), tracking long-term engagement.
- **Don't use when:** the question is about a single sequence (use funnel) or a cross-section snapshot (use saved report).
- **Failure mode:** small cohorts (`n < 30`) give noisy curves. Always flag.

## Saved report

> "Read a chart that's already defined."

- A funnel / retention / segmentation already saved in Mixpanel by the team.
- Looked up by id from `~/.config/adk/mixpanel.md.common_funnels` (or directly).
- Output: the report's pre-defined visualization values.
- **Use when:** the team has a canonical view ("our standard checkout funnel"); reproducible across sessions.
- **Don't use when:** the question is novel; build ad-hoc with `Run-Query`.

## Run-Query (ad-hoc)

> "Compute something that's not a saved report."

- Arbitrary JQL / formula / segmentation.
- Output: whatever you query.
- **Use when:** the question is novel and you need full control (custom segments, custom time-to-event, custom property combinations).
- **Don't use when:** a funnel / cohort / saved report already answers — those are cheaper to read.

## Decision tree

```
question
  | "X% from A to B" -> funnel
  | "behavior of segment X over time" -> cohort
  | "the standard <thing> chart" -> saved report
  | "novel cross-cut" -> Run-Query
```

## Examples

| Question | Primitive | Why |
| --- | --- | --- |
| "What % of signups complete first_export in 7d?" | funnel | Sequenced steps. |
| "How does the beta cohort retain vs all users?" | cohort | Population + retention curve. |
| "Show me the standard checkout funnel" | saved report | Team has it pinned. |
| "Median time from `add_to_cart` to `checkout_completed` per device" | Run-Query | Custom time-to-event + property segment. |
| "Top countries by `checkout_completed` last 7d" | Get-Events grouped | Aggregation. |
| "Did the new pricing page bump conversion?" | funnel + cohort | Funnel = conversion; cohort = "users who saw new pricing" vs control. |

## Cross-skill rule

If the question mentions an experiment / gate, route to `/adk-investigate:investigate-experiment` — it cross-checks Statsig + Mixpanel + DD for the three-source verdict. `investigate-mixpanel` alone is not enough for ship/iterate decisions.
