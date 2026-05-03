# `investigate-deploy` — deploy correlation rules

How to tag near-symptom deploys and when to hand off to multi-source triage. The skill **marks candidates** but does **not** name causes.

## Near-symptom tagging

When `--symptom-time T_sym` is provided:

```text
for each deploy with createdAt = T_run:
  delta = T_run - T_sym  (signed seconds; negative = before symptom)
  if abs(delta) <= 30 minutes:
    tag = near-symptom
    sort_key = abs(delta)
```

Default window: ±30 minutes. Tighter (±5min) is too narrow — deploys can take a few minutes to actually affect production after the workflow completes. Wider (±1h) introduces noise.

## Confidence the candidate is the cause

This skill does NOT compute confidence. It surfaces the candidate; confidence comes from the multi-source triage. As guidance for the consumer (`investigate-incident`):

| Signal | Adds confidence |
| --- | --- |
| Deploy ran in the 30 min before symptom | base candidacy |
| Deploy diff includes code in the affected service / module | + |
| Deploy diff has no test for the affected behavior | + |
| Logs show new error class first appearing post-deploy | + |
| Metric movement timed exactly to deploy completion | + |
| Statsig audit log shows a related gate flip in the same window | depends |
| Deploy went out cleanly with no failed runs preceding | neutral |
| Multiple deploys in window | confidence is harder; multiple candidates |

## When a deploy is NOT the cause

- Symptom started **before** the nearest deploy. Tag is `near-symptom` based on time, but causality is reversed.
- Multiple correlated services have no recent deploy → external cause (3rd-party outage, infra event).
- Deploy diff doesn't touch the affected code path. Inspect via `gh pr view <pr>` to confirm.

This skill marks "near-symptom" purely on time; the consumer should check directionality and diff overlap.

## Hand-off rules

When this skill produces near-symptom candidates, the report's `Follow-up` section ALWAYS includes:

```markdown
## Follow-up
- `/adk-investigate:investigate-datadog "errors in <service> last <window>"` — find log/metric signal that matches the new code path.
- `gh pr view <pr-number>` — inspect what changed in `<sha>`.
- `/adk-investigate:investigate-incident "<symptom>" --service <svc> --window <window>` — multi-source triage (this skill + DD + optionally Slack).
```

When NO near-symptom candidates are found:

```markdown
## Follow-up
- No deploys near symptom. Likely external cause: third-party outage, infra event, or a non-deploy config change. Check:
  - `/adk-investigate:investigate-statsig "what changed in last hour?" --use audit-log` — gate flips / config edits.
  - Status pages of upstream dependencies.
  - Datadog event stream for non-deploy events.
```

## When deploys span multiple repos

For a service tagged across multiple repos (e.g. `service:checkout` → `acme/checkout-api` + `acme/checkout-web` + `acme/order-service`), pull deploys for ALL repos. Tag each run independently; the per-repo near-symptom flag is computed per-repo.

The aggregate report has:

```markdown
## Multi-repo summary
| Repo | Deploys in window | Failed | Near-symptom |
| --- | --- | --- | --- |
| acme/checkout-api | 3 | 0 | 1 |
| acme/checkout-web | 2 | 0 | 0 |
| acme/order-service | 1 | 0 | 0 |
```

The "1 near-symptom" in `checkout-api` is the leading candidate; the consumer should drill into it first.

## What this skill never does

- Compute a confidence number for "deploy caused incident".
- Rank candidates beyond `abs(time-delta)` (the consumer ranks by additional signals).
- Auto-trigger any follow-up skill — it suggests; the operator (or `/adk-core:auto`) dispatches.
- Inspect the deploy diff itself — that's `gh pr view` or `/adk-review:review-pr`, not this skill.
