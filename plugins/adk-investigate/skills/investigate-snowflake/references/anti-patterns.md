# `investigate-snowflake` — anti-patterns

## "Just run the query, I trust you"

- The operator may insist. The skill does not skip the SQL display. Always print the SQL.
- **Fix:** every Phase 2 prints the SQL before execution. First query of session has a confirmation gate even under `--auto`.

## Returning all rows

- "Show me all orders today" → `SELECT * FROM orders WHERE order_date = today` returns 100k rows. The skill aggressively limits to 100 by default.
- **Fix:** always `LIMIT 100`. If the operator wants more, they pass `--limit <N>` and confirm.

## Joining across pods without a documented data-product map

- "Join `orders` from OMS with `users` from COMMERCE on `user_id`" — but the foreign key is owned by neither pod, and the join semantics may be wrong (1:N? eventually consistent?).
- **Fix:** check `snowflake.md.common_views` for documented joins. If not documented, stop and ask. The risk is silent garbage results.

## Querying PII columns

- "What's the email of user X?" — REFUSE. The PII guardrail blocks any column matching `pii_columns.block_substring` (`email`, `phone`, `address`, `ssn`, `name_full` by default) or `block_token_columns` (`DET_*`, `RAND_*`).
- **Fix:** the skill refuses, names the matched column, and suggests re-phrasing without PII OR escalating to a service account with proper access controls.

## Treating Snowflake as billing's source of truth

- "Revenue today per Snowflake = $X". Snowflake might be a delayed mirror; the production DB is the ledger.
- **Fix:** for billing-of-truth queries, redirect to the production DB. Snowflake's `revenue` view may have refresh delays, sample weighting, or filter exclusions that the operator doesn't know about.

## Pasting 100 raw rows in the report

- A markdown table with 100 rows is unreadable.
- **Fix:** aggregate. Top-20 by primary metric. Histogram for distributions. Single number for "how many". Save the raw 100 rows to `.temp/.../raw/` for the operator to grep.

## Using a warehouse / role outside the documented defaults

- "Use `WH_BIG` instead of `COMPUTE_WH`" — but the operator may not have access; or `WH_BIG` may cost 8x more credits.
- **Fix:** require explicit `--warehouse <name>` flag. Confirm under `--auto` if non-default.

## Running DML / DDL / GRANT

- The role `ANALYST_RO` doesn't have permission anyway, but the SQL string validator is a second line of defense.
- **Fix:** the Phase 2 validator rejects any SQL containing `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `CREATE`, `ALTER`, `DROP`, `GRANT`, `REVOKE` before execution. Any attempt is logged.

## Forgetting freshness caveats

- The view `orders_daily` may refresh every 6h. Querying it for "orders in the last hour" returns nothing — and the operator may misinterpret "no orders" as a real outage.
- **Fix:** report includes a `Caveats` line with view freshness if known, or "freshness unknown — verify with the data team".

## Saving raw results outside `.temp/`

- The `.temp/` folder is gitignored. Anywhere else may end up in a commit.
- **Fix:** raw saves are pinned to `.temp/task-<slug>/investigation/snowflake/raw/`. The skill validates the path before writing.
