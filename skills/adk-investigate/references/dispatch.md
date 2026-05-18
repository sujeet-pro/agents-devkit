# adk-investigate — input dispatch

> Routes by symptom shape OR URL OR explicit `--use <sub-flow>`.

| Input shape | Sub-flow | Reference |
|---|---|---|
| Symptom + service ("checkout 500s", "users see X errors") | incident | `incident.md` (specialized — most common) |
| `--use rca` flag, or "RCA for X" / "post-mortem prep" | rca | `rca.md` |
| `--use experiment` or Statsig experiment URL | experiment | `experiment.md` |
| Datadog URL (incident / monitor / dashboard / logs / trace / apm) | datadog (anchored to resource) | `datadog.md` |
| Mixpanel question / `--use mixpanel` | mixpanel | `mixpanel.md` |
| Statsig URL (gate / audit) / `--use statsig` | statsig | `statsig.md` |
| Snowflake question / `--use snowflake` | snowflake | `snowflake.md` |
| Looker URL / `--use looker` | looker | `looker.md` |

## Composite sub-flows

- **rca** combines `incident` + statsig audit-log ±2h + `git blame` on implicated files + optional mixpanel user-impact pass. Used post-incident.
- **experiment** = Statsig pulse + Mixpanel project-level metric + Datadog guardrails — three-source verdict.

## Ambiguity

- Symptom mentions a service the user has multiple repos for → ask which repo.
- "Why is X slow" without a metric definition → ask: p99? error rate? throughput?
- Slack alert permalink → auto-extracts service + symptom-time; no further classification needed.
