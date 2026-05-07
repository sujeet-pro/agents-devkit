# `investigate-experiment` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/investigate-experiment.md`.

## Phase 0 — pre-execution

- [ ] Experiment name resolved to id (`verified` from `statsig.md.common_experiments`).
- [ ] Linked repo + linked service resolved.
- [ ] Mixpanel project id resolved.
- [ ] Window resolved (default `since experiment_start`).
- [ ] Guardrail list resolved from `statsig.md.exposure_metric_conventions.guardrail_metrics` (or default).

## Phase 1 — preflight

- [ ] `bin/adk-mcp-health` confirms `statsig: connected`, `mixpanel-workspace: connected`, `datadog: connected`. **All three required.**
- [ ] `STATSIG_CONSOLE_API_KEY` env var present.
- [ ] `DATADOG_API_KEY` and `DATADOG_APP_KEY` env vars present (legacy `DD_API_KEY` / `DD_APP_KEY` also accepted).
- [ ] `bin/adk-info --check info repos statsig mixpanel datadog` returns 0.

## Phase 2 — three reads

- [ ] Statsig `Get_Experiment_Results` called; raw saved.
- [ ] Mixpanel `Get-Events` (or `Run-Query`) called for the project-level primary metric; raw saved.
- [ ] DD `get_metrics` called for each guardrail; raw saved.
- [ ] Each read has a time window AND env tag where applicable.
- [ ] If any source fails after retry, gap is recorded; verdict confidence will be capped at `medium` (or `low` if 2+ sources failed).

## Phase 3 — reconcile

- [ ] Reconciliation table built with one row per metric.
- [ ] Metric-definition divergence flagged if Mixpanel and Statsig directions agree but magnitudes diverge by >50% (relative).
- [ ] Each guardrail row has a `Verdict` column with one of `within tolerance`, `REGRESSION`, `improvement`.

## Phase 4 — verdict

- [ ] Verdict is one of `ship`, `iterate`, `kill`.
- [ ] If verdict = `ship`, NO guardrail row has `REGRESSION` AND no Mixpanel disagreement on primary direction.
- [ ] Sample size + days-in-experiment stated.
- [ ] Confidence stated (`low | medium | high`) with anchored bullets.

## Phase 5 — pre-handoff

- [ ] `.temp/task-<slug>/investigation/experiment.md` exists.
- [ ] Sections in correct order per `output-format.md`.
- [ ] Statsig console link, Mixpanel UI link, DD UI links present.
- [ ] If verdict = `iterate` due to disagreement, `Recommended probes` section non-empty.
- [ ] Final status banner printed.

## On any check failure

- Log to `validation/investigate-experiment.md` with the failing check + remediation.
- For "ship recommended despite guardrail regression": HARD BLOCK. Re-derive verdict per the rubric.
- For "single-source verdict": HARD BLOCK. Pull missing sources or downgrade confidence.
- Same check failing 3 times → surface, do not loop.
