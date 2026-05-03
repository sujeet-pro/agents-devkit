# `code-perf` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/code-perf.md`.

## Phase 0 — pre-execution

- [ ] `.temp/task-<slug>/` exists; `.temp/` is gitignored.
- [ ] User's prompt captured in `prompt.txt`.
- [ ] Repo resolved.
- [ ] Service tag resolved (or surfaced as "no alias in datadog.md").
- [ ] Metric identified (latency p50/p95/p99 / throughput / memory / build / etc.).
- [ ] (If `--budget`) budget value parsed.
- [ ] Slug derived.

## Phase 1 — preflight

- [ ] `git status` clean.
- [ ] Branch captured. Protected → branch-creation prompt.
- [ ] Validation commands resolved.
- [ ] Tests pass on HEAD (correctness baseline).
- [ ] (If using DD) `bin/adk-mcp-health` shows DD reachable; required env vars present.

## Phase 2 — MEASURE (baseline)

- [ ] `measurement-baseline.md` exists.
- [ ] Tool / protocol documented.
- [ ] Window documented (for prod metrics).
- [ ] Headline numbers recorded.
- [ ] Source links / IDs recorded (DD trace ID, profile path, Lighthouse run ID).
- [ ] Sample data quoted ≤15 words per quote.

## Phase 3 — IDENTIFY

- [ ] `bottleneck.md` exists with: Hypothesis, Evidence (quoted), Confidence, Proposed fix, Why this fix matches, Alternatives.
- [ ] Hypothesis is one sentence, falsifiable, names a specific cause.
- [ ] At least 1 quoted (≤15 word) trace / profile / metric output.
- [ ] Confidence stated (low / medium / high).
- [ ] If confidence = low: STOP and surface; even under `--auto`.
- [ ] Approval gate fired (unless `--auto`).

## Phase 4 — FIX

- [ ] Implementer subagent ran with `bottleneck.md`.
- [ ] Each edited file re-read after the agent claimed done.
- [ ] No file outside the planned set was touched (or scope creep was re-confirmed).
- [ ] Tests pass after the fix (correctness preserved).

## Phase 5 — VERIFY

- [ ] `measurement-after.md` exists.
- [ ] Same protocol as `measurement-baseline.md`.
- [ ] Headline numbers recorded with Δ.
- [ ] **Metric moved in the right direction** (p99 down, RSS down, build time down, etc.).
- [ ] If metric did NOT move: STOP. The diagnosis was wrong; loop back to Phase 3.
- [ ] If metric moved in the WRONG direction: STOP. Revert. Investigate.
- [ ] (If `--budget`) budget met. If not, the fix is incomplete; loop back to Phase 3.

## Phase 6 — GUARDRAIL

- [ ] At least ONE guardrail added or recommended:
    - Perf test in the test suite, OR
    - CI budget check (Lighthouse-CI / bundle-size / build-time gate), OR
    - Datadog monitor recommendation (the skill does NOT create monitors directly; recommends in the report).
- [ ] Guardrail's threshold = 1.5x to 2x the new measurement (catches a return-to-baseline regression but not flake).
- [ ] Guardrail documented in `report.md`.

## Phase 7 — pre-handoff

- [ ] `report.md` covers: Result, Before/After table, Bottleneck (with quote), Fix, Guardrail, Validation evidence, Decisions, Residual risk, NOT done, Next steps.
- [ ] Every artifact referenced in `report.md` exists.
- [ ] Decisions table includes every auto-pick.
- [ ] No remote write.
- [ ] Final status banner printed.
- [ ] Offer-depth question asked.

## Hard checks (the skill cannot pass without these)

1. `measurement-baseline.md` exists.
2. `bottleneck.md` exists with quoted evidence.
3. `measurement-after.md` exists with same-protocol re-measurement.
4. The metric moved in the right direction (signed delta).
5. (If `--budget`) the budget was met.
6. A guardrail was added or recommended.
7. Tests still pass (correctness preserved).
8. `report.md` includes the before/after table.

If any hard check fails:

- The skill is BLOCKED.
- The status banner shows `verified=no` or `guardrail=pending`.

## On any check failure

1. Log the failure under `## Validator failures`.
2. Block the next phase.
3. Diagnosis-was-wrong (metric didn't move) → loop back to Phase 3 once. After 2 wrong diagnoses, STOP regardless of mode.
4. Measurement is unstable / noisy (variance ≥ ±20% between runs) → STOP and surface; the measurement is not signal.
5. The bottleneck is in a third-party library → STOP and surface; the right fix may be `code-migrate` (upgrade) or a documented workaround, not "patch the third-party here".
