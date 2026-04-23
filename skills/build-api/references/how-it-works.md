# `build-api` — how it works

## Decision flow

```mermaid
flowchart TD
    Start["build-api invoked"] --> Phase1["Phase 1: pre-execution validator"]
    Phase1 --> Confirm["Confirm intent (or --auto)"]
    Confirm --> Inventory["Inventory existing surface (sibling endpoints, error envelope, naming)"]
    Inventory --> Draft["Draft contract FIRST (types/schema, no impl)"]
    Draft --> Hyrum["Hyrum's Law audit — list observable behaviors"]
    Hyrum --> Validate["Design edge validation (single boundary)"]
    Validate --> Implement["Implement smallest correct code"]
    Implement --> Phase2["Phase 2: mid-flow validator gates"]
    Phase2 --> Verify["Run typecheck + lint + smoke test against contract"]
    Verify --> Phase3["Phase 3: pre-handoff validator"]
    Phase3 --> Report["Final report (contract diff + consumer impact + Hyrum note)"]
    Report --> Phase4["Phase 4: post-execution validator"]
```

The skill is built around the principle that the **contract is the deliverable** — the implementation is what follows. See `references/error-semantics.md` for the standard status-code / error-code mapping and `references/hyrums-law-audit.md` for the observable-behavior checklist.
