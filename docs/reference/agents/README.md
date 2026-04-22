---
title: 'Agents'
description: 'Subagent personas used by the adk plugin (Claude Code).'
---

# Agents

Claude Code subagents that ship with the `adk` plugin. Each is a persona with a fixed model, allowed tools, and a curated set of skills it loads.

## How to use

Invoke a subagent directly in Claude Code:

```text
/agent <name>
```

Most agents are invoked automatically by `@adk:auto` (a.k.a. `adk-auto`) via the [`dispatcher`](./dispatcher.md) — you rarely call them by hand.

## Roster

- [`brainstorm-facilitator`](./brainstorm-facilitator.md)
- [`code-reviewer`](./code-reviewer.md)
- [`debugger`](./debugger.md)
- [`dispatcher`](./dispatcher.md)
- [`doc-writer`](./doc-writer.md)
- [`implementer`](./implementer.md)
- [`plan-reviewer`](./plan-reviewer.md)
- [`research-agent`](./research-agent.md)
- [`security-reviewer`](./security-reviewer.md)
- [`test-engineer`](./test-engineer.md)

## Source

`agents/<role>.md` — markdown + YAML frontmatter.
