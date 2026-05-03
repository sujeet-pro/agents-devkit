# `investigate-datadog` — artifact format

## `.temp/task-<slug>/investigation/` layout for this skill

Per `/adk-core:temp-folder` and `/adk-core:auto`'s artifact contract.

```
.temp/task-<slug>/
├── prompt.txt                                       # verbatim user prompt + ISO timestamp (from /adk-core:auto)
└── investigation/
    ├── datadog.md                                   # this skill's primary output
    ├── datadog/
    │   ├── entities.md                              # resolved entity table (Phase 0)
    │   ├── queries.md                               # the literal queries that ran
    │   └── raw/                                     # per-query JSON dumps from MCP (gitignored, large)
    │       ├── logs-aggregate-<n>.json
    │       ├── metrics-<n>.json
    │       └── monitors-<n>.json
    └── validation/
        └── investigate-datadog.md                   # per-phase validator log
```

## Rules

1. **Slug** comes from the calling skill (`/adk-core:auto` → `bin/adk-task-slug`). Never invent your own.
2. **`datadog.md` is the deliverable.** Everything else is supporting evidence the operator can dig into.
3. **`raw/` is large and not for the report.** It exists so the operator can re-derive the report or rerun a follow-up query without re-hitting the MCP.
4. **Never write outside `.temp/task-<slug>/`.** All output lives under this slug.
5. **Never overwrite an existing `datadog.md` without backing it up** to `datadog-<ISO>.md`. The operator may have annotated the previous run.

## Top-level (non-task) areas

If the skill is called outside `/adk-core:auto` (rare, but supported), the artifact may be written to:

| Path | When |
| --- | --- |
| `.temp/reports/datadog-<slug>.md` | Standalone investigation, no umbrella task |
| `.temp/task-<slug>/investigation/datadog.md` | Inside an `auto`-orchestrated task (default) |

Same shape; different path. Per `/adk-core:auto`'s `artifact-format.md`.

## Companion files

- `.temp/task-<slug>/investigation/deploy.md` — sibling output from `/adk-investigate:investigate-deploy` (if `auto` chained both).
- `.temp/task-<slug>/investigation/incident.md` — `/adk-investigate:investigate-incident` aggregates `datadog.md` + `deploy.md` + Slack into a single report.
