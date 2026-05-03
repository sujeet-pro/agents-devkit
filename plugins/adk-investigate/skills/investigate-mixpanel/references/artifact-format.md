# `investigate-mixpanel` — artifact format

## `.temp/task-<slug>/investigation/` layout for this skill

```
.temp/task-<slug>/
├── prompt.txt
└── investigation/
    ├── mixpanel.md                                  # this skill's primary output
    ├── mixpanel/
    │   ├── entities.md                              # resolved entity table (Phase 0)
    │   ├── queries.md                               # the literal queries that ran
    │   └── raw/                                     # per-query JSON dumps (gitignored, large)
    │       ├── funnel-<id>-now.json
    │       ├── funnel-<id>-baseline.json
    │       ├── cohort-<id>-retention.json
    │       └── usage-top-events.json
    └── validation/
        └── investigate-mixpanel.md                  # per-phase validator log
```

## Rules

1. **Slug** comes from the calling skill (`/adk-core:auto` → `bin/adk-task-slug`).
2. **`mixpanel.md` is the deliverable.** Everything else is supporting evidence.
3. **`raw/` is large and not for the report.** It exists so the operator can re-derive the report or rerun a follow-up query.
4. **Never write outside `.temp/task-<slug>/`.**
5. **Never overwrite an existing `mixpanel.md`** without backing it up to `mixpanel-<ISO>.md`.

## Top-level (non-task) areas

If the skill is called outside `/adk-core:auto`:

| Path | When |
| --- | --- |
| `.temp/reports/mixpanel-<slug>.md` | Standalone, no umbrella task |
| `.temp/task-<slug>/investigation/mixpanel.md` | Inside an `auto`-orchestrated task (default) |

## Companion files

- `.temp/task-<slug>/investigation/datadog.md` — sibling output from `/adk-investigate:investigate-datadog`.
- `.temp/task-<slug>/investigation/statsig.md` — sibling output from `/adk-investigate:investigate-statsig`.
- `/adk-investigate:investigate-experiment` aggregates `mixpanel.md` + `statsig.md` + `datadog.md` for its three-source verdict.
