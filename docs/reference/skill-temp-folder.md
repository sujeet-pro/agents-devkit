---
title: 'temp-folder'
description: '|'
skill_name: temp-folder
category: router
---
# temp-folder — `.temp/` working-artifact contract

Single source of truth for where intermediate artifacts live. Every other skill calls this convention to resolve paths.

## Rules

1. **Every task gets one folder** at `.temp/task-<slug>/`. Slug is kebab-case derived from the prompt, optionally date-prefixed.
2. **Never write outside this folder** before the deliverable is approved by the user.
3. **`.temp/` MUST be in `.gitignore`.** If absent, add it before any write.
4. **Folders are durable** — do not clean up after task completion. They are context for follow-up sessions.
5. **One canonical sub-path per artifact type.** No improvising new sub-paths.

## Canonical sub-paths

```
.temp/task-<slug>/
├── prompt.md                         # verbatim user prompt (auto skill writes this)
├── context.md                        # context-gather output (links to Jira/Confluence/Slack/...)
├── requirements.md                   # requirements skill
├── scope.md                          # scoping skill
├── brainstorm.md                     # plan-brainstorm
├── spec.md                           # plan-spec
├── design.md                         # plan-design
├── roadmap.md                        # plan-roadmap
├── proposal.md                       # plan-proposal
├── plan.md                           # final implementation plan (per-skill if multiple)
├── preview/sample-{1..5}.html        # frontend-mockup
├── validation/
│   ├── d1.md                         # review-local aggregate
│   └── per-skill/<skill>.md          # individual skill validators
├── browser-validation/
│   ├── verify-fix/{report.md, screenshots/, console.json, network.har}
│   ├── visual-check/{baseline,actual,diff}/<viewport>.png
│   ├── console-audit/{report.md, raw.json}
│   ├── interaction-test/{trace.md, screenshots/}
│   └── a11y-audit/{report.md, axe.json}
├── repos/                            # cloned reference repos for THIS task only
└── report.md                         # final consolidated report
```

## Top-level (cross-task) sub-paths

| Path | Purpose |
| --- | --- |
| `.temp/plans/<slug>.md` | Plans not tied to a specific task (e.g., restructure plans) |
| `.temp/drafts/<slug>.md` | Prose drafts before promotion |
| `.temp/reports/<slug>.md` | Standalone reviews / audits / investigations |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos for cross-task research |
| `.temp/notes/<slug>.md` | Short-lived working notes |

## Path resolution function (for callers)

```
resolveTempPath(slug, artifactType) -> string
```

| `artifactType` | Returns |
| --- | --- |
| `prompt` | `.temp/task-<slug>/prompt.md` |
| `context` | `.temp/task-<slug>/context.md` |
| `requirements` | `.temp/task-<slug>/requirements.md` |
| `scope` | `.temp/task-<slug>/scope.md` |
| `brainstorm` | `.temp/task-<slug>/brainstorm.md` |
| `spec` | `.temp/task-<slug>/spec.md` |
| `design` | `.temp/task-<slug>/design.md` |
| `roadmap` | `.temp/task-<slug>/roadmap.md` |
| `plan` | `.temp/task-<slug>/plan.md` |
| `preview/<n>` | `.temp/task-<slug>/preview/sample-<n>.html` |
| `validation/d1` | `.temp/task-<slug>/validation/d1.md` |
| `validation/<skill>` | `.temp/task-<slug>/validation/per-skill/<skill>.md` |
| `browser/<mode>` | `.temp/task-<slug>/browser-validation/<mode>/` |
| `report` | `.temp/task-<slug>/report.md` |

## Anti-patterns

See `references/anti-patterns.md`. Key ones: writing to repo root, omitting the slug, putting browser screenshots at repo root, committing `.temp/`.

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Path resolution flow + slug rules |
| `references/modes.md` | `auto` only |
| `references/persona.md` | The contract enforcer |
| `references/workflow.md` | First-write protocol (gitignore check + folder create) |
| `references/clarifying-questions.md` | Slug confirmation |
| `references/output-format.md` | Path-only output |
| `references/artifact-format.md` | Same as the table above (canonical layout) |
| `references/validator.md` | Validate a `.temp/task-<slug>/` against the contract |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | Worked slug examples |
| `references/interaction-contract.md` | Synced from canonical |
