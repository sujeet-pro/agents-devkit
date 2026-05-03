# `investigate-datadog` — anti-patterns

## Querying without a baseline

- "Errors are up." Up from what? Vs last hour, last 24h, last week? Without a baseline, "up" is just a number.
- "p99 is 880ms." Compared to what? The SLO? The p99 last week? The same time yesterday?
- **Fix:** every metric in the report has a `Baseline` column. If no baseline can be computed (e.g. brand-new metric), say so explicitly.

## Querying without a time window

- DD will return data from "all time" and the result is meaningless (and slow).
- The hosted MCP truncates at ~1k events without a window — and you'll silently miss data.
- **Fix:** always pass a `from`/`to` (or relative `now-1h`). Default `--time` is `last 1h` from `~/.config/adk/datadog.md.default_window`.

## Querying without an environment

- `env:*` mixes prod / staging / dev. Numbers are meaningless.
- **Fix:** always pass `env:prod` (or whichever was resolved). Cross-env queries require explicit `--env "*"` opt-in by the user.

## Pasting raw log lines

- 50 raw `[INFO]` lines is noise. The operator wants to know: how many errors of each class, and which class is biggest.
- **Fix:** use `aggregate_logs` (group by status, error class, host, route). Show top 5 with counts. Link to the raw view in DD UI.

## Inferring causation from correlation

- "p99 spiked at 13:02; the deploy went out at 12:58; the deploy caused it."
- Maybe. Maybe not. The spike could be a downstream service, a Kafka rebalance, a scheduled cron. You need at least one more signal (logs from the new code path? trace showing the new span is slow?) before "deploy caused".
- **Fix:** state confidence. "Deploy at 12:58 looks correlated; confidence medium pending log/trace confirmation." Then go fetch the second signal.

## Modifying anything

- This skill is read-only. The Datadog App key in adk's default config has `mcp_read` only.
- If the user asks "mute the alert", the skill says: "out of scope; use the Datadog UI / a different skill that explicitly opts into `mcp_write`".

## Editorializing

- "Things look bad." Bad how?
- "I think we should rollback." That's the operator's call; you provide evidence.
- **Fix:** state numbers + baselines + links. The operator decides what to do.

## Forgetting the DD UI link

- The prose summary is for orientation. The link is the deliverable. Without it, the operator has to re-construct the query in the DD UI, which is slow and error-prone.
- **Fix:** every result row has a "DD UI" column with a clickable link to the same query at the same window in the DD app.

## Routing to the wrong skill

- If the prompt says "deploys + errors", that's `/adk-investigate:investigate-incident`, not just `investigate-datadog`. Don't try to do the multi-source job from this skill — hand off.
- If the prompt says "experiment pulse", that's `/adk-investigate:investigate-statsig`.
- If the prompt says "funnel" or "DAU", that's `/adk-investigate:investigate-mixpanel`.

## Looping forever on a flaky MCP

- Datadog hosted MCP has variable cold-start latency. After 3 retries, surface the issue and stop.
- Same query that returned an error 3 times → stop and surface the original error verbatim.
