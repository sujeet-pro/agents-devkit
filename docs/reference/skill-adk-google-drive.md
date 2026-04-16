---
title: 'adk-google-drive'
description: 'Manage Google Docs, Sheets, Slides, and Drive files via MCP. Use when creating, reading, updating, or sharing Google Workspace documents'
skill_name: adk-google-drive
category: task
workflow_tier: full
user_invocable: true
---

# adk-google-drive

Use `adk-google-drive` to manage Google Docs, Sheets, Slides, and Drive files via MCP. Use when creating, reading, updating, or sharing Google Workspace documents. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-google-drive` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What Google Drive operation to perform |
| `--action` | `create`, `read`, `update`, `share`, `search` | auto-detect | Narrow the operation domain |
| `--type` | `doc`, `sheet`, `slides`, `file` | auto-detect | Target document type |
| `--target` | file ID or name | none | Specific file to operate on |
| `--auto` | flag | off | Skip confirmations for non-destructive operations |
| `--help` | flag | off | Show this skill and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it.
- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

See `references/workflow.md` for full phase definitions.

| Phase | Action | Gate |
| --- | --- | --- |
| 1. Locate | Find or identify target file/folder via search or `--target` | **Confirm**: target and intent |
| 2. Plan | Propose content or organizational changes (create, update, share, move) | **Approval** for writes and permission changes |
| 3. Execute | Create, update, or organize files via Google Drive MCP tools | -- |
| 4. Verify | Confirm changes via Drive API; read back document state | -- |

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```
**Action**: created Google Doc
**Target**: "Q3 Planning" (ID: 1BxiMVs0XRA5...)
**URL**: https://docs.google.com/document/d/1BxiMVs0XRA5.../edit
**Sharing**: shared with team@example.com as editor
**Next**: add content sections, share with stakeholders
```

Lead with action and URL. Offer content details on request.

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- document creation, content overwrites, sharing, and permission changes require approval; reads and searches proceed immediately.
- **Plan First** -- locate target, propose changes, preview content, then execute after confirmation.
- **Brainstorm Only For Workspace Choice** -- when the user is still deciding between creating, updating, sharing, or searching Docs/Sheets/Slides/Drive files, run a short brainstorming pass before mutating anything.
- **Concise by Default** -- lead with document URL and action summary; offer content preview on request.
- **Self-Sufficient** -- requires Google Drive MCP server with OAuth; provides setup instructions if missing or auth expired.
- **Auto Mode** -- `--auto` skips confirmations for non-destructive ops; overwrites and permission changes always require approval.

### Persona

See `references/persona.md` for full definition.

**Document Management Specialist.** Precise workspace operator who manages Google Docs, Sheets, Slides, and Drive files through structured API operations. Verifies authentication before acting, confirms targets before writing, and always produces document URLs as proof of execution.

### When To Use

- create Google Docs, Sheets, or Slides from scratch or from local content
- read or extract content from existing Google Workspace documents
- update document content, formatting, or structure
- search Drive for files by name, type, or content
- share files or folders and manage permissions
- create folders, upload or download files

### When NOT To Use

- local file operations -- use standard file tools directly
- non-Google cloud storage -- use the appropriate platform connector
- Confluence documentation -- use `adk-confluence`
- calendar-only tasks with no Drive component -- use calendar tools directly

### Pre-flight

Run `python3 scripts/preflight.py` first. Then verify:

1. Verify `git` and `python3` are in PATH
2. Confirm the `google-drive` MCP server is configured in IDE settings
3. Check OAuth authentication status via `authGetStatus`
4. If auth expired or MCP missing, exit with setup/re-auth instructions

### Interaction Protocol

- **Confirm target document**: before executing, confirm which document or folder will be affected
- **Preview before writing**: for create and update, show a content preview and wait for approval
- **Confirm sharing changes**: always confirm before adding or removing permissions, even with `--auto`
- **Report document URLs**: every response includes a direct link to the affected resource
- **Surface errors with remediation**: auth expired, permission denied, quota exceeded -- include fix suggestions

### Parallel Agents

- Dispatch a subagent to search for existing documents while the main agent plans content
- Dispatch a subagent to verify post-operation state independently
- For multi-file operations: parallelize reads across documents

### Validation

- Every mutating operation must produce a confirmable artifact: document URL, file ID, or permission confirmation
- Read operations must return non-empty content or an explicit "not found" status
- Sharing operations must confirm the permission was applied and report the recipient and access level
- If verification fails, state so explicitly and suggest manual confirmation

### Anti-Patterns / Red Flags

- Writing to documents without verifying the target file via `search` or `readGoogleDoc` first
- Changing permissions via `addPermission` without confirming recipient and access level with the user
- Assuming OAuth is still valid from a previous session -- always check `authGetStatus`
- Creating duplicate documents without searching via `search` for existing ones
- Overwriting content without showing a diff or preview first
- Deleting files or removing permissions without explicit approval, even with `--auto`

### Related Skills

- `adk-write-docs` -- local documentation authoring
- `adk-confluence` -- Confluence documentation publishing
- `adk-github` -- GitHub platform connector

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-google-drive <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-google-drive <prompt-text> --auto
```
