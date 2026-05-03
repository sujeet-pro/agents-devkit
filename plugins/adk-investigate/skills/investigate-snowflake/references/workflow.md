# `investigate-snowflake` — workflow detail

## Phase 0 — prompt expansion

1. **Restate** the user's question in one sentence. ("How many orders were placed today?")
2. **Resolve table / view.** Look up `~/.config/adk/snowflake.md.common_views`. If not matched, ask the user (do not guess across pods).
3. **PII precheck.** Tokenize the question and the candidate columns:
   - For each column referenced in the question (or in the candidate view's schema), check against `pii_columns.block_substring` (`["email", "phone", "address", "ssn", "name_full"]` by default) — case-insensitive substring match.
   - Check against `pii_columns.block_token_columns` (`["DET_*", "RAND_*"]`) — regex match.
   - If any match → **REFUSE**. Stop here. Tell the user which column matched and why. Suggest re-phrasing without PII or escalating to a service account with proper access controls.
4. **Resolve warehouse + role.** `--warehouse` flag wins; else `snowflake.md.default_warehouse` (typically `COMPUTE_WH`). Same for `--role` (typically `ANALYST_RO`).
5. **Resolve database + schema.** From `snowflake.md.default_database` and `default_schema_search_path` (or from the matched common view).

Output: `entities.md` table in `.temp/task-<slug>/investigation/snowflake/`.

## Phase 1 — preflight

1. `claude mcp list` — confirms the workspace `Snowflake (Quince)` connector is `Connected`.
2. `bin/adk-info --check snowflake` — confirms `~/.config/adk/snowflake.md` parses.
3. Confirm the resolved view exists in the resolved database/schema.

## Phase 2 — build SQL

1. **Compose** the SQL. Always:
   - `SELECT` only (no DML / DDL / GRANT — see `read-only-policy.md`).
   - Add `LIMIT <N>` (`100` default; `--limit` flag value).
   - Use the resolved warehouse + role + db + schema.
   - Aggregate where the question implies a count / top-N (don't return raw rows when the user asked "how many").
2. **PII check on the SQL string** (second-line defense against builder mistakes):
   - Reject any SELECT that names a blocked column.
3. **Show the SQL.** Print it. Always. Even under `--auto`.
4. **Confirmation gate** for the first query of any session — even under `--auto`. Subsequent queries in the same session under `--auto` execute without per-query confirmation, but every SQL is still printed.

## Phase 3 — execute

1. Run via the workspace Snowflake MCP using the resolved warehouse + role.
2. Capture result + execution metadata (rows scanned, credits used, partition pruning effectiveness if available).
3. Save raw to `.temp/task-<slug>/investigation/snowflake/raw/<query-id>.json`.

## Phase 4 — summarize + report

1. **Aggregate** the result:
   - If <= 20 rows AND the question asked for raw rows → table all of them.
   - Else → top-N (default 20) by primary metric; histogram for distributions; total count for "how many".
2. **Add caveats**:
   - View freshness (when was it last refreshed).
   - Coverage (any obvious filter, e.g. `is_active=true`).
   - Cost (credits used; if > 5, suggest a tighter predicate).
3. **Emit** `.temp/task-<slug>/investigation/snowflake.md` per `output-format.md`.

## Loop control

- Cap Phase 2 at 5 queries per skill invocation. Force the operator into the iteration loop.
- After 1 PII refusal, the skill remembers and surfaces a one-line reminder ("PII guardrail enforced; see snowflake.md.pii_columns").
- After 1 SQL parse error → reformat and try once more. After a second failure → surface and stop.
- Never re-run the same SQL in one session — output is cached.
