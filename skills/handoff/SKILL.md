---
name: handoff
description: "[full] [handoff] Use when handing off sessions or managing persistent context threads"
user-invocable: true
argument-hint: "<action> [--mode handoff|context-thread] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Handoff

Pause/resume work sessions and manage persistent context threads. Preserves work state for seamless resumption across sessions. Auto-detects the right mode from context, or accepts an explicit `--mode`.

Load references: `references/workflow-6phase.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`. For Medium/Large: also load `references/agentic-teams.md`, `references/principal-engineer.md`.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `handoff`, `context-thread` | auto-detect | Force a specific session mode |
| `--action` | varies by mode | none | Sub-action within a mode (e.g., `pause`, `resume`, `list` for handoff; `create`, `update`, `load`, `list`, `archive` for context-thread) |
| `--name` | `<thread-name>` | none | In context-thread mode, the thread name |
| `--note` | `<text>` | none | In context-thread update mode, the note to append |
| `--session` | `<session-id>` | none | In handoff mode, target a specific session |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Behavior Variations

- **`--mode handoff`**: Abbreviated workflow for capturing session state, pausing work, and resuming later. Phases 2-5 skipped.
- **`--mode context-thread`**: Abbreviated workflow for creating, updating, loading, listing, and archiving persistent named context threads. Phases 2-5 skipped.

### Examples

```
/handoff save my work for later
/handoff --mode handoff pause
/handoff --mode handoff resume
/handoff --mode context-thread --action create --name auth-refactor
/handoff --mode context-thread --action update --name auth-refactor --note "completed token validation"
/handoff --mode context-thread --action load --name auth-refactor
/handoff --mode context-thread --action list
/handoff --mode context-thread --action archive --name auth-refactor
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the mode from the task description:

| Signal | Mode | Stage File |
|---|---|---|
| Pause work, hand off, context window filling up, save for later, resume | handoff | `stages/handoff.md` |
| Named context threads, ongoing work streams, create/update/list/archive threads | context-thread | `stages/context-thread.md` |

### Resume Detection

When the user says "save context" or "resume":
- Check `.temp/threads/` for a named thread matching `--name`
- If a matching thread exists, load the context-thread stage with `--action load`
- Otherwise, load the handoff stage

### Disambiguation

If intent is unclear, ask one clarifying question:

```text
Are you looking to:
[H] Hand off this session for later (one-time snapshot)
[T] Manage a persistent named thread (ongoing work stream)
```

After selecting the mode, load the corresponding stage file and follow its instructions.

## Common Phases

All modes share the 6-phase workflow from `references/workflow-6phase.md`. Each stage file defines which phases apply and what to do in each.

### Phase 0: Intent Expansion

Follow the stage file's intent confirmation guidance. Always run this phase before taking action.

### Phase 1: Research & Options

Follow the stage file's exploration guidance. Every mode uses this phase, though simpler modes may keep it brief.

### Phase 2: Approach Selection

Most handoff work skips this phase after intent confirmation unless the user must choose a resume strategy.

### Phase 3: Planning

Most handoff work skips this phase after approval unless the session needs an explicit recovery plan.

### Phase 4: Execute

Follow the stage file's execution instructions.

### Phase 5: Validate & Learn

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Status line only (e.g., "Session saved to .temp/handoff/abc123.md")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus full context file listings and decision rationale

## Adjacent Skills

- `/develop` -- feature implementation (can trigger handoff on pause)
- `/plan --mode write` -- execution planning within a thread
- `/review` -- code review within a session context
