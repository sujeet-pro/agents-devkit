# input classifier: Statsig URL

## Patterns

```
https?://console.statsig.com/<project-key>/(gates|experiments|metrics)/<id>
https?://console.statsig.com/<project-key>/audit-log
```

## Fetch via

`adk-mcp-statsig`:
- gate URL → `Get_Gate_Details_by_ID`
- experiment URL → `Get_Experiment_Details_by_ID` + `Get_Experiment_Overall_Results`
- metric URL → `Get_Metric_Definition_by_ID`
- audit-log URL → `Get_Audit_Logs` with the URL's filter

## Extract into context.md

### gate
```markdown
### [statsig-gate] <id> — <name>
url: <full URL>
status: enabled | disabled
rollout: <percent or rules summary>
last edited: <ts> by <user>
rules (top 3): <quote>
```

### experiment
```markdown
### [statsig-experiment] <id> — <name>
url: <full URL>
status: setup | running | terminated
primary metric: <name>
secondary metrics: [...]
allocation: <%>
started: <ts>
sample size: <N>
primary lift: <%> (p=<value>)
guardrails: <list with directions>
```

### audit log
```markdown
### [statsig-audit] <window>
url: <full URL>
entries: <N>
relevant edits (filtered to query window or top 10):
  - <ts> — <actor> — <gate/experiment/config> — <action>
```

## Hints

- `/adk-investigate` audit-log: gold for "what changed before prod broke" — anchor to symptom time ±2h.
- `/adk-investigate --use experiment`: cross-check pulse vs Mixpanel reality vs DD guardrails.
- Don't recommend a gate flip from a skill — that's a manual action.
