---
title: First skill
description: Run /adk:auto (or adk-auto) on a real task — the prompt-routing dispatcher that picks the right downstream skills for you.
order: 2
---

# First skill

Once [installation](./installation.md) is done, the easiest way to start is the prompt-routing dispatcher: `/adk:auto` (Claude) or `adk-auto` (every other harness). It reads your prompt, gathers context (Jira / Confluence / Slack / GDocs / Gmail via MCP if links are present), runs requirements + scoping with you, and then dispatches per-task subagents loaded with the right downstream skills.

> [!TIP]
> If you already know which skill you want, invoke it directly — `/adk:plan-brainstorm`, `/adk:review-pr`, `/adk:audit-repo`, etc. The auto-router is for when you're unsure.

## Hello world

In Claude Code:

```text
/adk:auto    Build me a small CSV-export endpoint for the existing /api/users route. Keep it surgical.
```

In Cursor / Codex / Gemini:

```text
adk-auto    Build me a small CSV-export endpoint for the existing /api/users route. Keep it surgical.
```

## What happens

1. **Phase A — Requirements.** Claude restates the goal in one sentence, asks one clarifying question at a time, and locks `currentState` / `targetState` / `changeTolerance`.
2. **Phase B — Scoping.** Lists 2-3 viable approaches with explained pros/cons/blast-radius, recommends a default, asks for approval.
3. **Phase C — Dispatch.** Spawns parallel subagents (`implementer`, `test-engineer`, `doc-writer`, `code-reviewer`, `validate-browser` as relevant) loaded with the right downstream skills.
4. **Phase D — Aggregate.** Collects each subagent's report, runs the cross-cutting validators, surfaces a single verdict.

Every phase is gated unless you pass `--auto`.

## Safe defaults

```text
/adk:auto --auto                    # unattended; pick safe defaults at every gate
/adk:auto --mode review             # produce findings only — no writes
/adk:auto --scope src/users/        # restrict subagent reads to one path
```

## Other good first skills

| Want to… | Skill | Why |
| --- | --- | --- |
| Decide between two approaches | [`/adk:plan-brainstorm`](../../reference/skill-plan-brainstorm.md) | Iterative narrowing with explicit options + confidence target. |
| Self-review uncommitted work | [`/adk:review-local`](../../reference/skill-review-local.md) | Severity-tiered findings on `git status` + branch diff before push. |
| Review a remote PR | [`/adk:review-pr`](../../reference/skill-review-pr.md) | Posts findings back via `gh` CLI / Bitbucket / Atlassian MCP. |
| Triage CI failures | [`/adk:cicd-fix`](../../reference/skill-cicd-fix.md) | Watches `gh pr checks` (via `monitor-ci-status`) and fixes the failing job. |
| Update the docs site | [`/adk:prj-update-docs`](../../reference/) | Regenerates this docs site from the current `skills/`, `agents/`, `hooks/`, `bin/`, `.mcp.json`. |
| Refresh the docs of any other repo | [`/adk:docs-write`](../../reference/skill-docs-write.md) | One-pass authoring of any markdown deliverable from real source. |

## Where the working artifacts go

Every skill writes intermediate output under `.temp/` (gitignored). The canonical layout for a task initiated by `/adk:auto`:

```
.temp/task-<slug>/
  context.md          # what the dispatcher gathered (Jira ticket, Confluence page, etc.)
  requirements.md     # locked requirements after Phase A
  scope.md            # locked scope after Phase B
  brainstorm.md       # only if plan-brainstorm fired
  spec.md / design.md / roadmap.md / plan.md   # depending on the task
  preview/sample-{1..5}.html                    # frontend mockups
  validation/<phase>.md
  browser-validation/<mode>/...
  report.md           # final aggregated report
```

Top-level `.temp/` paths are documented in [`AGENTS.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/AGENTS.md).

## Next

- [Reference](../../reference/skills/README.md) — every skill, agent, hook, MCP server, and CLI script.
- [Concepts](../../concepts/) — philosophy, skill anatomy, memory files.
- Run [`/adk:setup`](../../reference/skill-setup.md) again any time `bin/adk-doctor` flags something missing.
