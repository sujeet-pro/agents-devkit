---
name: handoff
description: "adk - [full] [handoff] Use when handing off sessions or managing persistent context threads"
user-invocable: true
argument-hint: " [--mode handoff|context-thread] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git, python3]
workflow-tier: full
maturity: stable
workflow-family: quick-action

---

# Handoff

Pause/resume work sessions and manage persistent context threads. Preserves work state for seamless resumption across sessions. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.


| Skill                     | Load When                                     | Inline Fallback                                                                                                                                                 |
| ------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/adk:workflow --family quick-action` | always | Quick Action workflow: confirm → execute → verify. For narrow tasks with single execution path. `--auto` skips confirmations. |
| `/adk:communication`      | always                                        | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context.                                              |
| `/adk:preflight-check`    | before work                                   | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP.                                                         |
| `/adk:output-format`      | when producing output                         | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question.                                                |
| `/adk:principal-engineer` | complexity >= medium                          | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months?                                                                           |
| `/adk:agentic-teams`      | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning.                               |
| `/adk:interaction`        | NOT --auto                                    | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard.                                               |


## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

### Parameters


| Parameter     | Values                          | Default     | Description                                                                                                                              |
| ------------- | ------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `--mode`      | `handoff`, `context-thread`     | auto-detect | Force a specific session mode                                                                                                            |
| `--action`    | varies by mode                  | none        | Sub-action within a mode (e.g., `pause`, `resume`, `list` for handoff; `create`, `update`, `load`, `list`, `archive` for context-thread) |
| `--name`      | `<thread-name>`                 | none        | In context-thread mode, the thread name                                                                                                  |
| `--note`      | `<text>`                        | none        | In context-thread update mode, the note to append                                                                                        |
| `--session`   | `<session-id>`                  | none        | In handoff mode, target a specific session                                                                                               |
| `--verbosity` | `short`, `standard`, `detailed` | `standard`  | Output detail level                                                                                                                      |
| `--help`      | flag                            | off         | Show this help section                                                                                                                   |


### Behavior Variations

- `**--mode handoff**`: Quick Action workflow for capturing session state, pausing work, and resuming later.
- `**--mode context-thread**`: Quick Action workflow for creating, updating, loading, listing, and archiving persistent named context threads.

### Examples

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

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the mode from the task description:


| Signal                                                                          | Mode           | Stage File                 |
| ------------------------------------------------------------------------------- | -------------- | -------------------------- |
| Pause work, hand off, context window filling up, save for later, resume         | handoff        | `stages/handoff.md`        |
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

This skill uses the Quick Action workflow: confirm → execute → verify.

### 1. Confirm

Follow the stage file's intent confirmation guidance. Always run this phase before taking action.

### 2. Execute

Follow the stage file's exploration guidance and execution instructions.

### 3. Verify

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Status line only (e.g., "Session saved to .temp/handoff/abc123.md")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus full context file listings and decision rationale

## Adjacent Skills

- `/adk:dev-build` -- feature implementation (can trigger handoff on pause)
- `/adk:plan --mode write` -- execution planning within a thread
- `/adk:code-review-pr` -- code review within a session context

