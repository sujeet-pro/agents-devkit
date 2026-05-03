# `investigate-experiment` — three-source verdict rubric

The mechanical rule for translating Statsig pulse + Mixpanel cross-check + DD guardrails into a `ship | iterate | kill` recommendation.

## Inputs

| Input | Source |
| --- | --- |
| `statsig.primary.delta` | Statsig `Get_Experiment_Results` |
| `statsig.primary.p` | Statsig |
| `statsig.n_per_arm` | Statsig |
| `statsig.days_in_experiment` | Statsig (`Get_Experiment_Details_by_ID.start_date`) |
| `statsig.guardrails[]` | Statsig (per metric in `exposure_metric_conventions.guardrail_metrics`) |
| `mixpanel.primary.delta` | Mixpanel project-level over experiment window vs prior-equal-window |
| `dd.guardrails[]` | DD `get_metrics` for service over experiment window vs prior-equal-window |

## Power target

Default: `5% MDE @ 80% power` → `n_per_arm_target` ~= 7,800 for typical 10% conversion baseline. Adjust per `~/.config/adk/statsig.md.power_target` if set, or per the experiment's `target_n` if `Get_Experiment_Details_by_ID` returns one.

## Time-in-experiment target

Default: 7 days (one full week — captures weekday/weekend variance).

Override:
- `statsig.md.common_experiments[<exp>].target_duration_days` if set.
- 30 days if the product has monthly cycles (subscription renewals).
- Never decide during a high-variance window (holiday, sales event).

## The rubric (in order)

```text
guardrail_veto = ANY dd.guardrails[].verdict == REGRESSION (i.e. delta wrong direction at p<0.1)

if guardrail_veto:
    verdict = "iterate"  (or "kill" if guardrail miss is catastrophic AND no plausible iteration path)
    reason = "Guardrail miss: <metric> regressed <delta> (p=<p>); veto active. Iterate to remove the regression cost."
    confidence = "high" if veto unambiguous else "medium"
    return

mixpanel_agrees = abs(mixpanel.primary.delta) >= 0.5 * abs(statsig.primary.delta)
                  AND sign(mixpanel.primary.delta) == sign(statsig.primary.delta)

if statsig.primary.delta > 0 AND statsig.primary.p < 0.05:
    if NOT mixpanel_agrees:
        verdict = "iterate"
        reason = "Statsig +<X>% but Mixpanel project-level +<Y>% (>50% magnitude divergence). Investigate: metric-definition drift, splice imbalance, or tracking change."
        confidence = "medium"  # DD guardrails clear, but signal trustworthiness questionable
        probes = [
          "/adk-investigate:investigate-statsig <exp> --use metrics-catalog",
          "Compare Mixpanel Lexicon definition of <metric> with Statsig's metric definition",
          "Check splice composition in Statsig (cohort skew analysis)",
        ]
        return

    if statsig.days_in_experiment < target_days:
        verdict = "iterate"
        reason = "Insufficient time-in-experiment: <days> < <target_days>. Week-of-day / cycle effects unmeasured."
        confidence = "medium"
        return

    if statsig.n_per_arm < n_per_arm_target:
        verdict = "iterate"
        reason = "Underpowered: n=<n> < <target>. Let it run."
        confidence = "low"
        return

    # All criteria met
    verdict = "ship"
    reason = "Significant primary lift +<X>% (p=<p>); Mixpanel project-level +<Y>% confirms; DD guardrails clear; n=<n> per arm >= power target; days-in-experiment <days> >= <target_days>."
    confidence = "high"
    return

elif statsig.primary.p > 0.05:
    if statsig.n_per_arm >= n_per_arm_target:
        verdict = "kill"
        reason = "Powered (n=<n>); no significant lift detected (p=<p>). Free up the slot."
        confidence = "high"
    else:
        verdict = "iterate"
        reason = "Underpowered (n=<n> < <target>); let it run before deciding."
        confidence = "low"
    return

elif statsig.primary.delta < 0:
    verdict = "kill"
    reason = "Negative primary effect (<delta>%; p=<p>). No signal to iterate on."
    confidence = "high"
    return
```

## Confidence anchors

- `high`: all three sources align (or veto is unambiguous; or kill criteria are crisp).
- `medium`: 2 of 3 align, third has known issue (definition drift, source unreachable); OR veto borderline.
- `low`: only 1 source has a clear signal; OR a critical source unreachable; OR sample size below target.

## Edge cases

| Scenario | Verdict |
| --- | --- |
| Statsig says big lift but DD says no traffic for service | iterate; check whether the splice is reaching prod. Investigate the rollout config. |
| Mixpanel project-level >> Statsig delta | iterate; the experiment's effect appears smaller than the project's organic change → splice may be underpowered or the experiment is a rounding error in the project's noise floor. |
| Multiple guardrails near veto threshold (each at p~0.08) | iterate; conservative on borderline. |
| Guardrail moves in *good* direction at p<0.1 | bonus signal; mention in `Reason` but doesn't change the rubric output. |
| Negative primary lift but p>0.05 | iterate (underpowered evidence of harm); flag for owner attention. |

## How to use this rubric in the report

The Verdict section's `Reason` quotes from this file's templated reason strings, with placeholders filled in. The Confidence section lists the anchored bullets. The Reconciliation table feeds the rubric inputs.

The operator can audit the verdict by reading the rubric inputs vs. the template — there is no hidden judgment.
