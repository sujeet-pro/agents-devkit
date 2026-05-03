# `investigate-snowflake` — mode contract

`investigate-snowflake` is **read-only**. It supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix`.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks documented defaults at every decision:
  - `--warehouse` from `snowflake.md.default_warehouse`.
  - `--role` from `snowflake.md.default_role`.
  - `--limit 100`.
- Still validates after every phase.
- Still surfaces a final report.

**Three exceptions where `--auto` still asks:**

1. **First query of the session.** Always shows the SQL and asks "run?" — even under `--auto`. Subsequent queries under `--auto` run without per-query confirmation, but every SQL is still printed.
2. **`--limit > 100`.** Always asks for confirmation, even under `--auto`. Default is `100`.
3. **PII column matched.** REFUSES. Does not ask; does not execute; surfaces the matched column and stops.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
  - Phase 0: shows resolved view + warehouse + role + db + schema, asks "proceed?".
  - Phase 2: shows the SQL, asks "run it?".
  - Phase 4: shows the proposed report aggregation, asks "publish?".

## `--fix` is not supported

- This skill is read-only. The role in `snowflake.md.default_role` is `ANALYST_RO` (read-only).
- Any DML / DDL / GRANT is blocked at the SQL string level (Phase 2 validator).
- If the operator passes `--fix`, the skill rejects with: "investigate-snowflake is read-only; use a write-enabled role / dbt / a DE engineer for mutations".

## What `--auto` will NEVER do

1. Run DML (`INSERT` / `UPDATE` / `DELETE` / `MERGE`).
2. Run DDL (`CREATE` / `ALTER` / `DROP`).
3. Run GRANT or REVOKE.
4. Query a column matched by `~/.config/adk/snowflake.md.pii_columns.block_substring` or `block_token_columns`.
5. Use a warehouse / role outside `default_warehouse` / `default_role` without explicit user opt-in via flags.
6. Save raw results outside `.temp/task-<slug>/investigation/snowflake/raw/`.
7. Return more than 100 rows without explicit `--limit <N>` from the user.
8. Run a SQL that hasn't been printed first.
