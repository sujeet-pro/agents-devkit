# `investigate-snowflake` — output format

## Per-turn status banner

```
[adk-investigate:investigate-snowflake] task=<slug> warehouse=<wh> role=<role> phase=<0|1|2|3|4> mode=<auto|interactive>
```

## Final report

Written to `.temp/task-<slug>/investigation/snowflake.md`. Sections in this exact order:

```markdown
# Snowflake: <one-line restatement>

## Question
<verbatim user question>

## Resolved entities
| Kind | Surface | Resolved | Source |
| --- | --- | --- | --- |
| view | "orders" | DW_PROD_STRUCTURED.OMS.orders_daily | snowflake.md.common_views (verified) |
| warehouse | (omitted) | COMPUTE_WH | snowflake.md.default_warehouse |
| role | (omitted) | ANALYST_RO | snowflake.md.default_role |
| window | "today" | CURRENT_DATE() | NL parse |

## SQL
\```sql
SELECT ...
FROM ...
WHERE ...
LIMIT 100;
\```

## Result summary
<aggregate / top-N / single number>

## Row count
<count>

## Warehouse + role
- Warehouse: <name>
- Role: <name>

## Caveats
- <freshness, coverage, filter assumptions, partition pruning effectiveness>

## Cost (if reported by Snowflake)
- Bytes scanned: <X GB>
- Estimated credits: <Y>

## Raw result path
.temp/task-<slug>/investigation/snowflake/raw/<query-id>.json

## Follow-up queries
- `/adk-investigate:investigate-snowflake "<concrete next query>"` — <one-sentence reason>
```

## On REFUSAL (PII matched)

```markdown
# Snowflake: REFUSED — PII column matched

## Question
<verbatim user question>

## Refusal reason
The question references the column `<column>`, which matches the PII block list (`pii_columns.<rule>`) in `~/.config/adk/snowflake.md`. This skill refuses any query touching PII columns.

## Suggested alternatives
1. <re-phrase without PII>
2. <escalation path: service account / DE engineer>

## No SQL was executed.
```

## Rules

1. **SQL is always shown** in the report, even when execution succeeded.
2. **Result is always aggregated.** Single number / top-N / histogram. Never paste 100 raw rows.
3. **Caveats are explicit** — view freshness, coverage filters, refresh schedule.
4. **Cost is surfaced if available.** Snowflake reports bytes scanned + credits used; include them.
5. **Raw result path is always cited** so the operator can drill in.
6. **Refusal is its own report shape** — no SQL section, no result section; just the refusal reason and alternatives.
