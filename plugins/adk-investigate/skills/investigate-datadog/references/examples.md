# `investigate-datadog` — worked examples

## Example 1 — "errors in checkout last 1h"

**Prompt:** `/adk-investigate:investigate-datadog "errors in checkout last 1h"`

**Phase 0:**
- Restated: "Count of error logs for service `checkout-api` (resolved from alias) in the last 1h, env=prod."
- Resolved entities:
  | Kind | Surface | Resolved | Source |
  | --- | --- | --- | --- |
  | service | "checkout" | `checkout-api` | `datadog.md.service_aliases` (verified) |
  | window | "last 1h" | `now-1h..now` | NL parse |
  | env | (omitted) | `prod` | `datadog.md.default_env` (verified) |
  | use | (omitted) | `investigate` (logs) | prompt match |

**Phase 1:** preflight green. `datadog` MCP `connected`; `DD_API_KEY` and `DD_APP_KEY` present.

**Phase 2:**
1. Build query: `service:checkout-api env:prod status:error` over `[now-1h, now]`.
2. `aggregate_logs` group-by `error.message` → top 5 error groups.
3. `get_logs` top 3 raw lines per group (for spot-checking).
4. Compute baseline: same query against `[now-25h, now-24h]` (same hour yesterday).

**Phase 4 — `.temp/task-<slug>/investigation/datadog.md`:**

```markdown
# Datadog: errors in checkout last 1h (prod)

## Query
`service:checkout-api env:prod status:error` — last 1h.

## Results
| Error class | Count (last 1h) | Baseline (same hour yesterday) | Delta | Top sample |
| --- | --- | --- | --- | --- |
| `PaymentTimeout` | 412 | 38 | +984% | `[link to log line]` |
| `NullPointerException at OrderService.line47` | 88 | 0 | new | `[link]` |
| `RateLimitExceeded` | 24 | 22 | +9% | `[link]` |

## DD UI links
- [Errors aggregated](https://app.datadoghq.com/logs?query=service%3Acheckout-api+env%3Aprod+status%3Aerror&from_ts=...)
- [PaymentTimeout filter](https://app.datadoghq.com/logs?query=...PaymentTimeout...)

## Trends
- `PaymentTimeout` jumped from baseline ~40/hr to 412/hr — leading anomaly.
- `NullPointerException at OrderService.line47` is brand new in this window.

## Follow-up queries
- `/adk-investigate:investigate-datadog "p99 latency on checkout last 1h"` — confirm the timeout class.
- `/adk-investigate:investigate-deploy acme/checkout-api --window 1h` — check what shipped.
- `/adk-investigate:investigate-incident "PaymentTimeout spike" --service checkout` — full triage.
```

---

## Example 2 — "summarize the Production Overview dashboard"

**Prompt:** `/adk-investigate:investigate-datadog "summarize the Production Overview dashboard" --use dashboard-summary`

**Phase 0:**
- Resolved: `Production Overview` → id `abc-123-xyz` from `datadog.md.common_dashboards`.
- Window: default `last 1h`.

**Phase 2:**
1. `list_dashboards` to get the dashboard tile list.
2. For each tile, call its underlying query at `last 1h`.
3. Compare each tile to a baseline (same hour yesterday).

**Phase 4 — output excerpt:**

```markdown
## Tiles
| Tile | Now | Baseline | Status | DD UI |
| --- | --- | --- | --- | --- |
| Total request rate (5xx) | 0.42% | 0.45% | normal | [link] |
| p99 checkout-api | 880ms | 220ms | ANOMALY (+300%) | [link] |
| p99 storefront-web | 410ms | 380ms | normal | [link] |
| Kafka consumer lag (orders) | 1.2k | 1.1k | normal | [link] |
| DB connection pool utilization | 92% | 60% | ANOMALY (+53%) | [link] |
| Active monitors | 4 firing | 1 firing | ANOMALY | [link] |

## Anomalies (highlighted)
- **p99 checkout-api at 880ms** vs baseline 220ms (+300%).
- **DB pool 92%** vs baseline 60%.
- **4 monitors firing** vs baseline 1.

## Follow-up
- Two correlating signals (checkout p99 + DB pool) → likely a slow query introduced today.
- Suggested: `/adk-investigate:investigate-incident "checkout p99 spike + DB pool" --service checkout`.
```

---

## Example 3 — "which monitors are firing"

**Prompt:** `/adk-investigate:investigate-datadog "which monitors are firing on checkout?" --use alert-triage --monitor-tag service:checkout-api`

**Phase 2:**
1. `get_monitors --state Alert,Warn,No\ Data --tag service:checkout-api`.
2. For each, fetch last evaluation + triggered-at.
3. Cross-reference: any deploy in `acme/checkout-api` between earliest triggered-at and 30min before? (`gh run list --workflow=deploy --limit 20`.)

**Phase 4 — output excerpt:**

```markdown
## Monitors firing (service:checkout-api)
| Monitor | State | Triggered | Severity | Likely cause |
| --- | --- | --- | --- | --- |
| Checkout error rate > 1% | Alert | 13:02 UTC | P1 | deploy `a3f9c2e` at 12:58 UTC |
| Checkout p99 > 500ms | Alert | 13:02 UTC | P2 | (same deploy) |
| Checkout success rate < 99% | Warn | 13:05 UTC | P2 | (downstream of above) |
| Order webhook delivery | No Data | 12:58 UTC | P3 | reporter dropped at deploy time |

## Grouping
All four triggered at or just after the 12:58 deploy → likely the same root cause. Recommend:
- `/adk-investigate:investigate-incident "checkout monitors firing since 13:02" --service checkout-api --window 1h`
```
