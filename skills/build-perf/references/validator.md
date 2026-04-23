# `build-perf` — four-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/build-perf.md`.

## Phase 1 — pre-execution

- [ ] Surface, metric, and a NUMERIC target are explicit. ("Make it faster" → REJECT.)
- [ ] `.temp/task-<slug>/perf/{baseline,after}/` exist (or will be created).
- [ ] The chosen measurement tool is appropriate for the metric (see `references/measurement-tools.md`).
- [ ] If `env != prod`, the limitation is documented and the user accepted the lower-fidelity baseline.

## Phase 2 — mid-flow

- [ ] Baseline measurement was captured AS A FILE under `.temp/task-<slug>/perf/baseline/` (Lighthouse JSON, flamegraph, query plan, etc.).
- [ ] The bottleneck is named in `.temp/notes/perf-<slug>-bottleneck.md` with a CITATION into the baseline artifact.
- [ ] Only ONE bottleneck is being fixed in this pass.
- [ ] No drive-by refactors mixed in.

## Phase 3 — pre-handoff

- [ ] Re-measurement was done with the SAME tool, the SAME way, ≥3 runs (median/p50/p95 reported, not single-run).
- [ ] Delta is reported as a number (`baseline X → after Y`), not as a vibe.
- [ ] Win exceeds noise (typically ≥10% on noisy frontend metrics, ≥5% on stable backend metrics; document the noise floor if not).
- [ ] A guardrail was added (perf test / CI budget / monitor) OR the absence is explicitly accepted in the report.
- [ ] Repo-native typecheck + lint + tests still green.

## Phase 4 — post-execution

- [ ] Final report exists with delta + bottleneck + fix + guardrail + residual risk.
- [ ] Baseline + after artifacts archived under `.temp/task-<slug>/perf/`.
- [ ] User acknowledged (or `--auto`).
