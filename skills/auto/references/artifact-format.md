# `auto` — artifact format

## `.temp/task-<slug>/` canonical layout

Enforced by `@adk:temp-folder`. Every skill called from `auto` writes through this contract.

```
.temp/task-<slug>/
├── prompt.md                                # verbatim user prompt
├── context.md                               # context-gather
├── requirements.md                          # requirements
├── scope.md                                 # scoping
├── brainstorm.md                            # plan-brainstorm (optional)
├── spec.md                                  # plan-spec (optional)
├── design.md                                # plan-design (optional)
├── roadmap.md                               # plan-roadmap (optional)
├── preview/
│   └── sample-{1..5}.html                   # frontend-mockup (UI tasks only)
├── plan.md                                  # final implementation plan
├── validation/
│   ├── d1.md                                # review-local aggregate
│   └── per-skill/<skill>.md                 # individual skill validators
├── browser-validation/                      # validate-browser (UI tasks only)
│   ├── verify-fix/{report.md, screenshots/, console.json, network.har}
│   ├── visual-check/{baseline,actual,diff}/<viewport>.png
│   ├── console-audit/{report.md, raw.json}
│   ├── interaction-test/{trace.md, screenshots/}
│   └── a11y-audit/{report.md, axe.json}
└── report.md                                # final consolidated report
```

## Rules

1. Slug is kebab-case, derived from prompt nouns. Date-prefix only when disambiguation needed.
2. Never write outside `.temp/task-<slug>/` before final approval.
3. The folder is durable context — do not clean it after task completion. Old tasks accumulate; users prune manually.
4. `.temp/` is in `.gitignore`. Verify before any write.
