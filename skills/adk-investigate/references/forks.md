# adk-investigate — fork IDs

| fork_id | options | recommendation |
|---|---|---|
| `window` | last-30m / last-2h / last-24h / last-7d / custom | symptom-time ±30min if known, else last-2h |
| `time-resolution` | minute / 5-minute / hour | 5-minute |
| `cross-source-required` | 2 / 3 | 2 (3 for RCA) |
| `confidence-threshold` | medium / high | medium for triage; high for RCA conclusions |
| `blast-radius-ordering` | conservative / standard | standard (rollback > flag-off > restart > investigate-PR > escalate) |
