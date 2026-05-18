# adk-review — fork IDs

| fork_id | options | recommendation |
|---|---|---|
| `severity-bar` | blocker+critical-only / critical+should / all-tiers | critical+should |
| `dimensions` | any subset of (correctness, tests, security, perf, readability, consistency) | all six |
| `auto-post-policy` | never / batch-confirm / per-finding-confirm | batch-confirm |
| `confidence-threshold` | medium / high | high for blockers; medium otherwise |
| `nit-tolerance` | skip / cap-3 / show-all | cap-3 |
| `mode` | plan / act / plan-then-act | plan-then-act |
