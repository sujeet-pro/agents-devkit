# `investigate-incident` — output format

## Per-turn status banner

```
[adk-investigate:investigate-incident] task=<slug> service=<svc> window=<window> phase=<0..9> mode=<auto|interactive>
```

## Final report

Written to `.temp/task-<slug>/investigation/incident.md`. Sections in this exact order:

```markdown
# Incident: <symptom> (<window>)

## Symptom + window
- Symptom: <one sentence verbatim from the prompt>
- Window: <ISO start>..<ISO end>
- Affected service: <service tag> (repos: <comma-separated>)
- Symptom timestamp: <ISO> (provided | parsed from prompt | "now")

## Sources
| Source | Status | Path |
| --- | --- | --- |
| Datadog logs | pulled | investigation/incident/raw/dd-logs.json |
| Datadog metrics | pulled | investigation/incident/raw/dd-metrics.json |
| Datadog traces | pulled | investigation/incident/raw/dd-traces.json |
| Datadog monitors | pulled | investigation/incident/raw/dd-monitors.json |
| Deploy timeline (acme/checkout-api) | pulled | investigation/deploy/deploy-acme__checkout-api.md |
| Deploy timeline (acme/order-service) | pulled | investigation/deploy/deploy-acme__order-service.md |
| Slack #incident (chatter) | pulled | investigation/incident/raw/slack-chatter.json |
| Slack #datadog-alerts-bff (alerts) | pulled | investigation/incident/raw/slack-alerts.json |
| Slack | skipped: workspace connector unreachable | — |

## Datadog evidence
| Signal | Query | Finding | Baseline | DD UI |
| --- | --- | --- | --- | --- |
| logs | service:checkout-api status:error | 412/hr PaymentTimeout (88/hr NPE new) | 38/hr | [link] |
| metrics | error_rate | 4.1% | 0.4% (24h ago) | [link] |
| metrics | p99 | 880ms | 220ms (24h ago) | [link] |
| traces | top errored | OrderService.computePrice | n/a | [link] |
| monitors | firing | 4 monitors at 13:02 | 1 firing baseline | [link] |

## Deploy timeline
(table per repo, near-symptom flagged)

## Slack discussion summary (if scraped)
- 12 messages since 13:02; team aware.
- Leading thread: Carol started; Bob named deploy `a3f9c2e`. [Slack link]
- (≤15 words quoted per message)

## Statsig audit log (if relevant — typically only RCA pulls this)
| Time | Object | Action | Actor |
(rows, with Statsig links)

## Correlation analysis
<paragraph stating which 2+ signals agree on the leading direction>

## Root-cause hypothesis
<one paragraph>

**Evidence:**
- <Source 1>: <observed; link>
- <Source 2>: <observed; link>
- <Source 3 if applicable>: ...

**Confidence:** <low | medium | high> — <one-sentence rationale per confidence-language.md>

## Next actions (prioritized)
1. **<Action label>** (blast radius: <surgical|bounded|transformative>; reversible in <duration>)
   Command/link: <exact thing the operator runs>
   Cost: <duration>
2. ...

## Follow-up
- For the code fix: `/adk-code:code-bugfix "<root-cause sentence>" --repo <repo>`
- For full RCA: `/adk-investigate:investigate-rca "<symptom>" --window <window>`
```

## Rules

1. **Sources table is mandatory.** It makes gaps visible.
2. **Confidence is mandatory.** Every hypothesis has `low | medium | high` anchored to the rules in `confidence-language.md`.
3. **Multi-source protocol.** Hypothesis sentences cite at least 2 independent signals (or explicitly state "no leading hypothesis").
4. **Next actions prioritized.** Per `next-action-priorities.md`. Each has blast radius + reversibility + concrete command.
5. **Never auto-trigger** any next action. The report describes; the operator decides.
6. **Never name an individual.** Author / reviewer is metadata cited for context, not for blame.
7. **Slack quotes ≤15 words.** Summarize; link out.
