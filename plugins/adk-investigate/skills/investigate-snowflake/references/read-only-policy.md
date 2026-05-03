# `investigate-snowflake` — read-only policy

Hard rule: this skill executes only `SELECT` (and `SHOW` / `DESCRIBE`) statements. Any DML / DDL / GRANT is rejected at the SQL string level before execution.

## What's blocked

The Phase 2 SQL validator tokenizes the SQL and rejects any of these statement keywords (case-insensitive):

| Category | Keywords blocked |
| --- | --- |
| DML | `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE`, `COPY` (when target is a table not a stage) |
| DDL | `CREATE`, `ALTER`, `DROP`, `RENAME`, `COMMENT ON` |
| Permissions | `GRANT`, `REVOKE` |
| Session-altering | `USE` (allowed only for setting warehouse/role/db at session init), `SET PARAMETER` |
| Stored procedures | `CALL`, `EXECUTE` |
| Transactions | `BEGIN`, `COMMIT`, `ROLLBACK` (irrelevant in read-only but blocked for clarity) |

## What's allowed

- `SELECT` — the primary read.
- `WITH` — CTEs in support of `SELECT`.
- `SHOW` (e.g. `SHOW TABLES IN SCHEMA <s>`) — discovery.
- `DESCRIBE` (e.g. `DESCRIBE TABLE <t>`) — schema inspection.
- `EXPLAIN` — query plan analysis (sometimes useful for cost reasoning).

## Why a string-level validator

Even though the role `ANALYST_RO` doesn't have permission to write, the string-level validator is a second line of defense:

1. Catches mistakes (the validator runs before any network call).
2. Surfaces the violation to the operator immediately, without an opaque permission error.
3. Logs the attempted statement for audit (`.temp/task-<slug>/investigation/snowflake/sql/<query-id>-rejected.sql`).

## Validator implementation

```text
1. Strip comments (-- and /* ... */).
2. Tokenize on whitespace and semicolons.
3. Find the first non-WITH-prefix keyword in each statement.
4. If keyword in BLOCKED list → REJECT.
5. If multiple statements separated by `;` → reject (only one statement per query).
```

This is a simple lexer; it does NOT need to be a full SQL parser. It catches the 99% case (intent-level "I'm trying to write to the DB"). The remaining 1% (an exotic Snowflake feature with a write side-effect inside a `SELECT` — e.g. some older `RESULT_SCAN` patterns) is caught by the role-level permission as a backstop.

## Common false alarms

| User wrote | Why blocked | What to write instead |
| --- | --- | --- |
| `SELECT ... INTO ...` | `INTO` clause writes to a stage / table | Use `CREATE TABLE AS SELECT` (also blocked); for read-only export, use `COPY INTO @stage` (blocked); accept that read output goes through the report |
| `EXPLAIN UPDATE ...` | `UPDATE` keyword | `EXPLAIN SELECT ...` to inspect a read plan |
| `SHOW GRANTS ON ...` | `GRANT` substring (false positive) | The validator is keyword-based, not substring-based; `SHOW GRANTS` is fine |

## What to do if a legitimate query is blocked

The skill is conservative by design. If the operator needs a write:

- Use a different role (e.g. `ANALYST_RW` if available) and a different MCP path that opts into write scope.
- Use dbt / Airflow for any persistent transformation.
- Escalate to a DE engineer for one-off mutations.

This skill does NOT escalate to a write-enabled role itself, even with explicit operator opt-in. Read-only is the contract.

## Why one-statement-per-query

Multi-statement queries (separated by `;`) make it easy to hide a `DROP TABLE` after a `SELECT`. The validator rejects multi-statement input. Each `--ask` runs ONE statement.
