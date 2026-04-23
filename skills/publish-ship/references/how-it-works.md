# `publish-ship` — how it works

## Decision flow

```mermaid
flowchart TD
    Start["publish-ship invoked"] --> Phase1["Phase 1: pre-execution validator"]
    Phase1 --> Confirm["Confirm change + blast radius + flag + rollback"]
    Confirm --> Preflight["Run pre-launch checklist"]
    Preflight --> Block{"Any BLOCKER?"}
    Block -->|Yes| Stop["STOP — fix before launch"]
    Block -->|No| FlagCheck["Verify feature flag wiring (or document no-flag risk)"]
    FlagCheck --> Rollout["Write staged rollout plan"]
    Rollout --> Rollback["Verify rollback path (tested or dry-run)"]
    Rollback --> Monitor["Verify monitoring + SLOs in place"]
    Monitor --> Phase2["Phase 2: mid-flow validator gates"]
    Phase2 --> Approve["Approval gate (or --auto)"]
    Approve --> Handoff["Hand off to PaaS / CD pipeline"]
    Handoff --> FirstHour["Schedule first-hour post-deploy checks"]
    FirstHour --> Phase3["Phase 3: pre-handoff validator"]
    Phase3 --> Report["Final report (checklist + plan + monitoring + cleanup)"]
    Report --> Phase4["Phase 4: post-execution validator"]
```

The actual deploy command is NOT run by this skill — it prepares for the deploy and watches the first hour. See `references/pre-launch-checklist.md`, `references/staged-rollout.md`, `references/feature-flag-lifecycle.md`, and `references/first-hour-checklist.md` for the playbooks.
