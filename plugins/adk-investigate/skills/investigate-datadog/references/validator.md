# `investigate-datadog` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/investigate-datadog.md`.

## Phase 0 — pre-execution

- [ ] User's question captured verbatim.
- [ ] `--use` resolved to one of `investigate`, `dashboard-summary`, `alert-triage`.
- [ ] Time window resolved to a concrete `[from, to]` pair. No "recently" or "the past few hours".
- [ ] Environment resolved to a concrete tag (`prod`, `staging`, etc.). Not `*` unless explicitly opted-in.
- [ ] Service resolved if shorthand was used. Marked `verified` (matched `service_aliases`) or `inferred` (literal pass-through).
- [ ] If `--use dashboard-summary` and dashboard named by name, id was resolved from `datadog.md.common_dashboards`.

## Phase 1 — preflight

- [ ] `bin/adk-mcp-health --shipped` shows `datadog: connected`.
- [ ] `DATADOG_API_KEY` env var present (legacy `DD_API_KEY` also accepted).
- [ ] `DATADOG_APP_KEY` env var present (legacy `DD_APP_KEY` also accepted).
- [ ] `bin/adk-info --check datadog` returns 0.
- [ ] `~/.config/adk/datadog.md` has the keys this run needs (`site`, `default_env`, `default_window`, plus `service_aliases` if shorthand was used).

## Phase 2 — execute

- [ ] Each query string is logged to `.temp/task-<slug>/investigation/datadog/queries.md` before execution.
- [ ] Each query has a time window and an env tag (no `env:*`).
- [ ] Raw MCP responses written to `raw/` for traceability.
- [ ] No `mcp_write` tool invoked (any attempt → fail loud).
- [ ] No more than 5 queries in a single Phase 2 (force operator into the iteration loop after that).

## Phase 3 — summarize

- [ ] Every numeric result has a `Baseline` column populated (or explicit `n/a — first window`).
- [ ] Every result row has a DD UI link.
- [ ] No raw log lines pasted (aggregated only, with link to raw).
- [ ] If a likely cause is named, confidence stated (`low | medium | high`).

## Phase 4 — pre-handoff

- [ ] `.temp/task-<slug>/investigation/datadog.md` exists.
- [ ] All sections present in correct order: `Query`, `Resolved entities`, `Results`, `Trends`, `Anomalies`, `DD UI links`, `Follow-up queries`.
- [ ] Every artifact referenced in the report exists at the cited path.
- [ ] Final status banner printed.

## On any check failure

- Log the failure to `validation/investigate-datadog.md` with the failing check + remediation.
- Block the next phase until the failure is resolved.
- If the same check fails 3 times in this session, surface to the user — do NOT loop forever.
