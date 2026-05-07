# `code-perf` — workflow detail

## Phase 0 — prompt expand

1. **Restate** in one sentence: "Hit p99 < 500ms on `<endpoint>`" or "Diagnose the perf regression on `<service>` since `<time>`".
2. **Resolve repo** via `cwd → .git → repos.md`.
3. **Resolve service tag** via `~/.config/adk/datadog.md` `service_aliases` (e.g. "checkout" → "checkout-api"). If no alias, ask under `-i`; under `--auto`, use the verbatim name + record in Decisions.
4. **Identify the metric** the user cares about: latency p50/p95/p99 / throughput / memory / build time / TTFB / etc.
5. **Pick task slug**: `perf-<endpoint>-<symptom>` or `perf-<service>-<budget>` (e.g. `perf-checkout-p99-spike`).
6. **Create** `.temp/task-<slug>/`. Write `prompt.txt`.
7. **Approval gate** unless `--auto`.

## Phase 1 — preflight

1. `git status` clean. Dirty → ask.
2. Branch — protected → prompt `perf/<slug>`.
3. Resolve test / typecheck / lint commands. Tests must pass on HEAD (perf fixes shouldn't introduce correctness regressions).
4. If the work needs Datadog: `bin/adk-mcp-health` for DD reachability. `DATADOG_API_KEY` + `DATADOG_APP_KEY` present (legacy `DD_API_KEY` / `DD_APP_KEY` also accepted).

## Phase 2 — MEASURE (capture baseline)

The measurement protocol depends on what's slow. See `references/measurement-protocol.md` for per-tool recipes.

### For HTTP endpoints

- DD APM trace: pull p50/p95/p99 over a representative window (last 1h for hot regression; last 7d for budget work).
- Service: `<resolved tag>`.
- Env: `prod` (default per `datadog.md`) or `staging` if explicitly noted.
- Save the trace URL + the metric values + (optionally) a flame graph from one slow trace.

### For function-level perf

- Run the existing benchmarks (if any) on HEAD; capture the numbers.
- If no benchmarks, use a one-off harness (`hyperfine`, `wrk`, `ab`, `tinybench`, etc. — match the repo's style).

### For memory

- Capture RSS over a controlled load run.
- For Node/V8: heap snapshot before / after a workload.
- For JVM: heap dump + GC log.
- For Python: `tracemalloc` snapshot.

### For browser perf

- Lighthouse run (with the repo's existing config if any).
- Chrome DevTools perf trace + flame graph.
- Web Vitals (LCP, FID/INP, CLS, TTFB, FCP).

### For build / CI perf

- Time the build with `time` + repeated runs (3-5).
- Profile flags where available (`--profile` for esbuild / webpack, `gradle build --profile`).

### Save the baseline

Write `.temp/task-<slug>/measurement-baseline.md`:

- Tool / protocol used.
- Time window (for production metrics).
- The headline numbers.
- The relevant URL / file path / trace ID.
- A snippet of the relevant data (≤15 word quotes for any vendor-text).

**Approval gate** under `-i`. Under `--auto`, proceed.

## Phase 3 — IDENTIFY (bottleneck)

1. **Profile / trace / inspect** to find the bottleneck:
    - For DD traces, look at the slowest spans — look for: high-fanout DB queries (N+1), large response bodies, slow downstream calls, GC pauses.
    - For function profiles, look at the `self_time` columns; the highest-self-time function is usually the bottleneck.
    - For memory, look at retained sizes; long-lived references to short-lived data are leaks.
    - For browser, look at long tasks (>50ms), expensive layouts, large bundles.
    - For build, look at the longest-running step.
2. **Quote the evidence** (≤15 words per quote):
    - "DD trace shows 47 sequential `getUser` queries inside the request handler."
    - "Profile self-time: `validateInput` 380ms; total request 420ms."
    - "Heap snapshot: `cache` retains 240MB; oldest entry from 2 days ago."
    - "Lighthouse: LCP = 5.2s; main-thread blocked 3.1s by `bundle-vendor.js`."
3. **State confidence** (low / medium / high). Low → STOP and surface.
4. **Save** to `.temp/task-<slug>/bottleneck.md`:
    - Hypothesis: one sentence — what is causing the slowness.
    - Evidence: the quoted trace / profile / metric output.
    - Confidence: high / medium / low.
    - Proposed fix: one sentence — the smallest correct change.

**Approval gate** unless `--auto`.

## Phase 4 — FIX (smallest correct change)

1. Spawn the `implementer` subagent with `bottleneck.md` + the proposed fix.
2. The implementer applies the smallest correct change.
3. Run tests; confirm no regression (perf fixes shouldn't break correctness).
4. Capture the diff for the report.

## Phase 5 — VERIFY (re-measure)

1. **Re-run the same measurement protocol from Phase 2.**
    - For prod metrics: this means deploying the fix to staging or shadow-traffic — the production p99 will not move until the fix is live. The skill cannot deploy; it can only re-run a benchmark or a staging trace. Document the measurement context.
    - For local benchmarks: re-run the bench.
    - For browser: re-run Lighthouse / Chrome trace.
2. **Capture before/after** to `.temp/task-<slug>/measurement-after.md`:
    - Same protocol, same time window (or noted difference).
    - Headline numbers: before → after.
3. **If the fix didn't move the metric**, STOP. The diagnosis was wrong. Loop back to Phase 3.
4. **If the fix moved the metric in the wrong direction** (made it slower), STOP and revert.
5. **If the metric moved as expected**, continue.

## Phase 6 — GUARDRAIL

Add ONE of (depending on the perf type):

### Perf test (function / endpoint)

A test that asserts on duration with a generous threshold (e.g. 1.5x the new measurement). Lives in the test suite; runs in CI.

```ts
test("checkout completes in < 400ms (was 1.2s baseline)", async () => {
  const t0 = performance.now();
  await checkout(sampleCart);
  const dt = performance.now() - t0;
  expect(dt).toBeLessThan(400);
});
```

### CI budget check

For frontend: bundle size budget (`webpack-bundle-analyzer` + a CI check); Lighthouse-CI threshold.

```yaml
# .lighthouseci.json
{
  "ci": {
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.85 }]
      }
    }
  }
}
```

### Datadog monitor

For prod-monitored endpoints. Configure a monitor (manually via the DD UI or API; the skill does NOT create monitors directly — surfaces the recommendation in the report).

- Title: `<endpoint> p99 above 500ms`.
- Query: `avg(last_5m):p99:trace.<service>.request{env:prod} > 500`.
- Alert message: `<short>; runbook: <link>`.

The skill writes the recommendation in the report; the operator creates the monitor via DD UI.

## Phase 7 — REPORT

Write `.temp/task-<slug>/report.md`:

- **Result** — "Hit p99 < 500ms on `<endpoint>`" / "Reduced memory by 65%".
- **Before / After** — table.
- **Bottleneck** — one sentence quoting the evidence.
- **Fix** — table: file, +N/-M, role.
- **Guardrail** — what was added; where.
- **Validation evidence** — full suite + perf measurement.
- **Decisions** — every auto-pick.
- **Residual risk / follow-ups**.
- **Next steps** — typical: `/adk-review:review-code-changes` before push.

End with the offer-depth question.

## Loop control

- After 2 wrong diagnoses (fix applied, metric didn't move), STOP. Don't keep guessing — the diagnosis is wrong.
- If re-measurement is unstable / noisy (e.g. local bench varies ±20% between runs), STOP and surface — the measurement is not signal.
- If the bottleneck is in a third-party library (e.g. an ORM's slow query path), document; the fix may be "switch ORM" (a `code-migrate` task) or "work around" (a local optimization). Don't try to fix the third-party in this task.
