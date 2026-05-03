# `investigate-datadog` — output format

## Per-turn status banner (each turn opens with this)

```
[adk-investigate:investigate-datadog] task=<slug> use=<investigate|dashboard-summary|alert-triage> phase=<0|1|2|3|4> mode=<auto|interactive>
```

## Final report

Written to `.temp/task-<slug>/investigation/datadog.md`. Sections in this exact order:

```markdown
# Datadog: <one-line restatement> (<env>)

## Query
<the literal query string(s) that ran, one per line>

## Resolved entities
| Kind | Surface | Resolved | Source |
| --- | --- | --- | --- |
| service | "checkout" | checkout-api | datadog.md.service_aliases (verified) |
| window | "last 1h" | now-1h..now | NL parse |
| env | (omitted) | prod | datadog.md.default_env (verified) |

## Results

### --use investigate
| Group | Count / Value | Baseline | Delta | DD UI |
| --- | --- | --- | --- | --- |

### --use dashboard-summary
| Tile | Now | Baseline | Status | DD UI |
| --- | --- | --- | --- | --- |

### --use alert-triage
| Monitor | State | Triggered | Severity | Likely cause |
| --- | --- | --- | --- | --- |

## Trends
- <bullet per significant trend with a number, baseline, and link>

## Anomalies
- <bullet per outlier; flag with ANOMALY tag if >2σ from baseline or new>

## DD UI links
- [<short label>](https://app.datadoghq.com/...?query=...&from_ts=...&to_ts=...)

## Follow-up queries
- `/adk-investigate:<skill> "<concrete next query>"` — <one-sentence reason>
```

## Rules

1. **Every numeric result has a baseline column.** If no baseline can be computed, write `n/a — first window`.
2. **Every result row has a DD UI link.** No exceptions.
3. **No raw log lines.** Aggregate first; show top 5 with counts; link to raw.
4. **No editorializing.** "ANOMALY" is allowed as a flag; "this is bad" is not.
5. **Confidence statement.** If the report names a likely cause, end the section with `Confidence: <low|medium|high> — <one-sentence rationale>`.
6. **Follow-up queries** propose 1–3 concrete next steps. Each is a fully formed `/adk-investigate:<skill> "<query>"` invocation, not a vague suggestion.

## Example header

```markdown
# Datadog: errors in checkout last 1h (prod)

Run at 2026-05-03T14:00Z by `/adk-investigate:investigate-datadog --use investigate --time "last 1h" --env prod`.
```
