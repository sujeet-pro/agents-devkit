# `investigate-experiment` — output format

## Per-turn status banner

```
[adk-investigate:investigate-experiment] task=<slug> exp=<exp> phase=<0|1|2|3|4|5> mode=<auto|interactive>
```

## Final report

Written to `.temp/task-<slug>/investigation/experiment.md`. Sections in this exact order:

```markdown
# Experiment: <name>

## Resolved entities
| Kind | Surface | Resolved | Source |
| --- | --- | --- | --- |
| experiment | <user surface> | <id> | statsig.md.common_experiments (verified) |
| linked repo | (from common_experiments) | <owner/repo> | linked |
| linked service | (from repos.md) | <service tag> | repos.md (verified) |
| Mixpanel project | (from mixpanel.md) | <project_id> | mixpanel.md (verified) |
| window | (omitted) | since experiment_start (<days> days) | default |
| guardrails | (from statsig.md) | [error_rate, p99_latency_ms] | exposure_metric_conventions.guardrail_metrics |

## Statsig pulse
| Metric | Control | Treatment | Delta | p-value | Significant? |
| primary <metric> | <c> | <t> | <delta> | <p> | yes/no |
| secondary <metric> | <c> | <t> | <delta> | <p> | yes/no |
| guardrail <metric> | <c> | <t> | <delta> | <p> | yes/no |

- Sample: n per arm = <count>; days in experiment = <days>; allocation = <split>.
- Statsig console: [link]

## Mixpanel cross-check
| Metric | Now (<window>) | Baseline (prior <window>) | Delta | Mixpanel UI |
| primary <metric> | <now> | <baseline> | <delta> | [link] |

## Datadog guardrails
| Metric | Service window | Baseline | Delta | p-value (heuristic) | DD UI | Verdict |
| error_rate | <now> | <baseline> | <delta> | <p> | [link] | within tolerance / REGRESSION |
| p99_latency_ms | <now> | <baseline> | <delta> | <p> | [link] | within tolerance / REGRESSION |

## Reconciliation
| Metric | Statsig | Mixpanel | DD | Verdict |
| primary | +X% | +Y% | n/a | agree / disagree |
| guardrail error_rate | n/a | n/a | +Z% | within tolerance / REGRESSION (veto) |
| guardrail p99 | n/a | n/a | +W ms | within tolerance / REGRESSION (veto) |

## Verdict: <ship | iterate | kill>

**Reason:** <one paragraph>

**Confidence:** <low | medium | high>
- <bullet 1>
- <bullet 2>

## Recommended probes (if Verdict = iterate due to disagreement)
- <concrete next probe with command>

## Linked repo recent commits (since experiment_start)
- `<sha>` <author>: "<subject>"

## Follow-up
- If verdict = ship: gate flip happens in the Statsig console or a future
  explicitly write-enabled Statsig workflow.
- If verdict = iterate: <concrete probe or implementation change>.
- If verdict = kill: free up experiment slot; document learning in `/adk-docs:docs-write` (ADR or experiment-retro).
```

## Rules

1. **All three sources are pulled.** If one is unreachable, the verdict has confidence ≤ `low`; do not produce a report claiming `high` confidence.
2. **Reconciliation table is mandatory.** It puts the three numbers side by side.
3. **Verdict is mechanical.** Anchored to `three-source-verdict.md` rubric. Not opinion.
4. **Guardrail veto is explicit.** If any guardrail's verdict is `REGRESSION (veto)`, the overall Verdict CANNOT be `ship`.
5. **Sample size + days-in-experiment** stated for the Statsig pulse claim.
6. **Probes for iterate-due-to-disagreement** are concrete `/adk-investigate:<skill> "<query>"` invocations, not vague suggestions.
