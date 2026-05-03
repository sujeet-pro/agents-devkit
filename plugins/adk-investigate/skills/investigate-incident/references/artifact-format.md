# `investigate-incident` — artifact format

## `.temp/task-<slug>/investigation/` layout for this skill

```
.temp/task-<slug>/
├── prompt.txt
└── investigation/
    ├── incident.md                                  # this skill's primary output
    ├── incident/
    │   ├── entities.md                              # resolved entity table (Phase 0)
    │   ├── correlation.md                           # multi-source correlation working notes
    │   └── raw/
    │       ├── dd-logs-<svc>.json                   # raw DD MCP responses
    │       ├── dd-metrics-<svc>.json
    │       ├── dd-traces-<svc>.json
    │       ├── dd-monitors-<svc>.json
    │       └── slack-<channel>.json                 # if Slack scrape ran
    ├── datadog.md                                   # IF /adk-investigate:investigate-datadog also ran in this task
    ├── deploy.md                                    # IF aggregated; per-repo files in deploy/
    ├── deploy/
    │   ├── deploy-acme__checkout-api.md
    │   └── deploy-acme__order-service.md
    └── validation/
        └── investigate-incident.md                  # per-phase validator log
```

## Rules

1. **Slug** comes from the calling skill (`/adk-core:auto` → `bin/adk-task-slug`).
2. **`incident.md` is the primary deliverable.**
3. **Per-source raw JSON in `incident/raw/`.** Operator drills in via these.
4. **Per-repo deploy files in `deploy/`.** This skill calls `/adk-investigate:investigate-deploy` once per repo; each writes its own report; this skill aggregates.
5. **Never write outside `.temp/task-<slug>/`.**
6. **Never overwrite `incident.md`** without backup at `incident-<ISO>.md`.

## Top-level (non-task) areas

| Path | When |
| --- | --- |
| `.temp/reports/incident-<slug>.md` | Standalone (no umbrella task) |
| `.temp/task-<slug>/investigation/incident.md` | Inside `auto` task (default) |

## Companion files

- `.temp/task-<slug>/investigation/rca.md` — `/adk-investigate:investigate-rca` aggregates this skill's `incident.md` + Statsig audit + git blame.

## Subagent isolation

The `incident-investigator` agent (in this plugin's `agents/`) runs the parallel DD reads. Per the dispatcher rule (max 4 parallel subagents), this skill spawns at most 4 subagents at once. Each writes its own slice; this skill aggregates.

## Ephemerality

`.temp/` is gitignored. The reports persist across IDE sessions for the operator's reference but are NOT durable across `rm -rf .temp/`. Long-term post-mortem records belong in Confluence / a docs system; the report's `Follow-up` section recommends `/adk-docs:docs-publish-confluence` for persistence.
