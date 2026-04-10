---
title: Project Management
description: Initialize projects, manage milestones, hand off sessions, and coordinate agent teams
order: 7
---

# Project Management

The project-management skills help when the work is bigger than a single code change: starting new efforts, shaping milestones, parking ideas, preserving context between sessions, or coordinating parallel agent work.

> **Quick start:** `/adk:project <prompt-text>` is the best starting point when you want to bootstrap a project or shape roadmap work.

## Scenarios

- [Start Or Shape A Project](#start-or-shape-a-project)
- [Manage Milestones And Ideas](#manage-milestones-and-ideas)
- [Hand Off Or Resume Work](#hand-off-or-resume-work)
- [Coordinate Agent Teams](#coordinate-agent-teams)

---

## Start Or Shape A Project

Use `project` when the output should be a project artifact: a bootstrap plan, an initialized project direction, a roadmap milestone, or an idea captured for later work.

```text
/adk:project <prompt-text>
/adk:project bootstrap a new CLI tool for managing dotfiles
/adk:project --mode init <prompt-text>
```

The plain invocation is usually enough because the skill can infer whether you are starting a project or talking about the roadmap.

---

## Manage Milestones And Ideas

Use the explicit project modes when you already know whether the work is milestone management or idea capture.

```text
/adk:project --mode milestone --action create <prompt-text>
/adk:project --mode milestone --action track
/adk:project --mode milestone --action audit
/adk:project --mode idea <prompt-text>
/adk:project --mode idea --action review
```

Milestone mode is for roadmap work that already belongs to the execution track. Idea mode is for backlog parking-lot work that is not ready for specs or plans yet.

---

## Hand Off Or Resume Work

Use `handoff` when continuity is the main problem rather than the task itself.

```text
/adk:handoff --mode handoff
/adk:handoff --mode handoff --note <prompt-text>
/adk:handoff --mode handoff --action resume
/adk:handoff --mode handoff --action resume --session <session-name>
/adk:handoff --mode context-thread --action create --name <name>
/adk:handoff --mode context-thread --action update --name <name> --note <prompt-text>
```

Use handoff mode for pause/resume between sessions, and context-thread mode when you want a named stream of persistent project context that can be updated over time.

---

## Coordinate Agent Teams

Use `team` when the work itself should be parallelized across multiple models or multiple specialized agents.

```text
/adk:team <prompt-text>
/adk:team --mode multi --strategy merge <prompt-text>
/adk:team --mode multi --strategy vote <prompt-text>
/adk:team --mode team --roles <name> <prompt-text>
/adk:team --mode multi --timeout 120 <prompt-text>
```

Multi mode compares or merges multiple model runs of the same task. Team mode is for explicit role-based decomposition when different agents should own different slices of the work.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Bootstrap or shape a project | `project` | `<prompt-text>`, `--mode init` |
| Manage milestones or capture ideas | `project` | `--mode milestone`, `--mode idea`, `--action` |
| Pause, resume, or preserve context | `handoff` | `--mode`, `--action`, `--note`, `--session` |
| Compare models or dispatch agent teams | `team` | `<prompt-text>`, `--mode`, `--strategy`, `--roles`, `--timeout` |

## Related Skills

- **[`plan`](/reference/skill-plan/)** when a milestone or idea becomes concrete execution work.
- **[`spec`](/reference/skill-spec/)** when the next artifact should be a durable requirements document.
- **[`dev-build`](/reference/skill-dev-build/)** when planning is done and implementation should start.
