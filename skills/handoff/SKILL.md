---

## name: adk-handoff
description: "adk - [full] [handoff] Use when handing off sessions or managing persistent context threads"
user-invocable: true
argument-hint: " [--mode handoff|context-thread] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full

# Handoff

Pause/resume work sessions and manage persistent context threads. Preserves work state for seamless resumption across sessions. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.


| Skill                     | Load When                                     | Inline Fallback                                                                                                                                                 |
| ------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/adk:workflow`           | always                                        | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. `--auto` skips confirmations. |
| `/adk:communication`      | always                                        | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context.                                              |
| `/adk:preflight-check`    | before work                                   | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP.                                                         |
| `/adk:output-format`      | when producing output                         | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question.                                                |
| `/adk:principal-engineer` | complexity >= medium                          | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months?                                                                           |
| `/adk:agentic-teams`      | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning.                               |
| `/adk:interaction`        | NOT --auto                                    | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard.                                               |


## Reference Loading

Load reference files conditionally to minimize token usage:


| Reference                    | Load When                                             |
| ---------------------------- | ----------------------------------------------------- |
| `workflow-6phase.md`         | always (read only the section for the current phase)  |
| `communication-style.md`     | always                                                |
| `preflight.md`               | before preflight check                                |
| `output-formats.md`          | when producing final output                           |
| `output-format-modes.md`     | when producing final output                           |
| `principal-engineer.md`      | Phase 0, complexity >= medium                         |
| `agentic-teams.md`           | Phase 4, when launching child agents                  |
| `inline-interaction.md`      | interactive phases, NOT --auto                        |
| `help-format.md`             | when --help is passed                                 |
| `project-guidelines.md`      | Phase 1, when scanning project                        |
| `review-pipeline.md`         | review skills only                                    |
| `review-comment-template.md` | when posting review comments                          |
| `source-routing.md`          | when target is external (PR, Confluence, Google Docs) |


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

- `**--mode handoff**`: Abbreviated workflow for capturing session state, pausing work, and resuming later. Phases 2-5 skipped.
- `**--mode context-thread**`: Abbreviated workflow for creating, updating, loading, listing, and archiving persistent named context threads. Phases 2-5 skipped.

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

All modes share the 6-phase workflow from `/adk:workflow`. Each stage file defines which phases apply and what to do in each.

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

- `/adk:dev-build` -- feature implementation (can trigger handoff on pause)
- `/adk:plan --mode write` -- execution planning within a thread
- `/adk:code-review-pr` -- code review within a session context

