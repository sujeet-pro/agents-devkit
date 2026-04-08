---
title: "handoff"
description: Session pause/resume and persistent named context threads
skill_name: handoff
category: task
workflow_tier: full
user_invocable: true
---

# handoff

Pause and resume work sessions or manage persistent named context threads. Preserves work state for seamless resumption across sessions. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## When to Use

- Save current session state before context window fills up
- Hand off work for later resumption in a new session
- Create a persistent named context thread for an ongoing work stream
- Update a context thread with progress notes
- Load a previous context thread to resume work
- List or archive context threads

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--mode` | `handoff`, `context-thread` | auto-detect | Force a specific session mode |
| `--action` | varies by mode | none | Sub-action within a mode (e.g., `pause`, `resume`, `list` for handoff; `create`, `update`, `load`, `list`, `archive` for context-thread) |
| `--name` | `<thread-name>` | none | In context-thread mode, the thread name |
| `--note` | `<text>` | none | In context-thread update mode, the note to append |
| `--session` | `<session-id>` | none | In handoff mode, target a specific session |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip all confirmations and approval gates |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Handoff mode** (`--mode handoff`) | Abbreviated workflow for capturing session state, pausing work, and resuming later. Phases 2-5 skipped |
| **Context-thread mode** (`--mode context-thread`) | Abbreviated workflow for creating, updating, loading, listing, and archiving persistent named context threads. Phases 2-5 skipped |
| **Auto-detection** (no `--mode`) | Detects mode from context: "pause/hand off/save for later/resume" → handoff; "named threads/create thread/update thread" → context-thread |
| **Resume detection** | Checks `.temp/threads/` for a named thread matching `--name`; if found, loads the context-thread stage with `--action load` |
| `--verbosity short` | Status line only (e.g., "Session saved to .temp/handoff/abc123.md") |
| `--verbosity detailed` | Full context file listings and decision rationale |

## Key Behaviors

- **Smart mode detection**: infers mode from prompt keywords (pause/hand off/save for later → handoff; named threads/create thread → context-thread)
- **Resume detection**: automatically checks `.temp/threads/` for matching threads when user says "resume" or "save context"
- **Disambiguation prompt**: when intent is unclear, asks whether the user wants a one-time snapshot (handoff) or a persistent named thread (context-thread)
- **Stage-driven execution**: each mode loads its own stage file (`stages/handoff.md`, `stages/context-thread.md`)
- **Persistent storage**: handoff snapshots and context threads are saved to `.temp/` for cross-session durability

## Workflow

Both modes use abbreviated workflow — phases 2-5 are typically skipped after intent confirmation.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal and detect mode (handoff or context-thread) |
| 1. Research & Options | yes | Brief context analysis; check for existing threads/sessions |
| 2. Approach Selection | skip | Most handoff work skips this unless user must choose a resume strategy |
| 3. Planning | skip | Most handoff work skips this unless session needs an explicit recovery plan |
| 4. Execute | yes | Follow stage file execution instructions |
| 5. Validate & Learn | yes | Summary of what changed and what the user should know |

## Mode Detection

| Signal | Mode | Stage |
|--------|------|-------|
| Pause work, hand off, context window filling up, save for later, resume | handoff | `stages/handoff.md` |
| Named context threads, ongoing work streams, create/update/list/archive threads | context-thread | `stages/context-thread.md` |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect source, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

All output is markdown. Format varies by mode and is defined in each stage file. Verbosity adapts per `--verbosity`:

- **short**: Status line only (e.g., "Session saved to .temp/handoff/abc123.md")
- **standard**: Full structured output from the stage file
- **detailed**: Standard output plus full context file listings and decision rationale

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:dev-build` | Feature implementation (can trigger handoff on pause) |
| `/adk:plan --mode write` | Execution planning within a thread |
| `/adk:code-review-pr` | Code review within a session context |

## Examples

```
/adk:handoff save my work for later
/adk:handoff --mode handoff pause
/adk:handoff --mode handoff resume
/adk:handoff --mode context-thread --action create --name auth-refactor
/adk:handoff --mode context-thread --action update --name auth-refactor --note "completed token validation"
/adk:handoff --mode context-thread --action load --name auth-refactor
/adk:handoff --mode context-thread --action list
/adk:handoff --mode context-thread --action archive --name auth-refactor
```
