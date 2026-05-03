# `investigate-statsig` — anti-patterns

## Pulse without sample size + p-value

- "Primary metric is up 5%." Up over what n? With what confidence?
- A 5% lift at `n=200` per arm is noise. At `n=20,000` per arm it's real.
- **Fix:** every pulse claim has `n=<count> per arm` and `p=<value>`. Never quote a delta in isolation.

## Recommending ship on a guardrail miss

- Primary metric `checkout_completed` lift +4.2%, p=0.014. Ship!
- But guardrail `p99_latency_ms` moved from 220ms → 305ms (+38%), p=0.002. That's a regression in user experience that the primary metric ignores.
- **Fix:** guardrails are veto power. If any moves in the bad direction at p<0.1, the recommendation is `iterate` (or `kill`), never `ship`. Include the guardrail miss as a callout.

## Treating "2 days of pulse" as ship-ready

- Even with `n=10,000 per arm`, 2 days of data misses week-of-day variance and novelty effects.
- **Fix:** rubric requires either (a) ≥7 days in experiment OR (b) ≥1 full business cycle (depending on the product). Note time-in-experiment in the recommendation reasoning.

## Ignoring the audit log during incidents

- "Latency spiked at 13:02. Likely the deploy at 12:58."
- But the Statsig audit log shows a gate flip at 13:01 to roll out a new code path. That's likely the *real* cause.
- **Fix:** during any incident triage, always pull `audit-log --since (symptom_time - 2h)`. The gate flip / config edit is often the smoking gun the deploy timeline misses.

## Quoting raw audit log entries

- 50 lines of `[2026-05-03T13:01:42Z] gate_change | actor=alice | object=checkout_redesign | action=updated_targeting`. Noise.
- **Fix:** group by `object`, sort by recency, surface the top 5. Each row has all four fields (time, actor, object, action) but de-duplicated.

## Toggling anything

- This skill is read-only. The Statsig API key in adk's default config has `omni_read_only`.
- If the user asks "ship the gate", the skill says: "out of scope; use the
  Statsig console or a future explicitly write-enabled Statsig workflow that
  opts into `omni_write`".

## Using `metrics-catalog` as a primary investigation

- Looking up a metric definition is a *prep* step, not the investigation itself.
- **Fix:** for `pulse` / `experiment` questions, run `metrics-catalog` only when you don't recognize a metric in the report. Don't lead with definitions.

## Ignoring statsig.md.common_experiments[].repo

- The repo field links the experiment to the code that implements it. Recent commits in that repo can explain "the experiment lift moved last week" without needing a deeper investigation.
- **Fix:** when an experiment shows unexpected movement, check the linked repo's last 5 commits before concluding it's a real product effect.

## Forgetting Statsig console links

- The console URL has a deep link to the experiment / gate / audit entry.
- **Fix:** every result row has a "Statsig" column with the deep link.

## Hand-rolling the recommendation rubric

- "I think we should ship — the primary lift looks good." That's editorial.
- **Fix:** apply `pulse-evaluation.md` rubric mechanically. The recommendation is `ship | iterate | kill` based on rules; reasoning is the rubric inputs, not your opinion.
