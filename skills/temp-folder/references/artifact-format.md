# `temp-folder` — canonical layout

```
.temp/task-<slug>/
├── prompt.md
├── context.md
├── requirements.md
├── scope.md
├── brainstorm.md
├── spec.md
├── design.md
├── roadmap.md
├── proposal.md
├── plan.md
├── preview/sample-{1..5}.html
├── validation/
│   ├── d1.md
│   └── per-skill/<skill>.md
├── browser-validation/
│   ├── verify-fix/{report.md, screenshots/, console.json, network.har}
│   ├── visual-check/{baseline,actual,diff}/<viewport>.png
│   ├── console-audit/{report.md, raw.json}
│   ├── interaction-test/{trace.md, screenshots/}
│   └── a11y-audit/{report.md, axe.json}
├── repos/<owner>__<repo>/
└── report.md
```

Top-level `.temp/` (cross-task):

```
.temp/
├── plans/<slug>.md
├── drafts/<slug>.md
├── reports/<slug>.md
├── reference-repos/<owner>__<repo>/
└── notes/<slug>.md
```
