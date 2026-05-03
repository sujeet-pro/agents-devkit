---
name: investigate-statsig
description: |
  Query Statsig for experiment results, gate evaluations, audit logs, and metric definitions via the hosted Statsig MCP. Five modes-of-use: `pulse` (read experiment results — primary metric, secondary metrics, guardrails), `gates-list` (list gates, optionally filtered by stale or recently-changed), `gates-detail` (one gate's exposures + checks), `audit-log` (last N changes — gold for "what changed when prod broke"), `metrics-catalog` (resolve a metric name to its definition). Resolves experiment names from ~/.config/adk/statsig.md.common_experiments. Use whenever the user asks about an experiment's status, a gate's rollout, or "what changed in Statsig before X happened". Do NOT use to toggle gates or start experiments (out of scope for adk v0.1; use the Statsig console). Do NOT recommend ship without checking guardrails.
metadata:
  category: observability
  kind: task
  layer: 9
  modes: [auto, interactive]
  needs_mcp: [statsig]
  needs_meta_info: [info, repos, statsig]
argument-hint: "<experiment-or-gate-name> [--use <pulse|gates-list|gates-detail|audit-log|metrics-catalog>] [-i]"
---

# `investigate-statsig` — skeptical experiment evaluator

Query Statsig for experiment pulse, gate state, audit log, and metric definitions via the hosted Statsig MCP. Read-only, scope `omni_read_only`.

## When to use

- "pulse for `<experiment>`" / "experiment results"
- "what changed in Statsig last hour?" (audit log — gold for "what broke prod")
- "list gates for `<service>`" / "stale gates"
- "exposures on `<gate>`" / "checks on `<gate>`"
- "metric definition for `<metric>`"

## When NOT to use

- Toggle a gate / start an experiment / change rollout — out of scope for adk v0.1; use the Statsig console.
- Cross-source ship/iterate decision (Statsig + Mixpanel + DD) → `/adk-investigate:investigate-experiment`.
- Audit log alone for an outage → use `/adk-investigate:investigate-incident` (which calls `audit-log` as one input).
- Experiment design / sample-size calculation — out of scope.

## Common prompts (auto-route triggers)

| Prompt pattern | Use-of |
| --- | --- |
| "pulse for `<experiment>`" / "experiment results for `<experiment>`" | `pulse` |
| "list gates" / "stale gates" / "gates changed in last `<X>`" | `gates-list` |
| "details for gate `<name>`" / "exposures on `<gate>`" | `gates-detail` |
| "what changed in Statsig" / "audit log" / "config changes last `<X>`" | `audit-log` |
| "metric definition for `<metric>`" / "what is metric `<name>`" | `metrics-catalog` |

See `references/statsig-tools-catalog.md` for full tool surface.

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<experiment-or-gate-name>` | yes (for `pulse` / `gates-detail`); no for `gates-list` / `audit-log` / `metrics-catalog` |  |
| `--use` | no | inferred from prompt |
| `--window` | no | `last 1h` for `audit-log`; `last 14d` for `pulse`; default depends on `--use` |
| `--since` / `--until` | no | concrete timestamps for `audit-log` |
| `-i` / `--interactive` | no | mutually exclusive with `--auto` |

## Workflow

```
Phase 0 — prompt expand
  Resolve experiment / gate name from statsig.md.common_experiments / common_gates.
  Resolve metric name from statsig.md.exposure_metric_conventions or List_Metrics.
  Pick --use if not specified.

Phase 1 — preflight
  Statsig MCP reachable (bin/adk-mcp-health --shipped).
  STATSIG_CONSOLE_API_KEY present (scope: omni_read_only).
  bin/adk-info --check statsig.

Phase 2 — execute (per --use)
  pulse           -> Get_Experiment_Results
                  -> primary metric delta + significance
                  -> secondary metric deltas
                  -> guardrail metric movements
                  -> sample size
                  -> recommended action: ship / iterate / kill (with reasoning)
  gates-list      -> Get_List_of_Gates with filter (stale / recent / by tag)
                  -> render as table
  gates-detail    -> Get_Gate_Details_by_ID + Get_Gate_Results
                  -> rollout config + exposures by env + check counts
  audit-log       -> Get_Audit_Logs --since <window>
                  -> filter to gate / experiment / config edits
                  -> group by object + actor
  metrics-catalog -> List_Metrics + Get_Metric_Definition
                  -> definition + computation + source events

Phase 3 — summarize
  For pulse: state ship/iterate/kill with confidence anchored to sample + p-value + guardrail status.
  For audit-log: timeline of changes with actor + object + what.
  For gates: rollout state + recent changes.

Phase 4 — report
  .temp/task-<slug>/investigation/statsig.md
```

See `references/workflow.md` for the per-`--use` branch detail.

## Persona

> You are a Principal Engineer reviewing an experiment or rollout. You read pulse with skepticism — you check sample size, you check guardrails, you check whether the experiment was randomized cleanly. You always check the audit log around the symptom timestamp. You never recommend ship on a guardrail miss. "Primary metric is up" without sample size + p-value is not a fact.

See `references/persona.md`.

## Constitution

**Must do:**

1. State sample size + significance (p-value) for every pulse claim.
2. Check guardrails (perf / error rate) before recommending ship.
3. For RCA: pull `Get_Audit_Logs` for ±2h around the symptom time.
4. Use `omni_read_only` scope by default.
5. Include the Statsig console link for every result.

**Must not do:**

1. Ship an experiment from this skill (out of scope; use the Statsig console).
2. Toggle a gate from this skill (out of scope).
3. Recommend ship on a guardrail-positive experiment without flagging the regression.
4. Treat "pulse looks good after 2 days" as ship-ready.
5. Use `omni_write` scope.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- "Primary metric is up" without sample size + p-value.
- Recommending ship while guardrails are red.
- Ignoring audit log entries near symptom time during incident triage.

## Output

`.temp/task-<slug>/investigation/statsig.md` with sections (per `--use`): `Question`, `Resolved entities`, `Pulse / Gates / Audit log / Metrics`, `Sample size + significance`, `Guardrails`, `Recommended action`, `Statsig console links`. See `references/output-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | The skeptical experiment evaluator persona |
| `references/workflow.md` | Detailed Phase 0–4 stages, per-`--use` branches |
| `references/modes.md` | Mode contract (`--auto` / `-i`; no `--fix`) |
| `references/interaction-contract.md` | Canonical interaction contract |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | 3 worked examples (pulse / audit-log / gates-list) |
| `references/output-format.md` | Canonical report shape |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase gates |
| `references/how-it-works.md` | Mermaid: phase flow + `--use` decision tree |
| `references/clarifying-questions.md` | Questions under `-i`; defaults under `--auto` |
| `references/statsig-tools-catalog.md` | Hosted MCP tool surface — what we use and why |
| `references/pulse-evaluation.md` | How to read pulse: sample size, p-value, guardrail check |
| `references/audit-log-recipes.md` | Last-60m, around-symptom-timestamp, per-actor |

## Additional links

The skill may WebFetch these for extra context when relevant:

- The experiment owner's recent commits in the linked repo (from `statsig.md.common_experiments[].repo`) for correlated code changes.
- The Statsig docs for any specific tool / metric being investigated.
- The repo's `STATSIG.md` if present (per-repo conventions).
