# `investigate-experiment` — workflow detail

## Phase 0 — prompt expansion

1. **Restate** the question in one sentence. ("Should we ship checkout_funnel_v3?")
2. **Resolve experiment** from `~/.config/adk/statsig.md.common_experiments`:
   - Surface name → canonical id.
   - Pull `primary_metric`, `secondary_metrics`, `repo` from the meta-info entry.
3. **Resolve linked service** for the linked repo via `~/.config/adk/repos.md.repos[<repo>].datadog_service` (for DD guardrails).
4. **Resolve Mixpanel project** from `~/.config/adk/mixpanel.md.project_id` (used for the cross-check).
5. **Resolve window:**
   - `--window` flag wins.
   - Else `since experiment_start` (lifetime; the typical case for a ship/iterate/kill decision).
6. **Resolve guardrails:** read `~/.config/adk/statsig.md.exposure_metric_conventions.guardrail_metrics`. Default: `[error_rate, p99_latency_ms]`.

Output: `entities.md` table.

## Phase 1 — preflight

1. `bin/adk-mcp-health` confirms all three: `statsig: connected`, `mixpanel-workspace: connected`, `datadog: connected`. If any is unreachable, stop with the missing-thing list.
2. Env vars present: `STATSIG_CONSOLE_API_KEY`, `DATADOG_API_KEY`, `DATADOG_APP_KEY` (legacy `DD_API_KEY` / `DD_APP_KEY` are also accepted). (Mixpanel via workspace MCP; no env var.)
3. `bin/adk-info --check info repos statsig mixpanel datadog` returns 0.
4. (Cheap warmup) parallel: `Get_List_of_Gates --limit 1` (Statsig) + `list_dashboards` first 1 (DD) + `Get-Property-Names` (Mixpanel) to mask cold-start.

## Phase 2 — three parallel reads

Spawn three calls in parallel (max 4 parallel per dispatcher rule; we use 3):

### Statsig

```text
Get_Experiment_Results --experiment-id <id>
```

Extract:
- Primary lift + p + n per arm.
- Secondary lifts + p (each).
- Guardrail lifts + p (each).
- Days in experiment.

### Mixpanel

For the SAME primary metric (resolved by name), pull the project-level value over the experiment window:

```text
Get-Events --window <experiment_start>..<now> --event <primary_metric>
```

Compute the lift vs the *prior equal-duration window* (same window, shifted back by its own duration).

This is the "is the metric moving at the project level too?" check. The Statsig splice may be on a higher-converting segment or the metric definitions may have diverged.

### Datadog

For the linked service over the experiment window:

```text
get_metrics: error_rate
get_metrics: p99 latency
get_metrics: throughput (sanity check; not a guardrail by default)
```

Compare each to the prior-equal-window baseline. Compute delta + significance (heuristic: >2σ from baseline counts as "moved").

Save raw to `.temp/task-<slug>/investigation/experiment/raw/`.

## Phase 3 — reconcile

Build the comparison table:

| Metric | Statsig (treatment vs control) | Mixpanel (project level vs baseline) | DD (service level) | Verdict |
| --- | --- | --- | --- | --- |
| primary | +X% (p=<p>) | +Y% | n/a | agree / disagree / Mixpanel can't see it |
| guardrail.error_rate | n/a | n/a | +Z% (p=<p>) | within tolerance / REGRESSION |
| guardrail.p99_latency | n/a | n/a | +W ms (p=<p>) | within tolerance / REGRESSION |

Apply the rubric:

1. **Statsig says lift up + Mixpanel agrees direction + all DD guardrails clear.** Verdict-eligible: `ship`.
2. **Statsig says lift up + Mixpanel doesn't see it (delta < 50% of Statsig delta).** Verdict: `iterate` — investigate metric-definition discrepancy or splice imbalance before shipping.
3. **Statsig says lift up + ANY DD guardrail regressed (wrong direction at p<0.1).** Verdict: `iterate` (or `kill` if guardrail miss is severe). **Guardrail veto active.**
4. **Statsig says no significant lift (p>0.05).** Apply `pulse-evaluation.md` rubric on Statsig alone: `iterate` if underpowered, `kill` if powered.
5. **Statsig says negative effect.** Verdict: `kill`.

## Phase 4 — verdict

Render:

```markdown
## Verdict: <ship | iterate | kill>

**Reason:** <one paragraph anchored to rubric inputs>

**Confidence:** <low | medium | high>
- low: any source unreachable; metric-definition discrepancy; guardrail near veto threshold
- medium: all sources agree direction but magnitudes diverge; clear veto-or-not
- high: all three sources agree direction + magnitude; sample size satisfies power; days-in-experiment ≥ 7
```

## Phase 5 — emit

Write `.temp/task-<slug>/investigation/experiment.md` per `output-format.md`. Return path.

## Loop control

- Cap parallel calls at 3 (one per source).
- After 1 retry on each source, surface failures and continue with what's available; if 2/3 sources fail, stop with "insufficient evidence" verdict.
- Do not re-pull the same source in one session — data hasn't moved.
