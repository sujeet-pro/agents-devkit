# `investigate-experiment` — artifact format

## `.temp/task-<slug>/investigation/` layout for this skill

```
.temp/task-<slug>/
├── prompt.txt
└── investigation/
    ├── experiment.md                                # this skill's primary output
    ├── experiment/
    │   ├── entities.md                              # resolved entity table (Phase 0)
    │   ├── reconciliation.md                        # working notes on the three-source comparison
    │   └── raw/
    │       ├── statsig-pulse-<exp-id>.json
    │       ├── mixpanel-primary-<metric>.json
    │       ├── dd-error-rate-<service>.json
    │       └── dd-p99-<service>.json
    ├── statsig.md                                   # if /adk-investigate:investigate-statsig also ran
    ├── mixpanel.md                                  # if /adk-investigate:investigate-mixpanel also ran
    ├── datadog.md                                   # if /adk-investigate:investigate-datadog also ran
    └── validation/
        └── investigate-experiment.md                # per-phase validator log
```

## Rules

1. **Slug** comes from the calling skill (`/adk-core:auto`).
2. **`experiment.md` is the primary deliverable.**
3. **Per-source raw JSON in `experiment/raw/`** for traceability.
4. **Never write outside `.temp/task-<slug>/`.**
5. **Never overwrite `experiment.md`** without backup at `experiment-<ISO>.md`.

## Top-level (non-task) areas

| Path | When |
| --- | --- |
| `.temp/reports/experiment-<slug>.md` | Standalone (no umbrella task) |
| `.temp/task-<slug>/investigation/experiment.md` | Inside `auto` task (default) |

## Companion files

This skill calls `Get_Experiment_Results` (Statsig), Mixpanel `Get-Events`, and DD `get_metrics` directly — it does NOT chain through `/adk-investigate:investigate-statsig`, `investigate-mixpanel`, or `investigate-datadog` skills. Those skills are heavier and produce their own reports; this skill is the focused three-source verdict.

If the operator wants the per-source detail, they invoke the per-source skills separately, after this skill's verdict.

## Subagent isolation

This skill does not spawn subagents — the three parallel reads are made directly from the skill's own context. (If at some future point the reads become heavier, the `incident-investigator` agent could be reused, but as designed each call is small and direct.)
