# `investigate-deploy` — output format

## Per-turn status banner

```
[adk-investigate:investigate-deploy] task=<slug> repo=<owner/repo> workflow=<name> window=<duration> phase=<0|1|2|3|4> mode=<auto|interactive>
```

## Final report

Written to `.temp/task-<slug>/investigation/deploy.md`. Sections in this exact order:

```markdown
# Deploy timeline: <owner/repo> (<window>[, symptom at <time>])

## Summary
- <N> deploys in window
- <K> failed
- <M> near-symptom candidates (if --symptom-time set)

## Timeline (newest first)
| Time (UTC) | Status | Duration | SHA | Author | Title | [Δ-symptom (if applicable)] | URL |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Failed deploys (if any)
| Time | Status | SHA | Author | Title | Likely cause | URL |

## Near-symptom candidates (if --symptom-time set, sorted by abs(Δ))
| Time | SHA | Author | Title | Δ |

For each candidate, this skill states: **"This is a candidate, not a confirmed cause."** And points the operator at:
- `/adk-investigate:investigate-datadog "<query>"` — find log/metric signal matching the new code path.
- `gh pr view <pr>` — inspect what changed.
- `/adk-investigate:investigate-incident "<symptom>" --service <svc>` — multi-source triage.

## Cross-source: Datadog deploy events (if DD MCP reachable)
| Time (UTC) | DD event | Matched gh run |

(state coherence: "all gh runs matched DD events" or "1 gh run had no DD event — possibly the deploy was triggered outside the standard pipeline")

## Follow-up
- (concrete next steps)
```

## Rules

1. **Every row in the timeline has** `Time | Status | Duration | SHA | Author | Title | URL`. No exceptions.
2. **Failed deploys are duplicated into a `Failed deploys` section** for visibility — they may be the story.
3. **Near-symptom candidates are a separate section** if `--symptom-time` set, sorted by `abs(time-delta)`.
4. **Never claim "deploy caused"** — the skill marks candidates; conclusions belong to `/adk-investigate:investigate-incident`.
5. **Cross-source is opt-in** — only run if DD MCP is reachable; skip silently otherwise.
6. **Time format is ISO UTC** in the underlying data; the table column header reads `Time (UTC)`.
7. **Δ-symptom column** only appears when `--symptom-time` is set. Format: `<sign><N>m` or `<sign><N>h <N>m`.
