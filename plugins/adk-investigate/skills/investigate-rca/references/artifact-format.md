# `investigate-rca` — artifact format

## `.temp/task-<slug>/investigation/` layout for this skill

```
.temp/task-<slug>/
├── prompt.txt
└── investigation/
    ├── rca.md                                       # this skill's primary output
    ├── incident.md                                  # from Phase 2 (investigate-incident)
    ├── incident/                                    # from Phase 2 (raw / sub-artifacts)
    ├── deploy/                                      # from Phase 2 (per-repo deploy timelines)
    ├── statsig.md                                   # from Phase 3 (investigate-statsig --use audit-log)
    ├── statsig/                                     # from Phase 3 (raw)
    ├── git-blame.md                                 # from Phase 4 (code regression deep dive)
    ├── git-blame/
    │   ├── blame-<file-slug>.txt                    # `git blame` outputs
    │   └── pr-<num>.md                              # `gh pr view` outputs
    ├── mixpanel.md                                  # from Phase 5 (optional user impact)
    ├── mixpanel/                                    # from Phase 5 (raw)
    ├── rca/
    │   ├── timeline.md                              # working notes on the chronology
    │   ├── action-items-draft.md                    # before 5W frame applied
    │   └── blameless-rewrite-log.md                 # what blame-shaped phrases were rewritten
    └── validation/
        └── investigate-rca.md                       # per-phase validator log
```

## Rules

1. **Slug** comes from the calling skill (`/adk-core:auto`).
2. **`rca.md` is the primary deliverable.** Everything else is supporting evidence cited in the references section.
3. **Sub-skill outputs are siblings in `investigation/`.** This skill does NOT duplicate them; it cites their paths.
4. **`git-blame/` and `mixpanel/` are conditional.** Only created if those phases ran.
5. **Never write outside `.temp/task-<slug>/`.**
6. **Never overwrite `rca.md`** without backup at `rca-<ISO>.md`. The operator may have edited the previous draft.

## Top-level (non-task) areas

| Path | When |
| --- | --- |
| `.temp/reports/rca-<slug>.md` | Standalone (no umbrella task) |
| `.temp/task-<slug>/investigation/rca.md` | Inside `auto` task (default) |

## Companion files

The RCA is the terminal artifact in the investigate plugin. It does not feed downstream skills automatically. The natural next step is `/adk-docs:docs-publish-confluence` (or similar publication skill) AFTER the operator reviews and approves the RCA.

## Subagent isolation

This skill spawns the `incident-investigator` agent (via the chained `investigate-incident` call) for the multi-source pulls. Per the dispatcher rule, max 4 parallel subagents. This skill itself does not spawn additional subagents directly; it chains through the per-source skills.

## Multi-incident batch RCAs (out of scope for v0.1)

A future feature might be "RCA across the last N incidents". For v0.1, this skill handles one incident per invocation. Multi-incident batch is out of scope; the operator can run this skill N times and the operator-level synthesis is manual.
