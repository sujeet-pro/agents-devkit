# `investigate-mixpanel` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/investigate-mixpanel.md`.

## Phase 0 — pre-execution

- [ ] User's question captured verbatim.
- [ ] `--use` resolved to one of `usage-summary`, `funnel`, `cohort`.
- [ ] Time window resolved to a concrete `[from, to]` pair. No "recently".
- [ ] Every event name in the prompt exists in `~/.config/adk/mixpanel.md.common_events` OR has been verified against the project Lexicon. Marked `verified` or `inferred`.
- [ ] If `--use funnel`, funnel id resolved (saved id or ad-hoc step list).
- [ ] If `--use cohort`, cohort id resolved (saved id or ad-hoc definition).

## Phase 1 — preflight

- [ ] `claude mcp list` shows Mixpanel workspace connector as `Connected`.
- [ ] `bin/adk-info --check mixpanel` returns 0.
- [ ] `~/.config/adk/mixpanel.md` has the keys this run needs (`project_id`, `default_window`, plus `common_events` / `common_funnels` / `common_cohorts` if shorthand was used).

## Phase 2 — execute

- [ ] Each query string is logged to `.temp/task-<slug>/investigation/mixpanel/queries.md` before execution.
- [ ] Each query has a time window (no "all time").
- [ ] Raw responses written to `raw/` for traceability.
- [ ] Baseline query runs alongside the now-query (same shape, prior window).
- [ ] No more than 5 reports in a single Phase 2.
- [ ] No project-mutation tool invoked.

## Phase 3 — summarize

- [ ] Every numeric result has a `Baseline` column populated (or explicit `n/a — first window`).
- [ ] Every result row has a Mixpanel UI link.
- [ ] Low-traffic warnings are explicit. If any step `n < 100` (funnel) or cohort `n < 30`, the report has a `Low-traffic warnings` section listing them.
- [ ] If a likely cause is named, confidence stated.
- [ ] If any step's count dropped >50% vs baseline, the report flags "possible event-tracking change — verify Lexicon and deploy timeline".

## Phase 4 — pre-handoff

- [ ] `.temp/task-<slug>/investigation/mixpanel.md` exists.
- [ ] Sections in correct order: `Question`, `Resolved entities`, `Results`, `Trends`, `Low-traffic warnings`, `Mixpanel UI links`, `Follow-up queries`.
- [ ] Every artifact referenced in the report exists at the cited path.
- [ ] Final status banner printed.

## On any check failure

- Log the failure to `validation/investigate-mixpanel.md` with the failing check + remediation.
- Block the next phase until the failure is resolved.
- If the same check fails 3 times in this session, surface to the user.
