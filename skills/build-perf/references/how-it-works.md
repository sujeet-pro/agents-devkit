# `build-perf` — how it works

## Decision flow

```mermaid
flowchart TD
    Start["build-perf invoked"] --> Phase1["Phase 1: pre-execution validator"]
    Phase1 --> Confirm["Confirm metric + target (reject vague 'faster')"]
    Confirm --> Baseline["Baseline measurement (capture raw artifact)"]
    Baseline --> Bottleneck["Identify single bottleneck WITH evidence"]
    Bottleneck --> Plan["Pick optimization pattern from references"]
    Plan --> Implement["Implement smallest correct change"]
    Implement --> Phase2["Phase 2: mid-flow validator gates"]
    Phase2 --> Remeasure["Re-measure with SAME tool, ≥3 runs"]
    Remeasure --> Guardrail["Add perf test / CI budget / monitor"]
    Guardrail --> Phase3["Phase 3: pre-handoff validator"]
    Phase3 --> Report["Report delta + bottleneck + guardrail"]
    Report --> Phase4["Phase 4: post-execution validator"]
```

The skill rejects "make it faster" prompts. See `references/perf-budgets.md` for default budgets, `references/measurement-tools.md` for tool selection per metric, and `references/optimization-patterns.md` for the catalog of patterns indexed by surface.
