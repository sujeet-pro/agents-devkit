---
name: session-handoff
description: "Use when you need to pause work and resume in a new session with full context reconstruction, or when context window is filling up"
user_invocable: true
arguments:
  - name: action
    description: "Action: pause, resume, list (default: pause)"
    required: false
  - name: session
    description: "Session ID to resume (for action=resume)"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
---

# Session Handoff

Use `skills/_references/preflight-validations.md`.

Preserve work state when sessions must end — whether the context window is filling up, work is paused for the day, or a different task takes priority. Enables seamless resumption in a new session.

## Preflight

Before creating or resuming a handoff, run:

`zsh scripts/check-skill-deps.zsh session-handoff`

## Handoff Storage

Save handoffs to `.temp/handoff/<session-id>.md` in the current working directory. If `.temp/` does not exist, create it and ensure it is listed in `.gitignore`.

Use this handoff file format:

```markdown
---
session_id: <short-id>
created: <ISO-8601>
status: paused | completed
branch: <current git branch>
plan: <path to active plan if any>
skill: <skill that was active>
---

# Session Handoff: <brief description>

## Completed Work
- <what was finished, with file paths>

## In Progress
- <what was mid-flight, what state it's in>

## Remaining Work
- <what still needs to be done>

## Key Decisions Made
- <decision 1>: <rationale>
- <decision 2>: <rationale>

## Blocked Items
- <blocker 1>: <what's needed to unblock>

## Context Files
- <file paths the next session should read first>

## Git State
- Branch: <branch name>
- Last commit: <sha and message>
- Uncommitted changes: <description or "none">
```

## Pause Flow

1. **Capture state**: scan the conversation for completed work, in-progress items, remaining tasks, decisions, and blockers.
2. **Check for active plans**: if a `.temp/plans/*.md` file has unchecked tasks, link to it.
3. **Check git state**: capture branch, last commit, uncommitted changes.
4. **Interactive review**: present the handoff for user approval:

```text
## Session Handoff Draft

Completed: N items
In Progress: N items
Remaining: N items
Decisions: N captured
Blockers: N items

Action: [A]pprove & save | [E]dit | [A]dd more context
```

In `auto-approve` mode, save immediately without waiting for confirmation.

5. **Save**: write the handoff file to `.temp/handoff/<session-id>.md`.
6. **Remind**: suggest committing uncommitted changes before ending the session.

## Resume Flow

1. **Find handoff**: if `session` is provided, load that specific handoff. Otherwise, find the most recent `paused` handoff in `.temp/handoff/`.
2. **Present context**: display the handoff summary:

```text
## Resuming Session: <description>

Created: <date>
Branch: <branch>
Plan: <linked plan or "none">

Completed: <summary>
In Progress: <summary>
Next steps: <summary>
Blockers: <summary>

Action: [C]ontinue from where left off | [R]eview all context | [S]tart fresh (keep notes)
```

3. **Reconstruct context**: read the context files listed in the handoff.
4. **Resume plan**: if a plan is linked, load it and find the first unchecked task.
5. **Update handoff**: mark as `status: completed` when work finishes.

## List Flow

Display all handoffs with status:

```text
## Active Handoffs

| ID | Date | Branch | Status | Description |
|----|------|--------|--------|-------------|
| <id> | <date> | <branch> | paused | <description> |
```

## Adjacent Skills

- `/devkit:plan-execute` for resuming plan execution (has built-in pause support)
- `/devkit:context-thread` for persistent cross-session context
- `/devkit:dev-implement` for feature implementation (can trigger handoff on pause)
