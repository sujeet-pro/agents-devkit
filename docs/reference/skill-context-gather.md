---
title: 'context-gather'
description: 'Follows links found in a prompt, PR, doc, or task description and pulls relevant snippets from Jira, Confluence, Google Docs, Slack channels/threads, Gmail, and GitHub PRs/issues.'
artifact_kind: skill
skill_name: context-gather
category: standalone
---
# context-gather

Follows links found in a prompt, PR, doc, or task description and pulls relevant snippets from Jira, Confluence, Google Docs, Slack channels/threads, Gmail, and GitHub PRs/issues. Summarizes, deduplicates, and writes the consolidated context to `.temp/task-<slug>/context.md`. Use whenever the user pastes a link to an external system OR when reviewing/auditing a doc/PR that itself links to external systems for additional context. Do not use as a research-from-scratch tool (use `@adk:plan-research` (a.k.a. `adk-plan-research`) instead).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-context-gather` form via `agents-skills/`.

```text
/adk:context-gather            # interactive run (Claude Code)
/adk:context-gather --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-context-gather` (resolved through the
`agents-skills/adk-context-gather/` symlink).

## Source

Direct from `skills/context-gather/SKILL.md` — this page is auto-generated.

Pulls structured context from external systems referenced by URL in the prompt or in a target doc/PR.

## When to use

- The user pasted a Jira ticket / Confluence page / Google Doc / Slack thread / Gmail thread / GitHub PR URL.
- A doc you are reviewing references external sources for "see also" / "context" / "history".
- A code review comment links to a Slack discussion that needs to be read.

## When NOT to use

- The prompt has no external links → skip.
- You need to research a general topic from the web → `@adk:plan-research` (a.k.a. `adk-plan-research`).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<sources>` | yes | List of URLs (or auto-extracted from prompt) |
| `<task-slug>` | yes | Target `.temp/task-<slug>/` (created via `@adk:temp-folder`) |
| `<focus>` | optional | Free-text "what to look for" |
| `--auto` | optional | Skip per-source approval gates |

## Workflow

1. **Phase 1 validator.** Confirm slug exists, MCP availability for each source's host.
2. **Classify each source** by host:
   - `*.atlassian.net/browse/` → Jira (jira MCP)
   - `*.atlassian.net/wiki/` or `*confluence*` → Confluence (confluence MCP)
   - `docs.google.com/document/` → Google Docs (google-drive MCP)
   - `slack.com/archives/` → Slack thread (slack MCP)
   - `mail.google.com/` or message-id → Gmail (gmail MCP)
   - `github.com/.../{pull,issues}/N` → GitHub (`gh` CLI)
3. **Per source, fetch:**
   - Jira ticket: title, status, assignee, AC, parent, linked tickets, last 5 comments.
   - Confluence page: title, version, breadcrumb, full body, last 3 comments.
   - GDoc: title, last-modified, full body (or first 5000 words if larger), last 3 comments.
   - Slack thread: channel name, OP message, all replies, attached files (links only).
   - Gmail thread: subject, all messages (sender + ts + body), attachments (links only).
   - GitHub PR/Issue: title, status, body, all reviews/comments via `gh pr view --comments`.
4. **Per source, fall back gracefully** if MCP missing (per `references/mcp-fallback.md`):
   - Jira/Confluence → tell the user which env var is missing; skip silently.
   - GDoc/Gmail → same.
   - Slack → same.
   - GitHub → use `gh` CLI (always available if `setup` ran).
5. **Deduplicate**. If two sources reference the same Jira ticket, fetch once.
6. **Summarize each source** into 5-15 lines: what it is, current state, decisions captured, links to other sources.
7. **Aggregate** into `.temp/task-<slug>/context.md` (see `references/artifact-format.md` for the shape).
8. **Phase 4 validator.** Every URL processed (or marked as skipped with reason).

## Mode contract

`auto` only. Reading external context is non-destructive; review/fix do not apply.

## Output

`.temp/task-<slug>/context.md` — see `references/artifact-format.md`.
Final report: source count, fetched count, skipped count (with reasons), duration.

## Anti-patterns

- Pasting raw API responses into `context.md` (always summarize).
- Skipping a source silently because MCP is missing (always log it).
- Following links recursively without bound (max depth = 1 per skill run).
- Putting Slack thread URLs into `context.md` without their content (defeats the point).

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Per-source decision tree and aggregation flow |
| `references/modes.md` | auto only |
| `references/persona.md` | The aggregator persona |
| `references/workflow.md` | Detailed per-source steps |
| `references/clarifying-questions.md` | Source-list confirmation, focus question |
| `references/output-format.md` | Final report shape |
| `references/artifact-format.md` | `context.md` shape |
| `references/validator.md` | Four-phase gate |
| `references/anti-patterns.md` | What NOT to do |
| `references/mcp-fallback.md` | Per-MCP fallback (gh CLI for github; manual for others) |
| `references/source-types.md` | Per-host extraction recipe |
| `references/examples.md` | Worked examples |
| `references/interaction-contract.md` | Synced from canonical |


## Related skills

- [`auto`](./skill-auto.md) — `@adk:auto` (a.k.a. `adk-auto`)
- [`docs`](./skill-docs.md) — `@adk:docs` (a.k.a. `adk-docs`)
- [`plan-research`](./skill-plan-research.md) — `@adk:plan-research` (a.k.a. `adk-plan-research`)
- [`setup`](./skill-setup.md) — `@adk:setup` (a.k.a. `adk-setup`)
- [`temp-folder`](./skill-temp-folder.md) — `@adk:temp-folder` (a.k.a. `adk-temp-folder`)
