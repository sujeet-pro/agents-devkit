# `code-perf` — anti-patterns

## Optimizing without measuring

- **"I refactored this nested loop; it should be faster."** Without measurement, that's a guess. The compiler / JIT may have already optimized it; the new shape may even be slower.
- **"This O(n²) algorithm is bad; let me make it O(n log n)."** O(n log n) only beats O(n²) for large n. For n=8, the linear search may be faster. Measure.
- **"This SQL query is bad; let me rewrite it."** Without an `EXPLAIN ANALYZE`, the rewrite may be slower (e.g. lose an index hit).
- The rule: every optimization claim is either backed by a measurement or it's a guess. Guesses are out of scope for `code-perf`.

## Premature optimization on cold paths

- **Adding a cache to a function called once per request startup** (cold path; runs once per minute). The cache adds complexity without helping.
- **Memoizing a function called twice in the request lifetime** when the call cost is sub-millisecond. The memoization overhead may exceed the savings.
- **Optimizing the import order to "improve startup time"** by 0.1ms. Not worth the code-readability cost.
- The rule: optimize the hot path; cold paths get no special treatment.

## Trading readability for tiny wins

- **Replacing `arr.map(f).filter(g)` with a single hand-rolled loop** for a 2% improvement. Readability cost > performance benefit.
- **Inlining a function manually** so the JIT doesn't have to. The JIT does this; trust it.
- **Using bitfield tricks** (`x | 0` for `Math.floor(x)`) to save 5ns. Saves nothing in practice; obscures intent.
- The rule: the readability cost must be << the perf benefit. A 1% win is not worth 50% more code complexity.

## Skipping the guardrail

- **Fixing the perf bug, shipping, then declaring victory.** The bug returns in 6 weeks because no test / monitor catches it.
- **Adding a perf test with a too-tight threshold.** Will flake; will be disabled; provides no signal.
- **Adding a perf test with a too-loose threshold.** Won't catch a real regression.
- The rule: the guardrail's threshold is 1.5x to 2x the new measurement (so it catches a return-to-baseline regression but not flake).

## Vague metrics

- **"It feels faster."** Not a metric.
- **"It's fast enough now."** Compared to what?
- **"Tests pass quickly."** Tests passing tells you nothing about prod perf.
- **"The flame graph looks better."** Where? Show the specific span / function that improved.
- The rule: every claim is a number. Before / after.

## Diagnosing without quoting

- **"The bottleneck is the database."** Show the trace span and its duration.
- **"The query is slow."** Show the `EXPLAIN ANALYZE` output (or quote the relevant line).
- **"The N+1 is in the user list."** Show the trace with the 47 sequential calls.
- The rule: every bottleneck claim has a quoted (≤15-word) trace / profile / metric output.

## Wrong measurement scope

- **Measuring local development perf and assuming prod is the same.** Local has no concurrency, no production data volume, no real network latency. Different system.
- **Measuring p50 when the user complaint is about p99.** They're different distributions; fix the right one.
- **Measuring during a low-traffic window when the regression appears at peak.** Match the conditions.
- **Measuring TTFB when the user complaint is LCP.** Different metrics.

## Cache misuse

- **Adding a cache to fix a slow query without considering invalidation.** Cache invalidation is one of the two hard problems in computer science; you've added complexity.
- **Caching at the wrong layer.** Caching at the HTTP layer when the bottleneck is in the DB query. The HTTP cache hides the DB call but doesn't fix it; if the cache misses, the DB call is still slow.
- **Adding a cache that's never re-invalidated.** Stale data.
- **Adding a cache without metrics on hit-rate / size.** No way to tell if it's working.

## Skipping the verify step

- **"I applied the fix; tests pass; we're good."** Tests check correctness, not perf. The metric must move.
- **"The fix is intuitive."** Intuitive is not measured.
- **"The CI build is green; that's enough."** Unit tests don't exercise prod load.
- The rule: re-measure with the same protocol. Confirm the metric moved.

## Fixing the wrong bottleneck

- **"The trace shows DB time at 800ms; let me cache it."** But the actual user complaint is total latency 1.2s; if DB is 800ms and the rest is 400ms, even a perfect cache (DB → 0ms) only gets you to 400ms. Maybe the cache helps; maybe the rest of the stack also needs work.
- **"The slowest function is X; let me optimize X."** But X is called once per request and takes 5ms. Y is called 100 times per request and takes 1ms each (=100ms). Optimize Y.
- The rule: order by total time contribution, not single-function time.

## Confidence theatre

- **"High confidence" diagnosis with a ±50% measurement variance.** The measurement isn't signal; the confidence is theatre.
- **"It's definitely a memory leak."** Without a heap-size-over-time graph, "definitely" is too strong.
- **Hiding low confidence.** If you don't know, say so; STOP and surface.

## Reporting

- **Saying "fixed" without a before/after table.** Always include both.
- **Reporting only the headline number.** Include the context (window, env, sample size).
- **Hiding the guardrail.** It's part of the fix; the report names it.
- **Skipping residual risk.** Perf fixes often have follow-ups (other endpoints with the same pattern; monitoring tuning; dashboards to update).
