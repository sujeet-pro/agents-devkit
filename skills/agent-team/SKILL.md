---
name: agent-team
description: Use when orchestrating a complex task across multiple child agents with explicit ownership boundaries, handoff protocols, and conflict resolution
user_invocable: true
arguments:
  - name: task
    description: "High-level task description"
    required: true
  - name: team-size
    description: "Number of agents to spawn (default: auto, based on task complexity)"
    required: false
  - name: strategy
    description: "Coordination strategy: parallel, pipeline, review-loop (default: parallel)"
    required: false
---

# Team Dispatch

Use `skills/_references/agentic-teams.md` for the child-agent contract.

## Preflight

`zsh scripts/check-skill-deps.zsh agent-team`

## Overview

This skill is the "supervisor" pattern for complex tasks that require multiple agents working together. It decomposes a task into agent-sized work items, assigns roles, manages handoffs, and resolves conflicts.

## Phase 1: Task Decomposition

1. Analyze the task to identify independent work streams
2. Map each stream to a standard team shape from `skills/_references/agentic-teams.md` or define custom roles
3. Identify dependencies between streams (which must complete before others can start)
4. Create a coordination plan in `.temp/plans/team-<timestamp>.md`

## Phase 2: Agent Assignment

For each work stream, define:

```markdown
### Agent: <role-name>
- **Task**: <specific deliverable>
- **Inputs**: <what this agent needs>
- **Outputs**: <what this agent produces>
- **Constraints**: <boundaries — what NOT to touch>
- **Dependencies**: <which agents must complete first>
- **Tools needed**: <MCP servers, CLI tools>
```

## Phase 3: Dispatch

### Parallel Strategy (default)
- Launch all independent agents simultaneously
- Each agent receives full context for its task, not fragments
- Agents that depend on others wait for predecessor completion
- Monitor for conflicts (two agents trying to edit the same file)

### Pipeline Strategy
- Agents execute in sequence, each receiving the previous agent's output
- Use when tasks have strict ordering requirements
- Example: research → design → implement → review

### Review-Loop Strategy
- Implementation agent produces work
- Review agent checks it
- If issues found, implementation agent fixes
- Loop until review passes (max 3 iterations before escalating to user)

## Phase 4: Conflict Resolution

When agents produce conflicting outputs:

1. **File conflicts**: If two agents edit the same file, the agent with the more specific scope wins. Present the conflict to the user if unclear.
2. **Design conflicts**: Use `consensus-agent` to merge perspectives. Preserve minority views.
3. **Scope creep**: If an agent drifts outside its assigned boundaries, discard the out-of-scope work and note it for the user.

## Phase 5: Integration

1. Collect outputs from all agents
2. Verify no conflicts or regressions
3. Run integration verification (lint, test, build) if applicable
4. Present unified result to the user

## Platform Adaptation

- **Claude Code**: Use Agent tool with `run_in_background` for parallel dispatch
- **Codex**: Use child agents with full context
- **Gemini CLI**: Use native agents or sequential role-based passes
- **Cursor**: Stay inside Cursor, use built-in agent/model capabilities only
- **OpenCode**: Use built-in agent features; fall back to sequential if no parallel support

## Output

```markdown
## Team Dispatch Summary

### Task
<original task description>

### Team Composition
| Agent | Role | Status | Duration |
|-------|------|--------|----------|
| agent-1 | <role> | completed | Xs |
| agent-2 | <role> | completed | Xs |

### Results
<integrated output from all agents>

### Conflicts Resolved
<any conflicts and how they were resolved>

### Open Items
<anything that needs human decision>
```
