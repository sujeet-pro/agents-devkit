# `investigate-mixpanel` — workflow detail

## Phase 0 — prompt expansion

1. **Restate** the user's question in one sentence. ("What's the conversion rate from `signup_completed` to `first_export` in the last 7d?")
2. **Resolve event names** from `~/.config/adk/mixpanel.md.common_events`. Mixpanel returns `0` for typos silently — verifying against the Lexicon list catches `checkout_complete` vs `checkout_completed` early.
3. **Resolve funnel id** from `mixpanel.md.common_funnels`:
   - If user named a funnel id verbatim → use it.
   - If user named the steps → match against `common_funnels[].steps`. If exact match, use that funnel id.
   - Otherwise build an ad-hoc funnel from the named events.
4. **Resolve cohort id** from `mixpanel.md.common_cohorts` similarly.
5. **Resolve time window.** `--time` flag wins; else parse NL ("last 7d", "yesterday", "since 2026-04-25"); else `mixpanel.md.default_window` (typically `last 7d`).
6. **Pick `--use`**:
   - "DAU / WAU / MAU / top events / active users" → `usage-summary`
   - "funnel / convert / step / drop-off" → `funnel`
   - "cohort / retention / segment / users who did X" → `cohort`

Output: `entities.md` table in `.temp/task-<slug>/investigation/mixpanel/`.

## Phase 1 — preflight

1. `claude mcp list` — confirms the workspace `Mixpanel` connector is `Connected`. If not, stop with the missing-thing message and the exact `claude mcp add ...` invocation; never auto-install.
2. `bin/adk-info --check mixpanel` — confirms `~/.config/adk/mixpanel.md` parses and has the keys this run needs.
3. (Optional, fast) Pull the project's Lexicon URL via `Get-Lexicon-URL` and cache for the session. Used to validate event names cheaply without hitting `Get-Events`.

## Phase 2 — execute (per `--use`)

### `--use usage-summary`

1. **Top events.** `Get-Events --window <window> --top 20 --by event_name`. Returns count per event.
2. **DAU / WAU / MAU.** `Run-Query` with the standard `Daily Active Users` query, scoped to `<window>`.
3. **Compare to baseline.** Same query against the prior window of equal duration (or same period last week if `--time` is week-aligned).
4. **Compute deltas.** `now / baseline - 1` as percent. Flag deltas > ±10% as `NOTABLE`; > ±25% as `ANOMALY`.
5. **Top retention curves** for the top 5 events (cohort = "users who did X in window", retention measured at D1, D7, D30).

### `--use funnel`

1. **Resolve funnel id** (Phase 0).
2. **Run** `Get-Report --report-id <funnel-id> --window <window>` (if saved) OR `Run-Query` with the funnel definition (if ad-hoc).
3. **Per-step conversion + drop-off.** Each step: count, % of prior, % of step 1.
4. **Compare to baseline.** Same funnel against prior-equal window.
5. **Low-traffic check.** If any step has `n < 100`, flag it. If step 1 has `n < 100`, the entire funnel is suggestive at best.
6. **Tracking-change check.** If any step's count dropped to ~0 abruptly (vs baseline), flag "possible event-tracking change — check the Lexicon and the deploy timeline before concluding the product broke".

### `--use cohort`

1. **Resolve cohort id** (Phase 0). If ad-hoc cohort, build the definition (`users who did <event> in <window>` is the default).
2. **Cohort size.** Count of users in the cohort.
3. **Retention curve.** D1, D7, D30 (or `--retention-days <list>` if provided).
4. **Compare to control cohort** if specified (`--control-cohort <id>` or `--control "all users"`).
5. **Low-traffic check.** If cohort `n < 30`, the report says "small cohort; treat directionally".

## Phase 3 — summarize

1. **Top trends** — biggest deltas from baseline.
2. **Anomalies** — outliers (>2σ), zero counts where there should be data, drops correlating with tracking changes.
3. **Low-traffic warnings** — explicit list of any step / cohort with `n` below thresholds.
4. **Mixpanel UI links** — every result row has a clickable link.
5. **Follow-up queries** — concrete next `/adk-investigate:investigate-mixpanel ...` invocations.

## Phase 4 — report

Emit `.temp/task-<slug>/investigation/mixpanel.md` per `output-format.md`. Return path to caller.

## Loop control

- Cap Phase 2 at 5 reports per skill invocation.
- If `Get-Lexicon-URL` already cached this session, do not re-fetch.
- After 3 consecutive zero-count results for events you confirmed exist in the Lexicon, stop and ask the operator — there's likely a tracking outage that's worth surfacing.
