# `investigate-deploy` — artifact format

## `.temp/task-<slug>/investigation/` layout for this skill

```
.temp/task-<slug>/
├── prompt.txt
└── investigation/
    ├── deploy.md                                    # this skill's primary output
    ├── deploy/
    │   ├── entities.md                              # resolved entity table (Phase 0)
    │   ├── command.md                               # the literal `gh` command that ran
    │   └── raw/
    │       ├── gh-run-list-<repo>.json              # raw `gh run list` JSON
    │       └── dd-deploy-events-<service>.json      # if DD cross-reference ran
    └── validation/
        └── investigate-deploy.md                    # per-phase validator log
```

## Rules

1. **Slug** comes from the calling skill (`/adk-core:auto` → `bin/adk-task-slug`).
2. **`deploy.md` is the deliverable.**
3. **Raw JSON** in `raw/` is the operator's escape hatch — they can drill into a specific run without re-running `gh`.
4. **Never write outside `.temp/task-<slug>/`.**
5. **Never overwrite existing `deploy.md`** without backup at `deploy-<ISO>.md`.

## Top-level (non-task) areas

| Path | When |
| --- | --- |
| `.temp/reports/deploy-<slug>.md` | Standalone (no umbrella task) |
| `.temp/task-<slug>/investigation/deploy.md` | Inside `auto` task (default) |

## Companion files

- `.temp/task-<slug>/investigation/datadog.md` — sibling output; cross-referenced for DD deploy events.
- `.temp/task-<slug>/investigation/incident.md` — `/adk-investigate:investigate-incident` aggregates `deploy.md` as one of its required sources.
- `.temp/task-<slug>/investigation/rca.md` — `/adk-investigate:investigate-rca` aggregates `deploy.md`.

## Multi-repo runs

When the parent skill (e.g. `investigate-incident`) requests deploys for multiple repos (e.g. all repos that map to a single service tag in `repos.md`), this skill writes one report per repo:

```
investigation/
└── deploy/
    ├── deploy-acme__checkout-api.md
    ├── deploy-acme__checkout-web.md
    └── deploy-acme__order-service.md
```

And aggregates a top-level `deploy.md` summarizing across all three.
