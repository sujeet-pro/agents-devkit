# First-hour post-deploy checklist

The first 60 minutes after a deploy / release stage are when most regressions are caught. Schedule these checks explicitly with named owners and times.

## T+0 to T+5 minutes

- [ ] Deploy succeeded (CI/CD job green; no rollback already triggered by the platform).
- [ ] Service health endpoints return 200 across all instances / regions.
- [ ] Error rate on the changed routes within ±0.5 pp of baseline.
- [ ] No spike in 5xx from the upstream proxy / load balancer.
- [ ] Connection pool / queue depth normal.

## T+5 to T+15 minutes

- [ ] One named human runs the critical-path scenario manually (login → core action → logout / equivalent).
- [ ] Customer-facing pages load (`chrome-devtools` MCP can verify).
- [ ] Web-vitals (LCP, INP, CLS) for the changed surface within budget.
- [ ] Spot-check a customer support channel for new tickets matching the change.
- [ ] APM traces show no new slow query / new dependency call.

## T+15 to T+30 minutes

- [ ] Business KPI for the surface is within ±1% of baseline (orders, sign-ups, search CTR, message-send count, etc.).
- [ ] Background jobs (cron, queue workers) processing normally.
- [ ] Error budget burn rate is within plan.
- [ ] Log volume normal (no flood, no silence).

## T+30 to T+60 minutes

- [ ] All previous checks still green.
- [ ] No customer-reported regression.
- [ ] On-call escalations check: any alerts in the last hour are explainable.
- [ ] Decision: hold this stage / advance to next stage / rollback.

## End-of-window writeup (T+60)

- [ ] Stage status documented (held / advanced / rolled back).
- [ ] Metrics snapshot captured (link or screenshot).
- [ ] Next-stage trigger time scheduled (or rollback if applicable).
- [ ] Post-launch retro scheduled (within 1 week if anything notable happened).

## Anti-patterns

- "Watching Slack" instead of running these checks — explicit beats ambient.
- Skipping the manual critical-path scenario because "the metrics look fine" — metrics lag.
- Promoting to the next stage early because "it's been quiet" — quiet ≠ safe; honor the dwell time.
- Failing to document "we held / we rolled back" — the decision itself is data for the next launch.
