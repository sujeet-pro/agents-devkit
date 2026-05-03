# `code-perf` — measurement protocol

Per-tool recipes for capturing the baseline + after-measurement. The same recipe MUST be used for both phases (that's what makes the comparison valid).

## HTTP endpoint latency (production)

### Datadog APM

Tool: Datadog APM (via the `plugin-datadog-datadog` MCP — see `~/.config/adk/datadog.md` for site / env / service aliases).

Query shape (Datadog format):

```
p50:trace.<service>.request{env:<env>,resource_name:<resource>}
p95:trace.<service>.request{env:<env>,resource_name:<resource>}
p99:trace.<service>.request{env:<env>,resource_name:<resource>}
```

Example:

```
p99:trace.checkout-api.request{env:prod,resource_name:POST_/api/checkout}
```

Window:

- Hot regression: 24h (covers the regression boundary).
- Budget work: 7d.

For the bottleneck identification (Phase 3), pull a slow trace via the DD UI or the API:

- Filter by `duration:>1s` (or whatever threshold matches the p99 baseline).
- Inspect spans: look at the deepest spans, the slowest spans by self-time, and any patterns of repeated same-name spans (N+1 signature).

### `wrk` / `ab` (load testing locally)

For local benchmarking of a function-level HTTP endpoint:

```bash
wrk -t4 -c50 -d30s --latency http://localhost:3000/api/checkout
```

Capture: avg latency, p50, p95, p99 from `wrk`'s output.

```bash
ab -c 50 -n 5000 http://localhost:3000/api/checkout
```

`ab` outputs percentiles in its summary.

## Function-level CPU profiling

### Node / V8

```bash
node --cpu-prof --cpu-prof-dir=. <script>
# or, with Chrome DevTools:
node --inspect-brk <script>
# then attach Chrome DevTools, hit "record", run, hit "stop"
```

Profile output: a `.cpuprofile` file. Open in Chrome DevTools Performance panel; look at "self time" column.

### Python

```bash
py-spy record -o profile.svg -- python <script>
# or:
python -m cProfile -o profile.prof <script>
python -m pstats profile.prof
```

`py-spy` produces a flame graph SVG; `cProfile` produces a sortable stats file.

### JVM (Java / Kotlin)

```bash
async-profiler -d 30 -f profile.html <pid>
```

Flame graph HTML; look at the widest stacks.

### Rust

```bash
cargo flamegraph --bin <binary>
```

Or with `perf`:

```bash
perf record -F 99 ./target/release/<binary>
perf report
```

### Go

```bash
go test -cpuprofile=cpu.prof -bench=.
go tool pprof cpu.prof
# (interactive: top, list <function>, web)
```

## Microbenchmarks

### Vitest / `tinybench`

```ts
import { bench, describe } from 'vitest';

describe('foo', () => {
  bench('baseline', () => { … });
  bench('candidate', () => { … });
});
```

### `hyperfine` (CLI binaries)

```bash
hyperfine --warmup 3 --runs 10 'script-baseline' 'script-candidate'
```

Outputs mean + stddev for each.

### Go benchmark

```bash
go test -bench=. -benchmem -count=10
benchstat baseline.txt candidate.txt
```

`benchstat` shows the statistical significance of the difference.

## Memory profiling

### Node

Heap snapshots:

1. Run the app under controlled load.
2. At t=0, t=mid, t=end: `node --inspect-brk` → DevTools "Memory" tab → "Heap snapshot".
3. Save each as `.heapsnapshot`.
4. Diff the snapshots: in DevTools Memory tab, select snapshot 2 with "Comparison" view against snapshot 1.

Allocation timeline:

```bash
node --inspect-brk <script>
# DevTools → Memory → "Allocation instrumentation on timeline"
```

### Python

```python
import tracemalloc
tracemalloc.start()
# ... workload ...
snapshot1 = tracemalloc.take_snapshot()
# ... more workload ...
snapshot2 = tracemalloc.take_snapshot()
diff = snapshot2.compare_to(snapshot1, 'lineno')
for stat in diff[:10]:
    print(stat)
```

### JVM

```bash
jmap -dump:live,format=b,file=heap.hprof <pid>
# analyze with Eclipse MAT or VisualVM
```

GC log analysis:

```bash
java -Xlog:gc*:file=gc.log <main-class>
# analyze with GCViewer
```

## Browser perf

### Lighthouse

```bash
npx lighthouse https://example.com --preset=desktop --output=json --output-path=./lighthouse-baseline.json
# or with CLI flags for mobile + slow 4G:
npx lighthouse https://example.com --preset=experimental --output=json --output-path=./lighthouse-mobile.json
```

Headline numbers: LCP, TTI, TBT, CLS, FCP, SI, performance score.

### Chrome DevTools Performance trace

1. Open page in Chrome.
2. DevTools → Performance → Record.
3. Interact / load.
4. Stop. Save profile (`.json`).

Look at: Long tasks (>50ms), main-thread blocking, large layouts/repaints, JS execution time.

### Web Vitals (real user monitoring)

If the repo has Web Vitals reporting (e.g. via `web-vitals` npm package + a backend endpoint), pull from the analytics backend (Datadog RUM, Mixpanel events, etc.).

## Build / CI perf

### Local timing

```bash
time pnpm build
# 3-5 runs averaged
for i in 1 2 3 4 5; do time pnpm build; done
```

### Webpack / Vite profiling

```bash
# Webpack
webpack --profile --json > stats.json
# analyze with webpack-bundle-analyzer or speed-measure-webpack-plugin

# Vite
DEBUG=vite:* vite build > vite.log 2>&1
```

### Gradle profiling

```bash
./gradlew build --profile
# generates an HTML report in build/reports/profile/
```

### CI build profiling

Most CI systems expose per-step timing in their UI. For deeper analysis:

- GitHub Actions: enable workflow telemetry; pull from the API.
- CircleCI: per-step timing in the UI.
- Buildkite: agent telemetry.

## Cross-cutting rules

1. **Same protocol baseline + after.** That's the entire point of the re-measurement.
2. **Multiple runs for noisy measurements.** 3-5 runs minimum; report mean ± stddev.
3. **Match the conditions.** Local benchmarks should mimic prod (concurrency, data volume, network latency) where feasible.
4. **Quote the tool's output verbatim** (≤15 words per quote). Don't paraphrase.
5. **Save raw output as artifacts** under `.temp/task-<slug>/` so the reviewer can re-verify.

## When the metric is unstable

If the baseline measurement varies > ±20% across runs, the measurement is not signal. Options:

- **Increase sample size.** 10+ runs for tight CI / noisy environments.
- **Control more variables.** Pin the test data, the env, the load.
- **Switch to a different metric.** If "total latency" is noisy, look at the bottleneck-span latency (DB time alone may be more stable).
- **STOP and surface.** If you can't get a stable signal, the perf work is infeasible until the measurement is fixed.
