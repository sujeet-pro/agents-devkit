# `investigate-mixpanel` — mode contract

`investigate-mixpanel` is **read-only**. It supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` — there is nothing to fix; investigation produces evidence, not changes.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks documented defaults at every decision:
  - `--use` inferred from the prompt (`usage-summary` / `funnel` / `cohort`).
  - `--time` from `mixpanel.md.default_window` (typically `last 7d`).
  - `--funnel-id` matched from `mixpanel.md.common_funnels` if step set matches.
  - `--cohort-id` matched from `mixpanel.md.common_cohorts` if name matches.
- Still validates after every phase.
- Still surfaces a final report with Mixpanel UI links.
- Refuses any project-mutation tool.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
  - Phase 0: shows resolved events / funnel id / cohort id / window, asks "proceed?".
  - Phase 2: shows the constructed query before executing, asks "run it?".
  - Phase 3: shows proposed follow-up queries, asks "run any of these?".

## `--fix` is not supported

- This skill is read-only. The Mixpanel workspace connector is read-only by nature — the connector exposes 24 query tools, none of which mutate project state.
- If the operator passes `--fix`, the skill rejects with: "investigate-mixpanel is read-only; use the Mixpanel UI for project edits".

## What `--auto` will NEVER do

1. Modify a Mixpanel project, dashboard, report, cohort definition, or saved funnel.
2. Send tracking events (Mixpanel API write paths are not in scope).
3. Treat low-traffic samples as conclusive without flagging them.
4. Use Mixpanel as the billing source of truth — if the operator asks for an exact revenue / refund count, the skill redirects to `/adk-investigate:investigate-snowflake`.
5. Run a query with no time window. Default `last 7d` applies; never `all time`.
