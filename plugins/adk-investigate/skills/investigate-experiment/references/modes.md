# `investigate-experiment` — mode contract

`investigate-experiment` is **read-only**. It supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix`.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks documented defaults at every decision:
  - Window: `since experiment_start`.
  - Guardrails: from `statsig.md.exposure_metric_conventions.guardrail_metrics`; defaults `[error_rate, p99_latency_ms]`.
  - Three sources pulled in parallel.
- Still validates after every phase.
- Still surfaces a final verdict.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
  - Phase 0: shows resolved experiment + window + guardrails, asks "proceed?".
  - Phase 2: shows the three parallel calls, asks "run them?".
  - Phase 3: shows the reconciliation table, asks "publish verdict?".

## `--fix` is not supported

- This skill is read-only. The action it would imply (ship / iterate / kill) is operator-executed in the Statsig console; this skill does not toggle gates.
- If the operator passes `--fix`, the skill rejects with:
  "investigate-experiment is read-only; for the actual gate flip, use the
  Statsig console or a future explicitly write-enabled Statsig workflow."

## What `--auto` will NEVER do

1. Toggle a gate (Statsig).
2. Start / pause / end an experiment.
3. Recommend `ship` if any guardrail moved wrong direction at `p<0.1`.
4. Recommend `ship` if Mixpanel disagrees with Statsig on primary direction.
5. Recommend `ship` from a 2-day pulse with `n < power-target`.
6. Single-source verdict.
