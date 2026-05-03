---
name: investigate-experiment
description: |
  Cross-check a Statsig experiment's pulse against Mixpanel reality and Datadog guardrails. Statsig says "primary metric is up 5%"; this skill validates by pulling the same metric from Mixpanel (project-level, not experiment splice) and checking Datadog guardrails (error rate, p99 latency) for the experiment's window vs control. All three sources must agree on direction + magnitude before recommending ship. Produces a `ship | iterate | kill` verdict with reasoning anchored to the three-source-verdict rubric. Use to decide ship / iterate / kill on any non-trivial experiment. Do NOT use for incident triage (use `/adk-investigate:investigate-incident`), single-tool experiment queries (use `/adk-investigate:investigate-statsig` alone), or experiment design / sample-size calculation (out of scope).
metadata:
  category: observability
  kind: task
  layer: 9
  modes: [auto, interactive]
  needs_mcp: [statsig, mixpanel-workspace, datadog]
  needs_meta_info: [info, repos, statsig, mixpanel, datadog]
argument-hint: "<experiment-name> [--window <duration>] [-i]"
---

# `investigate-experiment` — three-source verdict

Cross-check a Statsig experiment's pulse against Mixpanel + Datadog. Read-only.

## When to use

- "should we ship `<experiment>`?"
- "is the `<experiment>` test winning?"
- "iterate or kill on `<experiment>`?"
- Any pre-ship review of an experiment's results.

## When NOT to use

- Incident triage → `/adk-investigate:investigate-incident`.
- Single-source experiment query (just Statsig) → `/adk-investigate:investigate-statsig --use pulse`.
- Mixpanel-only product-analytics question → `/adk-investigate:investigate-mixpanel`.
- DD-only metric question → `/adk-investigate:investigate-datadog`.
- Experiment design / sample-size calculation — out of scope.
- After the verdict is `ship`, the actual gate flip → use the Statsig console
  or a future explicitly write-enabled Statsig workflow.

## Common prompts (auto-route triggers)

| Prompt pattern | Action |
| --- | --- |
| "should we ship `<exp>`?" | full three-source verdict |
| "is `<exp>` winning?" | full three-source verdict |
| "ship/iterate/kill on `<exp>`?" | full three-source verdict |
| "pulse for `<exp>` cross-check" | full three-source verdict |
| "guardrail check on `<exp>`" | guardrail-focused (still pulls all 3) |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<experiment-name>` | yes | — |
| `--window` | no | `since experiment_start` |
| `-i` / `--interactive` | no | mutually exclusive with `--auto` |

## Workflow

```
Phase 0 — prompt expand
  Resolve experiment from statsig.md.common_experiments (id, primary_metric, secondary_metrics, repo).
  Resolve service tag for the linked repo via repos.md (for DD guardrails).
  Resolve Mixpanel project from mixpanel.md.
  Window = since experiment_start (default) or --window flag.

Phase 1 — preflight
  All three MCPs reachable: statsig + mixpanel-workspace + datadog.
  Env vars present (STATSIG_CONSOLE_API_KEY, DD_API_KEY, DD_APP_KEY).
  bin/adk-info --check info repos statsig mixpanel datadog.

Phase 2 — three parallel reads (max 4 parallel; we use 3):
  Statsig: Get_Experiment_Results -> primary lift, secondary lifts, guardrails, sample, p-values.
  Mixpanel: same primary metric at the project level (not the experiment splice).
  Datadog: error_rate + p99 + throughput for the affected service over the same window vs prior-window baseline.

Phase 3 — reconcile
  Apply three-source-verdict rubric (see references/three-source-verdict.md):
    - Statsig says lift up + Mixpanel agrees direction + DD guardrails clear -> ship-eligible.
    - Statsig says lift up + Mixpanel doesn't see it -> tracking discrepancy; investigate before ship.
    - Statsig says lift up + DD guardrail regressed -> guardrail veto (ITERATE or KILL).
    - Statsig says no lift OR p too high -> kill or iterate per pulse-evaluation.md.

Phase 4 — verdict
  Recommendation = ship | iterate | kill, with reasoning + confidence.
  Apply guardrail-veto.md (any DD guardrail regression at p<0.1 vetoes ship).

Phase 5 — emit experiment.md
  .temp/task-<slug>/investigation/experiment.md
```

See `references/workflow.md` for the per-phase detail.

## Persona

> You are a Principal Engineer reviewing an experiment for ship/iterate/kill. You require all three sources (Statsig + Mixpanel + DD) to agree on direction and magnitude. A Statsig win + Mixpanel disagreement means tracking is broken or the metric definitions diverged. A Statsig win + DD guardrail regression is not a ship — performance regressions are user-experience regressions even if conversion ticked up. You never recommend ship on a guardrail miss.

See `references/persona.md`.

## Constitution

**Must do:**

1. Pull all three sources before recommending. Never partial.
2. Apply the `three-source-verdict.md` rubric mechanically. The recommendation is `ship | iterate | kill`, with reasoning anchored to the inputs.
3. State sample size + significance + days-in-experiment for the Statsig pulse claim.
4. Check guardrails (DD `error_rate`, `p99_latency_ms`, plus any in `statsig.md.exposure_metric_conventions.guardrail_metrics`).
5. State confidence on the verdict.

**Must not do:**

1. Recommend ship if any guardrail moved the wrong direction at `p<0.1`. Veto active.
2. Treat Statsig and Mixpanel as the same metric automatically. Verify the metric definitions; if they diverged, surface the discrepancy.
3. Ship a gate from this skill. Out of scope.
4. Single-source verdict.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- "Statsig says ship; let's ship" — without DD guardrail check, you can miss a perf regression.
- Treating Mixpanel and Statsig as the same metric automatically (definitions can drift).
- Ignoring sample size on the Statsig side.

## Output

`.temp/task-<slug>/investigation/experiment.md` with sections: `Experiment`, `Statsig pulse`, `Mixpanel cross-check`, `Datadog guardrails`, `Reconciliation`, `Verdict (ship/iterate/kill)`, `Confidence`, `Reasoning`. See `references/output-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | The three-source-verdict persona |
| `references/workflow.md` | Detailed Phase 0–5 stages |
| `references/modes.md` | Mode contract (`--auto` / `-i`; no `--fix`) |
| `references/interaction-contract.md` | Canonical interaction contract |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | 3 worked examples (clear ship / iterate / kill) |
| `references/output-format.md` | Canonical experiment.md shape |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase gates |
| `references/how-it-works.md` | Mermaid: phase flow + verdict matrix |
| `references/clarifying-questions.md` | Questions under `-i`; defaults under `--auto` |
| `references/three-source-verdict.md` | The `ship | iterate | kill` rubric |
| `references/guardrail-veto.md` | When a DD guardrail vetoes ship |

## Additional links

- The experiment owner's recent commits (from `statsig.md.common_experiments[].repo`).
- The Statsig docs for any metric definition.
- The Mixpanel Lexicon for the project (`Get-Lexicon-URL`).
