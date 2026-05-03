# `code-perf` — mode contract

`code-perf` supports `--auto` (default) and `-i` / `--interactive`. Plus `--budget <metric>=<value>`. Does **not** support `--fix` — mutation IS the goal.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks the documented `(default)` option at every decision.
- **Still measures BEFORE editing.** Auto does NOT skip the baseline.
- **Still re-measures AFTER editing.** Auto does NOT skip the verify step.
- **Still adds a guardrail.** Auto does NOT skip the guardrail.
- Refuses any irreversible destructive op.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
    - Phase 0 — confirm restated symptom + service tag + metric.
    - Phase 2 — review the baseline measurement (operator may know "that window includes a deploy; pick a different window").
    - Phase 3 — confirm the bottleneck identification (this is the most-valuable gate; the operator may know context the trace doesn't show).
    - Phase 5 — review the after-measurement (operator may want to see the trace before accepting the win).
    - Phase 7 — confirm the report.

## `--budget <metric>=<value>`

Optional. Composes with `--auto` / `-i`. Tells the skill the explicit budget to hit:

- `--budget p99=500ms` — endpoint p99 latency.
- `--budget p95=300ms` — same.
- `--budget rss=300MB` — resident memory.
- `--budget lcp=2500ms` — Largest Contentful Paint.
- `--budget bundle=200KB` — JS bundle size.
- `--budget build=120s` — build time.

The budget becomes the success criterion. Verify-step (Phase 5) checks the metric against the budget; if not met, the diagnosis was wrong (or the fix is incomplete).

## What `code-perf` will NEVER do, even under `--auto`

1. Skip the baseline measurement. Without it, "fix" is meaningless.
2. Skip the bottleneck identification. Without it, the fix is a guess.
3. Skip the re-measurement. Without it, "the fix worked" is a guess.
4. Skip the guardrail. The regression will silently come back.
5. Apply micro-optimizations on cold paths. (Premature optimization.)
6. Trade readability for a 1% win.
7. Push, commit, or open a PR.
8. Create Datadog monitors directly. Recommends; the operator creates via DD UI.
9. Quote vague metrics ("feels faster"). Always numerical.
10. Diagnose with low confidence. Surfaces and stops.

## What `--auto` MAY do without asking

- Pick the time window for prod metrics ("last 1h" for hot regression; "last 7d" for budget work).
- Pick which type of guardrail to add (perf test for functional perf, CI budget for bundle size, DD monitor recommendation for prod). Record in Decisions.
- Pick between two equivalent fixes that both move the metric — record in Decisions.

## Composition

- Called from `/adk-core:auto`, the chain is typically `auto → investigate-datadog (optional) → code-perf → review-code-changes`. `auto` propagates flags down.
- `/adk-investigate:investigate-datadog` may run first (for context / dashboard correlation); `code-perf` then has more starting context.
- Called directly with `--auto`, runs end-to-end.
- Called directly with `-i`, runs interactively.

## Invalid combinations

- `--auto -i` — refused at parse.
- `--fix` — silently ignored. `code-perf` always mutates.
