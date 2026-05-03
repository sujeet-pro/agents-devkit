# `investigate-statsig` — mode contract

`investigate-statsig` is **read-only**. It supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` — there is nothing to fix; investigation produces evidence, not changes.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks documented defaults at every decision:
  - `--use` inferred from the prompt.
  - `--window` for `audit-log`: `last 60m`. For `pulse`: `since experiment_start` (lifetime).
  - For `pulse`: applies `pulse-evaluation.md` rubric and produces `ship | iterate | kill` recommendation with reasoning.
- Still validates after every phase.
- Still surfaces a final report with Statsig console links.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
  - Phase 0: shows resolved experiment / gate / metric + window, asks "proceed?".
  - Phase 2: shows the constructed call, asks "run it?".
  - Phase 3: shows the recommended action, asks "publish to report?".

## `--fix` is not supported

- This skill is read-only. The Statsig API key in adk's default config has `omni_read_only`.
- If the operator passes `--fix`, the skill rejects with: "investigate-statsig is read-only; use the Statsig console to toggle gates / start experiments".

## What `--auto` will NEVER do

1. Toggle a gate (would require `omni_write`; not in scope).
2. Start, pause, or end an experiment.
3. Modify a gate's targeting rule.
4. Edit a metric definition.
5. Recommend `ship` on a guardrail-failing experiment without flagging the regression as a veto.
6. Use `omni_write` scope.
