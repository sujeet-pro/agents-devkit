# `investigate-snowflake` — artifact format

## `.temp/task-<slug>/investigation/` layout for this skill

```
.temp/task-<slug>/
├── prompt.txt
└── investigation/
    ├── snowflake.md                                 # this skill's primary output
    ├── snowflake/
    │   ├── entities.md                              # resolved entity table (Phase 0)
    │   ├── sql/                                     # one file per query
    │   │   ├── q1-<short-slug>.sql
    │   │   └── q2-<short-slug>.sql
    │   └── raw/                                     # query results (gitignored, may be large)
    │       ├── q1-<short-slug>.json
    │       └── q2-<short-slug>.json
    └── validation/
        └── investigate-snowflake.md                 # per-phase validator log
```

## Rules

1. **Slug** comes from the calling skill (`/adk-core:auto` → `bin/adk-task-slug`).
2. **`snowflake.md` is the deliverable.**
3. **`raw/` MUST be inside `.temp/`.** The skill validates the path before writing — anything outside is rejected.
4. **`sql/` keeps each query as a separate file.** This makes it cheap to re-run a previous query without re-rendering it.
5. **Never overwrite existing `snowflake.md`** without backup at `snowflake-<ISO>.md`.
6. **No raw results outside `.temp/`.** Production data must not leak into the repo.

## Top-level (non-task) areas

| Path | When |
| --- | --- |
| `.temp/reports/snowflake-<slug>.md` | Standalone (no umbrella task) |
| `.temp/task-<slug>/investigation/snowflake.md` | Inside `auto` task (default) |

## .gitignore enforcement

`.temp/` MUST be in the repo's `.gitignore`. The skill checks this in Phase 1 preflight — if `.temp/` is not gitignored, the skill stops with a clear error and the suggested `.gitignore` line. Production data must NEVER be committable.

## Companion files

- `.temp/task-<slug>/investigation/datadog.md` — sibling output, may be cross-referenced.
- `.temp/task-<slug>/investigation/mixpanel.md` — sibling.

This skill does NOT participate in the `investigate-incident` / `investigate-rca` composite chains by default — it's a standalone read tool. Composite skills do not auto-call it (Snowflake reads need explicit operator intent because of the data sensitivity).
