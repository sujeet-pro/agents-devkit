---
title: Project Management
description: Initialize projects, manage milestones, hand off sessions, and coordinate agent teams
order: 7
---

# Project Management

ADK includes skills for project lifecycle management — from initializing a new project to managing milestones, capturing ideas, handing off sessions, and coordinating multi-agent teams.

## Scenarios

- [Initialize a new project](#initialize-a-new-project)
- [Manage milestones](#manage-milestones)
- [Capture ideas](#capture-ideas)
- [Hand off a session](#hand-off-a-session)
- [Resume a session](#resume-a-session)
- [Use context threads](#use-context-threads)
- [Coordinate agent teams](#coordinate-agent-teams)

---

## Initialize a New Project

Use `project` to scaffold a new project with documentation and configuration:

```text
/adk:project --mode init
```

### Specify project type

```text
/adk:project --mode init --type api
/adk:project --mode init --type library
/adk:project --mode init --type cli
```

---

## Manage Milestones

Track and manage project milestones:

```text
/adk:project --mode milestone --action create "v1.0 Release" --milestone Q3-2025
/adk:project --mode milestone --action list
/adk:project --mode milestone --action update --milestone Q3-2025
```

---

## Capture Ideas

Quick-capture ideas into a backlog:

```text
/adk:project --mode idea "add dark mode support"
/adk:project --mode idea --action list
```

Idea mode uses an abbreviated workflow — no planning or approval needed.

---

## Hand Off a Session

When you need to pause work and resume later (or pass it to another session), use `handoff`:

```text
/adk:handoff --mode handoff
```

This captures:

- Current progress and completed tasks
- Pending work and blockers
- File changes and branch state
- Context needed for resumption

### Add a note

```text
/adk:handoff --mode handoff --note "auth module 80% complete, blocked on OAuth provider config"
```

---

## Resume a Session

Resume a previously handed-off session:

```text
/adk:handoff --mode handoff --action resume
```

ADK detects previous handoff artifacts and restores context.

### Resume a specific session

```text
/adk:handoff --mode handoff --action resume --session auth-implementation
```

---

## Use Context Threads

Context threads are named, persistent context bundles that can be updated and referenced across sessions:

### Create a thread

```text
/adk:handoff --mode context-thread --action create --name "api-redesign"
```

### Update a thread

```text
/adk:handoff --mode context-thread --action update --name "api-redesign" --note "completed endpoint design, starting implementation"
```

### List threads

```text
/adk:handoff --mode context-thread --action list
```

---

## Coordinate Agent Teams

Use `team` to dispatch work across multiple agents or models.

### Multi-model comparison

Run the same task across multiple models and merge results:

```text
/adk:team --mode multi --strategy merge "review this authentication implementation"
/adk:team --mode multi --strategy vote "which caching strategy is best for our use case?"
/adk:team --mode multi --strategy best-of "write unit tests for the payment module"
```

Strategies:
- `merge` — combine outputs from all models
- `vote` — majority-wins for decisions
- `best-of` — pick the highest-quality output

### Specialized agent team

Dispatch a team of agents with distinct roles:

```text
/adk:team --mode team --roles "security-reviewer,performance-analyst,api-designer" review the new API design
```

### Timeout control

```text
/adk:team --mode multi --timeout 120 complex analysis task
```

---

## Which Skill to Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Initialize project | `project` | `--mode init`, `--type` |
| Create/track milestones | `project` | `--mode milestone`, `--action` |
| Capture ideas | `project` | `--mode idea` |
| Pause and hand off | `handoff` | `--mode handoff`, `--note` |
| Resume work | `handoff` | `--action resume`, `--session` |
| Persistent context | `handoff` | `--mode context-thread`, `--name` |
| Multi-model comparison | `team` | `--mode multi`, `--strategy` |
| Agent team dispatch | `team` | `--mode team`, `--roles` |

## Related Skills

- **[`plan`](/reference/skill-plan/)** — create implementation plans for milestone work
- **[`dev-build`](/reference/skill-dev-build/)** — execute development tasks
- **[`use`](/reference/skill-use/)** — route any task through the orchestrator
