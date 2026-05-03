# `investigate-snowflake` — result limit policy

Default: `LIMIT 100`. The operator can opt for more via `--limit <N>`, with a confirmation gate even under `--auto`.

## Why ≤100 by default

1. **Reports.** A 100-row markdown table is the practical readability limit. Beyond that, the operator wants a summary, not a table.
2. **Cost.** Snowflake credits scale with bytes scanned. `LIMIT 100` doesn't reduce scan size by itself, but it forces the operator to think about what they actually need; without it, the easy mistake is a 1M-row pull.
3. **Memory.** Loading 1M rows into memory as MCP response → JSON → markdown is slow and wasteful.
4. **PII blast radius.** If a non-PII column accidentally contained latent PII (e.g. a `notes` field with email addresses pasted by users), 100 rows leaked is far better than 1M.

## How `LIMIT` is enforced

Phase 2 of the workflow:

1. If the SQL already has a `LIMIT` clause, leave it (don't override the operator).
2. If not, append `LIMIT 100` (or `--limit` value).
3. If `--limit > 100`, ask for confirmation **even under `--auto`**.

```text
SELECT * FROM big_table WHERE x = 1
->
SELECT * FROM big_table WHERE x = 1 LIMIT 100
```

```text
SELECT * FROM big_table WHERE x = 1 LIMIT 50
->
unchanged (operator chose 50)
```

```text
/adk-investigate:investigate-snowflake "..." --limit 5000
->
"You requested 5000 rows (default 100). Confirm?"
```

## When to opt for more rows

- **Aggregations across many groups.** `GROUP BY country` may legitimately produce 200 rows. Use `--limit 250`.
- **Distribution / histogram queries.** Sometimes 1k buckets are needed.
- **One-off bulk export.** This is rare and should usually go through dbt / Airflow instead.

In all cases, justify the limit in the operator's confirmation response.

## Result aggregation in the report

Even with `LIMIT 100`, the report does NOT paste 100 raw rows by default. The aggregation rule from `how-it-works.md`:

| Question shape | Report shape |
| --- | --- |
| "how many" | single number |
| "by `<dimension>`" | top-20 by primary metric |
| "distribution" | histogram / quantiles |
| "raw rows requested" + row count <= 20 | table all |
| "raw rows requested" + row count > 20 | top-20 in report; full result in `raw/` |

## Caveat — `LIMIT` and ORDER

`LIMIT` without `ORDER BY` returns an arbitrary 100 rows. For top-N reasoning, the operator must include `ORDER BY <metric> DESC`. The skill warns if `LIMIT` is present without `ORDER BY` for queries with aggregation or joins.

## Caveat — `LIMIT` and partition pruning

`LIMIT` does not reduce bytes scanned for queries without partition predicates. The skill includes "bytes scanned" in the report's `Cost` section and suggests adding a partition predicate (e.g. `WHERE event_date >= ...`) when the scan is large.
