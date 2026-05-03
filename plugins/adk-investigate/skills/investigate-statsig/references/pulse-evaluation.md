# `investigate-statsig` — pulse evaluation rubric

How to translate `Get_Experiment_Results` into a `ship | iterate | kill` recommendation.

## Inputs

| Input | Where it comes from | Notes |
| --- | --- | --- |
| Primary lift (relative %) | `Get_Experiment_Results` | The headline number. |
| Primary p-value | `Get_Experiment_Results` | Significance — typically gate at p<0.05. |
| Sample size per arm | `Get_Experiment_Results` | The `n`. |
| Time in experiment (days) | `Get_Experiment_Details_by_ID` (`start_date`) | Calendar duration. |
| Power target (MDE @ confidence) | `~/.config/adk/statsig.md.power_target` (optional) | Defaults to `5% MDE @ 80% power`. |
| Guardrail metrics + p-values | `Get_Experiment_Results` `guardrails` field | The veto inputs. |

## Decision rubric

```
guardrail_veto = ANY guardrail with delta in bad direction at p<0.1

if guardrail_veto:
    recommendation = "iterate" (or "kill" if no plausible iteration path)
    reason = "Guardrail miss: <metric> moved <delta> (p=<p>); <metric> is direction-of-good <good_dir>; veto active"

elif primary_lift > 0 and primary_p < 0.05:
    if time_in_experiment_days >= 7 OR >= 1 business cycle:
        if sample_size_per_arm >= power_target_n:
            recommendation = "ship"
            reason = "Significant primary lift +<lift>% (p=<p>); guardrails clear; n=<n> per arm satisfies <power_target>; <days> days in experiment"
        else:
            recommendation = "iterate"
            reason = "Underpowered: n=<n> per arm < <power_target_n>; let it run"
    else:
        recommendation = "iterate"
        reason = "Insufficient time-in-experiment: <days> < 7 days; week-of-day effects unmeasured"

elif primary_p > 0.05:
    if sample_size_per_arm >= power_target_n:
        recommendation = "kill"
        reason = "Powered (n=<n>); no significant lift detected (p=<p>); free up the slot"
    else:
        recommendation = "iterate"
        reason = "Underpowered (n=<n> < <power_target_n>); let it run before deciding"

elif primary_lift < 0:
    recommendation = "kill"
    reason = "Negative primary effect (<lift>%; p=<p>); no signal to iterate on"
```

## Sample-size targets (default)

If `~/.config/adk/statsig.md.power_target` is unset, use:

- 5% MDE (minimum detectable effect) @ 80% power.
- For typical conversion rates (~10%), this is `n ~ 7,800 per arm`.
- For very small base rates (<1%), this scales up dramatically; `Get_Experiment_Details_by_ID` may include a `target_n` field — use that if present.

## Time-in-experiment

- Default minimum: 7 calendar days (covers one full week, captures weekday/weekend variance).
- For products with monthly cycles (subscription renewals): 30 days.
- For products with seasonal effects (holiday shopping): never decide during a high-variance window.
- Override via the experiment owner's `target_duration_days` in `statsig.md.common_experiments[].target_duration_days` if set.

## Guardrail conventions

Per `~/.config/adk/statsig.md.exposure_metric_conventions.guardrail_metrics`. Typical:

| Metric | Direction-of-good |
| --- | --- |
| `error_rate` | lower |
| `p99_latency_ms` | lower |
| `crash_rate` | lower |
| `revenue_per_session` | higher (a positive guardrail; rare) |

A guardrail moves "wrong" if it goes against direction-of-good with `p<0.1`. (Looser p-threshold for guardrails because we want to be conservative — a 10% chance of false-flagging is acceptable to avoid shipping a regression.)

## Confidence statement

Every recommendation ends with:

```
Confidence: <low | medium | high>
- low: any one of [n underpowered, time too short, single guardrail near veto threshold]
- medium: lift significant, guardrails clear, but one factor borderline
- high: lift significant, guardrails clear, n >> target, duration > target
```

## Example output

```markdown
## Recommendation: iterate
**Reason:** Primary lift +4.2% (n=18,401 per arm; p=0.014) is significant, guardrail `p99_latency_ms` moved +85ms (p=0.002; direction-of-good is lower → REGRESSION). Veto active; iterate on the implementation to remove the latency cost before shipping.

**Confidence:** high — sample size and duration are both sufficient; the veto is unambiguous.
```
