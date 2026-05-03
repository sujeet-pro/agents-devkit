# `auto` — artifact format

## `.temp/task-<slug>/` canonical layout

Enforced by `/adk-core:temp-folder`. Every skill called from `auto` writes through this contract.

```
.temp/task-<slug>/
├── prompt.txt                               # verbatim user prompt + ISO timestamp
├── skill-plan.md                            # auto / prompt-expand output
├── context.md                               # context-gather output (if links)
├── dispatch.md                              # dispatcher subagent's per-slice results
├── plan.md                                  # implementer plan (code-* skills)
├── review/
│   ├── findings.md                          # review-* skills
│   ├── postback.md                          # what was posted
│   └── reconciliation.md                    # how existing comments treated
├── investigation/
│   ├── datadog.md
│   ├── mixpanel.md
│   ├── statsig.md
│   ├── snowflake.md
│   ├── deploy.md
│   ├── incident.md
│   └── rca.md
├── docs/
│   ├── draft.md                             # docs-write
│   └── review.md                            # docs-review
├── validation/
│   ├── auto-validator.md                    # auto's own per-phase log
│   └── per-skill/
│       ├── code-bugfix.md
│       ├── review-code-changes.md
│       └── ...
└── report.md                                # final consolidated report
```

## Top-level (non-task) areas

| Path | Purpose |
| --- | --- |
| `.temp/plans/<slug>.md` | Restructure / refactor plans (no task slug) |
| `.temp/drafts/<slug>.md` | Prose drafts before promotion |
| `.temp/reports/<slug>.md` | Reviews, audits, investigations not tied to a task |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos for research (gitignored) |
| `.temp/notes/<slug>.md` | Short-lived working notes |

## Rules

1. Slug is kebab-case, derived from prompt nouns/verbs (max 6 words). Date-prefix only when disambiguation is needed.
2. Never write outside `.temp/task-<slug>/` before final approval.
3. The folder is durable context — do not auto-clean after task completion. Old tasks accumulate; the user prunes manually.
4. `.temp/` is in `.gitignore`. Verify before any write.
5. The slug is preserved across skill invocations within a session.
