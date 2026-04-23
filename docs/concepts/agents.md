---
title: Subagents
description: How ADK ships specialist subagents under the Claude plugin agents/ folder, and the supported frontmatter surface for plugin-shipped agents.
order: 4
---

# Subagents

Skills are playbooks. **Subagents** are the specialists a skill dispatches when the work is too big, too parallel, or too specialized to handle inline. The brainstorming facilitator, the code reviewer, the test engineer, and the debugger are all subagents.

The `adk` Claude Code plugin ships **one Markdown file per subagent** under `[agents/](https://github.com/sujeet-pro/agents-devkit/tree/main/agents)`, referenced from `.claude-plugin/plugin.json` as `"agents": "./agents/"`. The schema follows the [Claude Code plugins reference — Agents](https://code.claude.com/docs/en/plugins-reference#agents) section.

## Roster

10 subagents currently ship with the plugin:


| Subagent                                                                                                           | Role                                                                              |
| ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| [brainstorm-facilitator](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/brainstorm-facilitator.md) | Iterative brainstorming and route selection (paired with the brainstorming MCP) |
| [code-reviewer](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/code-reviewer.md)                   | Code review with severity-ordered findings                                        |
| [security-reviewer](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/security-reviewer.md)           | Security-focused vulnerability analysis                                           |
| [test-engineer](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/test-engineer.md)                   | Test writing, execution, and coverage                                             |
| [doc-writer](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/doc-writer.md)                         | Documentation authoring from code evidence                                        |
| [research-agent](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/research-agent.md)                 | Deep technical research with citations                                            |
| [plan-reviewer](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/plan-reviewer.md)                   | Plan critique and gap analysis                                                    |
| [implementer](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/implementer.md)                       | Focused code implementation                                                       |
| [debugger](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/debugger.md)                             | Systematic root-cause debugging                                                   |
| [dispatcher](https://github.com/sujeet-pro/agents-devkit/blob/main/agents/dispatcher.md)                         | Routes a classified task to the right downstream subagent (used by /adk:auto)   |


In Claude's `/agents` UI, these appear with the plugin namespace prefix: `adk:code-reviewer`, `adk:dispatcher`, etc.

## Frontmatter contract

Per the plugins reference, **plugin-shipped agents support a restricted set of frontmatter fields** for security reasons. ADK uses these and only these:


| Field                       | Used for                                                                      |
| --------------------------- | ----------------------------------------------------------------------------- |
| `name`                      | Required. Becomes the invocation name.                                        |
| `description`               | Required. What the agent specializes in and when Claude should invoke it.     |
| `model`                     | Pin a specific model (e.g. `claude-opus-4-7` for review-grade work).          |
| `effort`                    | `low` / `medium` / `high` reasoning budget.                                   |
| `maxTurns`                  | Hard cap on the agent's turn count.                                           |
| `tools` / `disallowedTools` | Allow- or deny-list specific tools (e.g. reviewers disable `Write`/`Edit`).   |
| `skills`                    | The ADK skills this agent may invoke.                                         |
| `memory`                    | Per-agent memory toggle.                                                      |
| `background`                | Run as a background subagent so the main conversation keeps its token budget. |
| `isolation`                 | Only `"worktree"` is supported per spec.                                      |


> [!IMPORTANT]
> The plugins reference [explicitly excludes](https://code.claude.com/docs/en/plugins-reference#agents) `hooks`, `mcpServers`, and `permissionMode` from plugin-shipped agents. ADK does not set these. The `bin/adk-validate` script catches accidental usage.

A typical ADK agent file:

```yaml
---
name: "code-reviewer"
description: "Review code for correctness, regressions, and missing validation. Use proactively after implementation, before commit, and before merge."
model: "claude-opus-4-7"
disallowedTools:
  - "Write"
  - "Edit"
maxTurns: 20
skills:
  - "review-local"
  - "review-pr"
effort: "high"
background: true
---

# Code Reviewer
...
```

## Status protocol

All ADK subagents report one of four statuses back to the calling skill:


| Status               | Meaning                                                         |
| -------------------- | --------------------------------------------------------------- |
| `DONE`               | Work complete, ready for the next phase                         |
| `DONE_WITH_CONCERNS` | Complete but with flagged issues the caller must read           |
| `NEEDS_CONTEXT`      | Missing information; caller must provide it and re-dispatch     |
| `BLOCKED`            | Cannot continue; escalate to the user or break the task smaller |


The calling skill is required to handle these statuses. It cannot silently retry a `BLOCKED` subagent or ignore `DONE_WITH_CONCERNS`.

## Subagent vs skill — when to use which


| Situation                                                       | Use                                                                                             |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Invoke a workflow end-to-end (plan → build → validate → report) | A **skill** (`/adk:build-feature`, `/adk:review-pr`, ...)                                       |
| Want a focused specialist inside a workflow                     | A **subagent** (dispatched by the skill)                                                        |
| Add a new specialist role                                       | Author one Markdown file under `agents/` and add it to the relevant skill's `agents:` allowlist |


## Claude-only

ADK's subagents (and the plugin as a whole) target Claude Code and Claude Desktop only. There is no projection into Cursor, Codex, Gemini, or other harnesses.

## Related

- [Skill Anatomy](./skill-anatomy.md) — how skills decide to dispatch a subagent.
- [Hooks](./hooks.md) — safety and lifecycle checks for both skills and subagents.
- [Plugins reference — Agents](https://code.claude.com/docs/en/plugins-reference#agents) — Anthropic's authoritative spec for plugin-shipped agents.
