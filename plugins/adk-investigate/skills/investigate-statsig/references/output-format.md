# `investigate-statsig` — output format

## Per-turn status banner

```
[adk-investigate:investigate-statsig] task=<slug> use=<pulse|gates-list|gates-detail|audit-log|metrics-catalog> phase=<0|1|2|3|4> mode=<auto|interactive>
```

## Final report

Written to `.temp/task-<slug>/investigation/statsig.md`. Sections vary by `--use`.

### `--use pulse`

```markdown
# Statsig: pulse for <experiment>

## Resolved entities
(table)

## Recommendation: <ship | iterate | kill>
**Reason:** <one paragraph anchored to the rubric inputs>

## Primary metric
| Metric | Control | Treatment | Delta | p-value | Significant? |

## Secondary metrics
(same shape)

## Guardrails
| Metric | Control | Treatment | Delta | p-value | Verdict |
(verdict: within tolerance | REGRESSION (veto) | improvement)

## Sample
- n per arm: <count>
- Days in experiment: <days>
- Allocation: <split>

## Linked repo (if statsig.md.common_experiments[].repo set)
<owner/repo>. Recent commits since experiment start:
- `<sha>` <author>: "<subject>"

## Statsig console links
- [Experiment overview](...)
- [Pulse view](...)

## Follow-up queries
- `/adk-investigate:investigate-experiment "<exp>"` — full three-source verdict.
```

### `--use audit-log`

```markdown
# Statsig: audit log <window>

## Timeline (<N> changes)
| Time (UTC) | Object | Action | Actor | Statsig |

## Most likely incident-relevant (if symptom-window provided)
<one-paragraph correlation>

## Confidence
**<low | medium | high>** — <one-sentence rationale>

## Follow-up queries
- `/adk-investigate:<skill> "<concrete next query>"` — <reason>
```

### `--use gates-list`

```markdown
# Statsig: gates <filter>

## Result (<N> gates)
| Gate | Owner | Last evaluated | Last modified | Status |

## Trends
- <bullet per noteworthy pattern>

## Follow-up queries
```

### `--use gates-detail`

```markdown
# Statsig: gate <name>

## Current state
- Status: <passing/disabled> at <rollout %>
- Owner: <owner>
- Targeting rules: (table)
- Exposures (last 7d): <count>
- Pass rate: <%>

## Recent audit (this gate)
| Time | Action | Actor |

## Statsig console
- [Gate detail](...)
```

### `--use metrics-catalog`

```markdown
# Statsig: metric <name>

## Definition
- Type: <count | sum | unique | ratio | percentile>
- Source events: (list)
- Computation: <formula>
- Is guardrail? <yes/no>

## Statsig console
- [Metric detail](...)
```

## Rules

1. **Every numeric claim has `n` and `p-value`** (for pulse).
2. **Every guardrail verdict explicit** (`within tolerance | REGRESSION (veto) | improvement`).
3. **Every result row has a Statsig console link.**
4. **Recommendation is mechanical** — anchored to `pulse-evaluation.md` rubric, not opinion.
5. **For `audit-log` during incident triage**, the report includes a "Most likely incident-relevant" section if a symptom timestamp is in scope.
