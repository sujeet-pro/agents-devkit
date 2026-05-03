# `investigate-statsig` — artifact format

## `.temp/task-<slug>/investigation/` layout for this skill

```
.temp/task-<slug>/
├── prompt.txt
└── investigation/
    ├── statsig.md                                   # this skill's primary output
    ├── statsig/
    │   ├── entities.md                              # resolved entity table (Phase 0)
    │   ├── calls.md                                 # the literal MCP calls that ran
    │   └── raw/                                     # per-call JSON dumps (gitignored)
    │       ├── pulse-<experiment-id>.json
    │       ├── audit-<from>--<to>.json
    │       └── gates-list-<filter>.json
    └── validation/
        └── investigate-statsig.md                   # per-phase validator log
```

## Rules

1. **Slug** comes from the calling skill (`/adk-core:auto` → `bin/adk-task-slug`).
2. **`statsig.md` is the deliverable.**
3. **`raw/` for traceability.** The operator may want to re-derive the report or grep for a specific entry.
4. **Never write outside `.temp/task-<slug>/`.**
5. **Never overwrite existing `statsig.md`** without backup at `statsig-<ISO>.md`.

## Top-level (non-task) areas

| Path | When |
| --- | --- |
| `.temp/reports/statsig-<slug>.md` | Standalone (no umbrella task) |
| `.temp/task-<slug>/investigation/statsig.md` | Inside `auto` task (default) |

## Companion files

- `.temp/task-<slug>/investigation/datadog.md` — sibling output from `/adk-investigate:investigate-datadog`.
- `.temp/task-<slug>/investigation/mixpanel.md` — sibling output from `/adk-investigate:investigate-mixpanel`.
- `.temp/task-<slug>/investigation/incident.md` — `/adk-investigate:investigate-incident` aggregates `statsig.md`'s `audit-log` slice.
- `.temp/task-<slug>/investigation/rca.md` — `/adk-investigate:investigate-rca` aggregates `statsig.md`'s `audit-log` for ±2h around symptom.
