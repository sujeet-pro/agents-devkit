# `build-security` — how it works

## Decision flow

```mermaid
flowchart TD
    Start["build-security invoked"] --> Phase1["Phase 1: pre-execution validator"]
    Phase1 --> Confirm["Confirm gap + source + mitigation"]
    Confirm --> Tier{"Three-tier classification"}
    Tier -->|Always| Repro["Reproduce / cite advisory"]
    Tier -->|Ask| Approve["Explicit user approval"]
    Tier -->|Never| Refuse["REFUSE + explain why"]
    Approve --> Repro
    Repro --> SecretScan["Pre-commit secret scan (mandatory)"]
    SecretScan --> Plan["Pick OWASP pattern"]
    Plan --> Implement["Smallest correct change"]
    Implement --> RegTest["Add regression test"]
    RegTest --> Phase2["Phase 2: mid-flow validator gates"]
    Phase2 --> Validate["Run audit tool + typecheck + lint + tests"]
    Validate --> Phase3["Phase 3: pre-handoff validator"]
    Phase3 --> Report["Report gap + mitigation + residual risk"]
    Report --> Phase4["Phase 4: post-execution validator"]
```

The skill enforces the three-tier boundary system from `references/three-tier-boundaries.md` and consults `references/owasp-patterns.md` for OWASP Top 10 mitigation patterns.
