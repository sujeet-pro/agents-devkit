# Pre-launch checklist

Run every item below. Mark each `OK` / `WARN` / `BLOCKER`. Capture in `.temp/notes/ship-<slug>-checklist.md`. Zero BLOCKERs is the gate.

## Code

- [ ] All CI checks green on the merge candidate (lint, typecheck, unit, integration, build, audit).
- [ ] Test coverage on the changed surface is non-decreasing.
- [ ] No `// TODO: before launch` / `FIXME` / `xit` / `it.skip` / `pytest.skip` introduced.
- [ ] No leaked secrets in the diff (`git diff main..HEAD | grep -iE 'password|secret|api[_-]?key|token'`).
- [ ] No `console.log` debugging left behind in shipped paths.
- [ ] No `localhost` / dev-only URLs hardcoded in shipped paths.

## Schema / data

- [ ] DB migrations are forward-only OR a tested reverse migration exists.
- [ ] Migrations are backward-compatible with the previous code version (so rollback works).
- [ ] No destructive migration runs synchronously with deploy (drop column / drop table → separate later step).
- [ ] Long-running migrations have a separate runbook.

## Configuration

- [ ] All new env vars are set in the prod env (and staging).
- [ ] All new feature flags exist in the flag store, default OFF in prod.
- [ ] Secret rotation, if any, is scheduled (not blocking deploy unless the new code requires the new key).
- [ ] Third-party limits (rate limits, quota) verified.

## Security

- [ ] `npm audit` (or equivalent) has no critical / high without an accepted exception.
- [ ] Authn / authz changes have a regression test.
- [ ] Security headers (CSP, HSTS, etc.) tested on a deploy preview.
- [ ] PII handling is documented / unchanged / approved.

## Performance

- [ ] No new long task (>50ms) introduced on hot paths.
- [ ] Bundle size delta is within budget (`bundlesize` or equivalent).
- [ ] N+1 / unbounded query check on changed routes.
- [ ] If perf-critical, a baseline + after measurement exists (handoff from `@adk:build-perf`).

## Accessibility / UX

- [ ] axe-core / Lighthouse a11y score not regressed.
- [ ] Keyboard navigation tested on the new UI.
- [ ] Loading / empty / error states implemented.
- [ ] Responsive at 360 / 768 / 1280.

## Observability

- [ ] Logs are structured and have a `request_id` / `trace_id`.
- [ ] Errors flow to Sentry / equivalent.
- [ ] Metrics: error rate, p95 latency, throughput, business KPI exist on a dashboard.
- [ ] Alerts: error-rate spike, latency-p95 spike, business-KPI drop are configured.
- [ ] Dashboard URL is in the report.

## Rollout & rollback

- [ ] Feature flag exists, OFF in prod by default, with a documented targeting plan.
- [ ] Rollback path is tested or dry-run-validated.
- [ ] Rollback owner is named and online during the launch window.
- [ ] On-call is aware and available for the first hour.

## Documentation & comms

- [ ] CHANGELOG / release notes updated.
- [ ] User-facing comms drafted if external (status page, email, in-app).
- [ ] Internal comms posted (Slack, dashboards updated).
- [ ] Runbook updated with new alert→action mappings.

## Legal / compliance (if applicable)

- [ ] Privacy review for new PII flows.
- [ ] Data-residency requirements honored.
- [ ] Audit-log entries for high-value mutations.
