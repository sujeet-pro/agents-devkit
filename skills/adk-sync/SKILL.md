---
name: adk-sync
description: |
  Publish, sync, push-to, post-to, update, fetch-as-markdown, pull-from-Confluence/Jira/Slack. Bidirectional 3P bridge for markdown. Hybrid path: writes to `<repo>/.temp/adk/sync/<task>/synced/` when invoked from a repo with a repo-coupled doc, else `~/.agents-devkit/sync/<task>/synced/` (default). READ mode (--read <url>): pulls a Confluence page / Jira description / GDoc / GitHub PR body / GitHub issue / Slack thread into local markdown. WRITE mode (--write <md-path> --to <destination>): publishes markdown to confluence / jira-desc / jira-comment / gh-pr-body / gh-issue-comment / slack / gdoc. Idempotent: match-by-id first, match-by-title-and-parent second, never by content hash. Format conversions are programmatic (md ↔ Confluence storage XHTML, md ↔ Jira ADF, md ↔ Slack blocks); AI only for "is this update safe?" checks. Per-invocation user confirmation required for every write regardless of mode (constitution §I.4). NEVER overwrites a human-authored target without explicit opt-in. NEVER changes sharing/restrictions/ACLs. Read helpers are called internally by other skills' Phase 0 context-gather.
allowed-tools: [Read, Write, Bash, WebFetch]
argument-hint: "(--read <url>) | (--write <md-path> --to <destination> [--target <id-or-title>]) [-i|--interactive] [--detailed] [--deep]"
metadata:
  category: docs
  kind: task
  layer: 1
  paths: ["**/*.md"]
  model: sonnet
  effort: low
  user-invocable: true
  disable-model-invocation: false
  needs_mcp_required: []
  needs_mcp_optional: [adk-mcp-atlassian, adk-mcp-github, adk-mcp-slack]
  needs_meta_info: [workspaces, repos]
  forks_emitted: [idempotency, conflict-resolution, format-conversion-strictness, overwrite-policy, model-depth]
---

# adk-sync

3P bridge. Read remote → markdown. Write markdown → remote. Mostly programmatic.

`--detailed` makes safety checks stricter and gathers more source/target context before conversion. `--deep` selects the stronger model profile per `shared/model-depth.md`; use it for ambiguous overwrite/conflict decisions, not routine format conversion.

## Modes

### Read mode

```
/adk-sync --read <url>
```

Pulls the resource into `<task_dir>/synced/<source>.md` (path resolved per `shared/paths.md`). Supported source URLs:

| URL type | Reference |
|---|---|
| Confluence page | `references/read-confluence.md` |
| Jira issue (description + comments) | `references/read-jira.md` |
| GitHub PR (body + comments) | `references/read-gh-pr.md` |
| GitHub issue | `references/read-gh-issue.md` |
| Slack thread permalink | `references/read-slack.md` |
| GDoc (via workspace connector or shared URL) | `references/read-gdoc.md` |

### Write mode

```
/adk-sync --write <md-path> --to <destination> [--target <id-or-title>]
```

Pushes the local markdown to the destination. Supported destinations:

| --to | Reference |
|---|---|
| `confluence` | `references/write-confluence.md` (md → storage XHTML; create-or-update by title + parent) |
| `jira-desc` | `references/write-jira-desc.md` (md → ADF; replace issue description) |
| `jira-comment` | `references/write-jira-comment.md` (md → ADF; append comment) |
| `gh-pr-body` | `references/write-gh-pr-body.md` (md as-is; replace PR body via `gh pr edit`) |
| `gh-issue-comment` | `references/write-gh-issue-comment.md` (md as-is; new comment) |
| `slack` | `references/write-slack.md` (md → Slack blocks; post to channel — requires SLACK_BOT_TOKEN) |
| `gdoc` | `references/write-gdoc.md` (md → GDoc; create-or-update by name + folder) |

## Workflow

```
Phase 0 — context-gather
  - Identify mode (read or write)
  - Resolve destination from --to + --target (or default from overrides)
  - Read mode: classify URL, prepare fetcher
  - Write mode: load source md, detect format, prepare converter

Phase 1 — advise
  - Read mode: 0–1 questions (usually just "confirm destination")
  - Write mode: up to 3 questions
    1. Idempotency check: existing target by ID or title-and-parent?
    2. Conflict resolution if target was edited by a human since last sync
    3. Per-invocation publish confirmation (REQUIRED, even --auto)

Phase 2 — execute (programmatic + light AI)
  - Read: fetch via MCP; convert to markdown; write to <task_dir>/synced/
  - Write: convert via skill script; idempotent existence check; create OR update
  - Idempotency: match by ID first; by title+parent second; never by content hash

Phase 3 — validate
  - Read: round-trip check (fetched → md → re-render → compare visible content)
  - Write: re-fetch the published resource and diff against source md

Phase 4 — report
  - URL of synced resource
  - Round-trip / diff verification result
  - Honest gap reporting (e.g., image link rewrites if Confluence)
```

## Hard rules

1. **Idempotent**: same input → same target. Match by ID; fall back to title-and-parent; never by content hash.
2. **Never overwrite human-authored** without explicit per-invocation user opt-in (check `lastEditor` or equivalent metadata).
3. **Per-invocation confirmation** for every write, even `--auto`. (Constitution §I.)
4. **Programmatic conversions** — markdown ↔ XHTML / ADF / Slack-blocks live in `scripts/`. No AI for deterministic format mapping.
5. **Refuse to change sharing / restrictions / ACLs**. That's a human action.
6. **No bulk operations** in a single invocation. One target per run; loop with the user for batches.

## Persona

- `shared/personas/doc-writer.md` — only for the "is this update safe?" pre-write check.

## Guidelines auto-loaded

- None by default. Reads / writes are content-neutral.

## Fork IDs

| fork_id | options | recommendation |
|---|---|---|
| `idempotency` | match-by-id / match-by-title-parent / new-always | match-by-id |
| `conflict-resolution` | abort / overwrite-with-confirm / merge-3-way | abort |
| `format-conversion-strictness` | strict / lossy-ok / preserve-html | strict |
| `overwrite-policy` | refuse-human-authored / confirm-each / always-overwrite | refuse-human-authored |

## Refusals

- Destination requires sharing change → refuse.
- Source md doesn't exist or is empty → refuse, name the issue.
- Bulk write requested → refuse; offer per-target loop.
- Human-authored target without explicit overwrite confirmation → refuse.
