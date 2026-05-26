# adk-investigate — hard rules + refusals

## Hard rules

1. **Always pin a window.** No vague time references.
2. **Two-source minimum** before naming a root cause.
3. **State confidence with evidence count** on every non-trivial claim.
4. **Never modify** a monitor / dashboard / gate / experiment / data table.
5. **Lowest-blast-radius first**: rollback > flag-off > restart > investigate-PR > escalate.
6. **Refuse PII queries** against columns listed in `connectors/<source>.json5` `pii_columns`.
7. **Quote ≤15 words per source** verbatim; link out for the rest.

## Refusals

- No service mapping in overrides → ask which repo / service.
- Symptom too vague ("X is slow" without metric) → ask for the metric (p99? error rate?).
- Single-source diagnosis attempted → refuse to conclude; report "leading hypothesis", require a second source.
- DD MCP unreachable → stop in Phase 1 with the named env-var gap.
- Required Statsig audit access missing → for RCA, refuse; for incident, proceed with `[statsig: skipped]`.
