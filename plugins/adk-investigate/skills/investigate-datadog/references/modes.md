# `investigate-datadog` — mode contract

`investigate-datadog` is **read-only**. It supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` — there is nothing to fix; investigation produces evidence, not changes.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks documented defaults at every decision:
  - `--use investigate` (unless prompt clearly matches `dashboard-summary` or `alert-triage`).
  - `--time` from `datadog.md.default_window` (typically `last 1h`).
  - `--env` from `datadog.md.default_env` (typically `prod`).
  - For `dashboard-summary`: if the dashboard is named in `datadog.md.common_dashboards`, use its id; if multiple match, pick the highest-priority.
- Still validates after every phase (per `validator.md`).
- Still surfaces a final report (results, baselines, DD UI links, follow-up queries).
- Refuses any write action — `mcp_write` is not in scope for this skill.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
  - Phase 0: shows the resolved entities + chosen `--use` + window + env, asks "proceed?".
  - Phase 2: shows the constructed query before executing, asks "run it?".
  - Phase 3: shows the proposed follow-up queries, asks "run any of these?".
- Used when the operator wants to inspect query construction before execution, or iterate on the entity resolution.

## `--fix` is not supported

- This skill is read-only. The Datadog App key in adk's default config has `mcp_read` only.
- If the operator passes `--fix`, the skill rejects it with: "investigate-datadog is read-only; use the Datadog UI for monitor / dashboard edits".

## What `--auto` will NEVER do

1. Modify a Datadog monitor / dashboard / alert / SLO.
2. Mute or unmute a monitor.
3. Resolve / reopen a Datadog incident.
4. Use `mcp_write` scope (the App key should not even have it).
5. Run a query against `env:*` (cross-env) without explicit `--env "*"` opt-in.
6. Quote raw log lines without aggregation.
