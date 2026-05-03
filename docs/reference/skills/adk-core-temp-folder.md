---
title: 'adk-core:temp-folder'
description: '  Canonical .temp/task-<slug>/ working-artifact layout. Every other adk skill writes through this convention. Use this skill whenever you need to create a new task workspace, look up the path for a particular artifact, or document the layout. The skill wraps the bin/adk-task-slug script for slug generation. Do NOT put final / committed artifacts here — .temp/ is gitignored. Do NOT use this skill to delete or clean .temp/ — that is the operator''s manual job (the folder is durable session context).'
plugin: 'adk-core'
skill: 'temp-folder'
source: 'plugins/adk-core/skills/temp-folder/SKILL.md'
group: 'core-skills'
order: 107
---
# adk-core:temp-folder

## Source

`plugins/adk-core/skills/temp-folder/SKILL.md`

## Skill Body

# temp-folder — canonical .temp/ layout authority

The single source of truth for `.temp/task-<slug>/` directory layout. Other skills shell out to `bin/adk-task-slug` to create their workspace.

## When to use

- A skill is starting and needs a fresh workspace.
- The user asks "where does adk put its working files?".
- Documentation links want to reference the layout.

## When NOT to use

- Final / committed artifacts → put them in the repo, not `.temp/`.
- Cleaning `.temp/` → that's the operator's manual job. The folder is durable session context.

## Common prompts

- "create a workspace for this task"
- "where do .temp/ files go?"
- "show me the .temp/ layout"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<slug-or-prompt>` | yes | The slug, or the prompt from which to derive a slug |
| `--scope <path>` | optional | Target directory (default: cwd) |
| `--print-only` | optional | Echo the slug; do NOT create the folder |

## Layout

```
.temp/task-<slug>/
├── prompt.txt                          # verbatim user prompt (auto / outer skill writes this)
├── skill-plan.md                       # auto / prompt-expand output
├── context.md                          # context-gather output
├── scope.md                            # if scoping ran
├── design.md                           # if design ran (rare for adk)
├── plan.md                             # implementer plan (code-* skills)
├── review/
│   ├── findings.md
│   ├── postback.md
│   └── reconciliation.md
├── investigation/
│   ├── datadog.md
│   ├── mixpanel.md
│   ├── statsig.md
│   ├── snowflake.md
│   ├── deploy.md
│   ├── incident.md
│   └── rca.md
├── docs/
│   ├── draft.md
│   └── review.md
├── validation/
│   ├── auto-validator.md
│   └── per-skill/<skill>.md
└── report.md                           # final consolidated report
```

## Top-level (non-task) areas

| Path | Purpose |
| --- | --- |
| `.temp/plans/<slug>.md` | Restructure / refactor plans (no task slug) |
| `.temp/drafts/<slug>.md` | Prose drafts before promotion |
| `.temp/reports/<slug>.md` | Reviews, audits, investigations not tied to a task |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos for research (gitignored) |
| `.temp/notes/<slug>.md` | Short-lived working notes |
| `.temp/setup-report.md` | Output of `/adk-core:setup --auto` |

## Workflow

```
Phase 1 — preflight
  - Verify `bin/adk-task-slug` exists and is executable.
  - Verify the target scope is writable unless --print-only is set.
  - No MCP or connector is required.

Phase 2 — create or print
  - Receive slug (or prompt to slug-ify).
  - Run bin/adk-task-slug "<input>" [--print] [--date] [--scope].
  - The script emits the slug and creates .temp/task-<slug>/ in cwd.
  - Return the slug + the absolute path to the workspace.
```

## Persona

> Convention enforcer. The .temp/ layout is the contract; you keep it consistent across skills.

See `references/persona.md`.

## Constitution

**Must do:**

1. Slugs are kebab-case, max 6 words, derived from prompt nouns/verbs.
2. Every skill writes ALL artifacts under `.temp/task-<slug>/`. No exceptions.
3. The skill creating a new task is responsible for the slug.
4. `.temp/` is gitignored. Verify before any write.
5. Slug is preserved across skill invocations within a session (the dispatcher passes it down).

**Must not do:**

1. Auto-clean old `.temp/task-*/` folders.
2. Use a date-only slug when descriptive nouns are available.
3. Write outside `.temp/task-<slug>/` from a skill that's mid-task.
4. Allow whitespace, uppercase, or punctuation in slugs.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- "I'll just write to the repo root for now" — no. `.temp/` exists for this.
- Auto-deleting old task folders. Old artifacts are research material; the user prunes manually.
- Using a different slug per skill in the same session. One slug per task.

## Output

The skill emits two things to stdout:

```
slug: <slug>
path: <absolute-path-to-.temp/task-<slug>/>
```

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Convention enforcer |
| `references/workflow.md` | Slug derivation rules |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | Slug examples (good + bad) |
| `references/output-format.md` | The slug + path output shape |
| `references/modes.md` | Mode contract |
| `references/interaction-contract.md` | Canonical interaction contract |
