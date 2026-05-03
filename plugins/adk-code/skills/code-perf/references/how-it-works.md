# `code-perf` — how it works (diagrams)

## Phase flow (measure-fix-verify cycle)

```mermaid
flowchart TD
    Prompt["User prompt + (optional) --budget"] --> P0["Phase 0: prompt expand + service + metric"]
    P0 --> P1["Phase 1: preflight (commands + tests green + MCPs)"]
    P1 --> P2["Phase 2: MEASURE baseline"]
    P2 --> P3["Phase 3: IDENTIFY bottleneck (with QUOTED evidence)"]
    P3 --> Conf{"Confidence ≥ medium?"}
    Conf -- no --> Stop1["STOP: low confidence; surface"]
    Conf -- yes --> Approve3{"--auto?"}
    Approve3 -- no --> Gate3["Approval: confirm bottleneck + proposed fix"]
    Approve3 -- yes --> P4
    Gate3 --> P4["Phase 4: FIX (implementer)"]
    P4 --> P5["Phase 5: VERIFY (re-measure, same protocol)"]
    P5 --> Move{"Metric moved correctly?"}
    Move -- no --> Wrong{"2nd wrong diagnosis?"}
    Wrong -- no --> P3
    Wrong -- yes --> Stop2["STOP: wrong diagnosis; ask user"]
    Move -- yes --> Budget{"--budget? met?"}
    Budget -- no --> P3
    Budget -- yes --> P6["Phase 6: GUARDRAIL (perf test / CI budget / DD monitor)"]
    Move -- wrong-direction --> Revert["REVERT; investigate"]
    P6 --> P7["Phase 7: REPORT (before/after + fix + guardrail)"]
    P7 --> Done["Hand-off: offer-depth question"]
```

## Bottleneck identification decision tree

```mermaid
flowchart TD
    Start["Have baseline measurement"] --> Q1{"What kind of perf?"}
    Q1 -- "endpoint latency" --> Endpoint["DD APM trace<br/>Look at slowest spans (DB, downstream, GC)"]
    Q1 -- "function CPU" --> Func["Profile (perf, py-spy, async-profiler, Chrome DevTools)<br/>Look at self_time"]
    Q1 -- "memory" --> Mem["Heap snapshot diff<br/>Look at retained sizes; long-lived → short-lived references"]
    Q1 -- "browser" --> Browser["Lighthouse + Chrome perf trace<br/>Look at long tasks (>50ms), bundle size, render blocking"]
    Q1 -- "build" --> Build["Build with --profile<br/>Look at longest steps"]
    Endpoint --> Q2{"Slowest span: DB?"}
    Q2 -- yes --> N1{"Multiple sequential same-shape spans?"}
    N1 -- yes --> NPlus1["Hypothesis: N+1 → batch the call"]
    N1 -- no --> SlowQuery["Hypothesis: slow query → EXPLAIN ANALYZE → index? rewrite?"]
    Q2 -- no --> Downstream{"Slowest span: downstream HTTP?"}
    Downstream -- yes --> DS["Hypothesis: slow downstream → cache? parallel? circuit breaker?"]
    Func --> Top{"Top self_time function?"}
    Top --> Algo["Hypothesis: algorithmic → big-O analysis"]
    Mem --> Retain{"Object with monotonically growing retained size?"}
    Retain -- yes --> Leak["Hypothesis: leak — find the long-lived reference holder"]
    Browser --> Block{"Largest blocker?"}
    Block -- "JS bundle" --> Bundle["Hypothesis: bundle too big → code-split, lazy-load"]
    Block -- "image" --> Image["Hypothesis: image too late / too big → preload / optimize"]
    Block -- "render" --> Render["Hypothesis: layout thrash / large reflow → audit CSS / DOM"]
```

## Measurement protocol decision (Phase 2)

```mermaid
flowchart TD
    Start["Need to measure"] --> Q1{"Production metric?"}
    Q1 -- yes --> DD["Datadog APM (p50/p95/p99 over window)"]
    Q1 -- no --> Q2{"Function-level CPU?"}
    Q2 -- yes --> Bench["Benchmark (existing or hyperfine/tinybench/wrk)"]
    Q2 -- no --> Q3{"Memory?"}
    Q3 -- yes --> Heap["Heap snapshot before/after a workload"]
    Q3 -- no --> Q4{"Browser?"}
    Q4 -- yes --> LH["Lighthouse + Chrome perf trace"]
    Q4 -- no --> Q5{"Build / CI?"}
    Q5 -- yes --> Time["time + --profile flags + repeat 3-5x"]
    Q5 -- no --> Ask["Ask the operator which protocol applies"]
```

## Guardrail decision tree

```mermaid
flowchart TD
    Start["Need a guardrail"] --> Q1{"Function / endpoint perf?"}
    Q1 -- yes --> PerfTest["Perf test in suite (assert duration < threshold)"]
    Q1 -- no --> Q2{"Browser perf?"}
    Q2 -- yes --> LCi["Lighthouse-CI threshold"]
    Q2 -- no --> Q3{"Bundle size?"}
    Q3 -- yes --> BundleCI["Bundle-size CI check (e.g. webpack-bundle-analyzer threshold)"]
    Q3 -- no --> Q4{"Build time?"}
    Q4 -- yes --> BuildCI["CI step that fails if build > N seconds"]
    Q4 -- no --> Q5{"Production-monitored?"}
    Q5 -- yes --> DDMon["Datadog monitor recommendation (skill does not create directly)"]
    Q5 -- no --> Manual["Document the manual check in the runbook"]
```
