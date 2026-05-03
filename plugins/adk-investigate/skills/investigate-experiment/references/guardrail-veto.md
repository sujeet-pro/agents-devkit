# `investigate-experiment` — guardrail veto

A guardrail veto is the rule that prevents `ship` recommendations on experiments with regressions in non-primary metrics (typically performance, error rate, infra cost). This file codifies the veto.

## What's a guardrail

Guardrails are metrics that should NOT regress under any circumstance, even if the primary metric improves. Default list (from `~/.config/adk/statsig.md.exposure_metric_conventions.guardrail_metrics`):

| Guardrail | Direction-of-good | Why |
| --- | --- | --- |
| `error_rate` | lower | A 5% conversion lift with 2x error rate is a regression in user trust. |
| `p99_latency_ms` | lower | A 5% conversion lift with 50% p99 regression is a regression in user experience for the worst-served users. |
| `crash_rate` | lower | Conversion that comes with crashes is paid for in churn. |
| `revenue_per_session` | higher | (rare; sometimes used as a positive guardrail to ensure we're not optimizing for clicks at the expense of dollars) |

The list is configurable per project / experiment.

## When the veto fires

For each guardrail:

```text
direction_wrong = sign(delta) != direction_of_good_sign
significant   = p < 0.1                  # looser than 0.05 because we're conservative on guardrails
veto_fires    = direction_wrong AND significant
```

If ANY guardrail's `veto_fires == true`, the overall verdict cannot be `ship`. The verdict is `iterate` (default) or `kill` (if the regression is catastrophic and no plausible iteration path exists).

## Why p<0.1 (looser than 0.05)

For the primary metric, we want to be sure we're not shipping noise — `p<0.05` is the standard threshold.

For guardrails, we want to be sure we're not shipping a regression — we'd rather false-positive (block a clean experiment) than false-negative (ship a regression). `p<0.1` is conservative: a 10% chance of being wrong about a regression is acceptable cost vs the risk of shipping a real regression.

This is asymmetry by design.

## Example: clean ship

```text
primary checkout_completed: +4.2% (p=0.014) ← significant lift
mixpanel project-level: +3.8% ← agrees direction
guardrail error_rate:    -0.1% (p=0.71)  ← within tolerance
guardrail p99_latency:   +5ms  (p=0.32)  ← within tolerance

veto = false
verdict eligible for ship
```

## Example: veto active

```text
primary checkout_completed: +4.2% (p=0.014) ← significant lift
mixpanel project-level: +3.8% ← agrees direction
guardrail error_rate:    +1.1% (p=0.45)  ← within tolerance
guardrail p99_latency:   +85ms (p=0.002) ← REGRESSION; p<0.1 → veto fires

veto = true
verdict = iterate (or kill if no plausible iteration path)
```

## When the veto can be temporarily relaxed

In rare, well-justified cases the operator may explicitly opt-in to ship despite a guardrail miss. This skill does NOT support that — the veto is mechanical here.

If the operator has a good reason (e.g. business-critical launch, mitigations in place), they:
- Document the trade-off (in `/adk-docs:docs-write` as an ADR).
- Get explicit sign-off from the platform team.
- Ship via the Statsig console with eyes open.

This skill won't issue a `ship` recommendation in that scenario. It produces evidence; the operator decides to override.

## Severity gradient (within "REGRESSION")

The verdict is `iterate` for borderline regressions and `kill` for catastrophic ones. Heuristic:

| Guardrail miss size | Verdict |
| --- | --- |
| <2x baseline | iterate (typically fixable with a less-expensive implementation) |
| 2x – 5x baseline | iterate (pause and investigate; major rework needed) |
| >5x baseline | kill (the product change has structural issues; iteration unlikely to recover) |

These are heuristics; operator judgment may override either direction.

## Reporting the veto

The `Datadog guardrails` table marks the offending row(s) with `REGRESSION (veto)`. The `Reconciliation` table aggregates. The `Verdict` paragraph names the veto explicitly.

Example verdict prose:

```markdown
## Verdict: iterate

**Reason:** Primary lift +4.2% (Statsig p=0.014, Mixpanel project-level +3.8% confirms). However, p99_latency_ms regressed +85ms (DD p=0.002, direction-of-good is lower → REGRESSION). The latency regression is a user-experience cost that vetoes ship. Iterate: investigate caching / async paths / lighter computation in the v3 implementation, then re-run.
```

## Cross-skill rule

This veto is enforced by `investigate-experiment`. The single-source `/adk-investigate:investigate-statsig --use pulse` also flags guardrail movements in its own pulse evaluation (`pulse-evaluation.md`), but only the cross-source verdict here applies the *DD-confirmed* guardrail check.

`/adk-investigate:investigate-rca` may invoke `investigate-experiment`'s rubric retroactively to attribute an outage to a known guardrail-failing experiment that shipped anyway.
