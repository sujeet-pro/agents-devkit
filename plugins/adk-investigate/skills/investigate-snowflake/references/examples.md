# `investigate-snowflake` — worked examples

## Example 1 — count of orders today

**Prompt:** `/adk-investigate:investigate-snowflake "count of orders today"`

**Phase 0:**
- Resolved entities:
  | Kind | Surface | Resolved | Source |
  | --- | --- | --- | --- |
  | view | "orders" | `DW_PROD_STRUCTURED.OMS.orders_daily` | `snowflake.md.common_views` (verified) |
  | warehouse | (omitted) | `COMPUTE_WH` | `snowflake.md.default_warehouse` |
  | role | (omitted) | `ANALYST_RO` | `snowflake.md.default_role` |
  | window | "today" | `CURRENT_DATE()` | NL parse |
- PII check: no PII columns referenced. PASS.

**Phase 1:** preflight green.

**Phase 2:**

```sql
-- Showing SQL before execution (first query of session — confirmation required even under --auto)
SELECT COUNT(*) AS order_count
FROM DW_PROD_STRUCTURED.OMS.orders_daily
WHERE order_date = CURRENT_DATE()
LIMIT 100;
```

User confirms: "yes, run".

**Phase 3:** result: `42,891`.

**Phase 4:**

```markdown
# Snowflake: count of orders today

## Question
"count of orders today"

## SQL
\```sql
SELECT COUNT(*) AS order_count
FROM DW_PROD_STRUCTURED.OMS.orders_daily
WHERE order_date = CURRENT_DATE()
LIMIT 100;
\```

## Result
- order_count: **42,891**

## Warehouse + role
- Warehouse: COMPUTE_WH
- Role: ANALYST_RO

## Caveats
- View `orders_daily` is refreshed at 02:00 UTC daily. Today's count reflects orders placed before the last refresh; recent activity may be missing. For real-time counts, query the production DB.

## Raw result path
.temp/task-<slug>/investigation/snowflake/raw/q1-count-orders-today.json

## Follow-up queries
- `/adk-investigate:investigate-snowflake "orders by hour today"` — drill into temporal pattern.
- `/adk-investigate:investigate-snowflake "orders by SKU category today"` — top-category breakdown.
```

---

## Example 2 — active SKUs by category last 24h

**Prompt:** `/adk-investigate:investigate-snowflake "active SKUs by category last 24h" --limit 20`

**Phase 0:**
- View resolved: `DW_PROD_STRUCTURED.CATALOG.skus_active`.
- PII check: PASS.

**Phase 2:**

```sql
SELECT category, COUNT(DISTINCT sku_id) AS active_sku_count
FROM DW_PROD_STRUCTURED.CATALOG.skus_active
WHERE last_seen_at >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
GROUP BY category
ORDER BY active_sku_count DESC
LIMIT 20;
```

**Phase 4 excerpt:**

```markdown
## Result (top 20 by active_sku_count)
| category | active_sku_count |
| --- | --- |
| apparel-women | 3,481 |
| apparel-men | 2,847 |
| home-decor | 1,902 |
| home-bedding | 1,415 |
| ... | ... |

## Caveats
- View `skus_active` includes only SKUs with `is_visible=true`. Archived SKUs are not in this result.
- View is refreshed every 1h.

## Follow-up queries
- `/adk-investigate:investigate-snowflake "active SKUs by category last 7d"` — extend window for comparison.
```

---

## Example 3 — PII refusal

**Prompt:** `/adk-investigate:investigate-snowflake "list emails of users who placed an order today"`

**Phase 0:**
- PII check: question references "emails" → matches `pii_columns.block_substring` `["email", ...]`. **REFUSE.**

**Phase 2 — does not run.**

**Output:**

```markdown
# Snowflake: REFUSED — PII column matched

## Question
"list emails of users who placed an order today"

## Refusal reason
The question references the column `email`, which matches the PII block list (`pii_columns.block_substring`) in `~/.config/adk/snowflake.md`. This skill refuses any query touching PII columns regardless of the requesting user.

## Suggested alternatives
1. Re-phrase without PII: "count of orders today" or "orders by SKU category today".
2. If you genuinely need user emails for a legitimate purpose:
   - Use a service account with proper access controls (check with the security team).
   - Document the use case in a Jira ticket / Linear issue and route through the data engineering escalation path.

## No SQL was executed.
```
