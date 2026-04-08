---
title: "handoff"
description: Session handoff and persistent context threads
skill_name: handoff
category: task
workflow_tier: full
---

# handoff

Pauses and resumes work sessions, and manages named context threads that persist across sessions.

## When to Use

- Pause work and capture context for later resumption
- Pass work to another session or collaborator
- Maintain persistent context bundles across sessions

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `handoff`, `context-thread` | `handoff` | Operation mode |
| `--action` | mode-specific | — | Sub-action (e.g., `resume`, `create`, `list`, `update`) |
| `--name` | thread name | — | Context thread name |
| `--note` | free text | — | Additional context note |
| `--session` | session ID | — | Target session for resume |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Workflow

Abbreviated — phases 2–5 skipped for most operations.

| Phase | Action |
|-------|--------|
| 0. Intent | Detect mode and action |
| 1. Research | Read current progress, file state, branch state |
| 4. Execute | Capture/restore context |
| 5. Validate | Verify handoff/thread operation |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `interaction`.

## Examples

```text
/adk:handoff
/adk:handoff --note "auth module 80% complete"
/adk:handoff --mode handoff --action resume
/adk:handoff --mode handoff --action resume --session auth-implementation
/adk:handoff --mode context-thread --action create --name "api-redesign"
/adk:handoff --mode context-thread --action update --name "api-redesign" --note "endpoints done"
/adk:handoff --mode context-thread --action list
```
