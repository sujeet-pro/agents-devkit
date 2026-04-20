---
title: Custom Subagents (per provider)
description: How ADK ships custom subagents independently for Claude, Cursor, and Codex.
order: 4
---

# Custom Subagents (per provider)

Skills are playbooks. **Custom subagents** are the specialists a skill dispatches when the work is too big, too parallel, or too specialized to handle inline. The brainstorming facilitator, the code reviewer, the test engineer, and the debugger are all subagents.

ADK ships subagent definitions independently per provider. There is **no shared canonical source**. Each runtime's folder is the source of truth for its own files because each harness supports a different schema and a different feature surface.

## Roster

These are the subagents currently shipped (lists may grow or differ per provider over time):

| Subagent | Role |
| --- | --- |
| `adk-brainstorm-facilitator` | Iterative brainstorming and route selection |
| `adk-code-reviewer` | Code review with severity-ordered findings |
| `adk-security-reviewer` | Security-focused vulnerability analysis |
| `adk-test-engineer` | Test writing, execution, and coverage |
| `adk-doc-writer` | Documentation authoring from code evidence |
| `adk-research-agent` | Deep technical research with citations |
| `adk-plan-reviewer` | Plan critique and gap analysis |
| `adk-implementer` | Focused code implementation |
| `adk-debugger` | Systematic root-cause debugging |

Each subagent declares its mission, scope, hard rules, output format, and anti-patterns inside its file.

## Status protocol

All subagents report one of four statuses back to the calling skill:

| Status | Meaning |
| --- | --- |
| `DONE` | Work complete, ready for the next phase |
| `DONE_WITH_CONCERNS` | Complete but with flagged issues the caller must read |
| `NEEDS_CONTEXT` | Missing information; caller must provide it and re-dispatch |
| `BLOCKED` | Cannot continue; escalate to the user or break the task smaller |

The calling skill is required to handle these statuses. It cannot silently retry a `BLOCKED` subagent or ignore `DONE_WITH_CONCERNS`.

## Per-provider files

The same subagent name (`adk-implementer`, etc.) appears in three independent files when supported by all three providers:

- [`agents-claude/<name>.md`](https://github.com/sujeet-pro/agents-devkit/tree/main/agents-claude) — Markdown with Claude-flavored YAML frontmatter
- [`agents-cursor/<name>.md`](https://github.com/sujeet-pro/agents-devkit/tree/main/agents-cursor) — Markdown with Cursor-flavored YAML frontmatter
- [`agents-codex/<name>.toml`](https://github.com/sujeet-pro/agents-devkit/tree/main/agents-codex) — standalone TOML

Each file is fully self-contained: frontmatter (or TOML keys) plus the body inlined. Edit the file in the provider's folder; nothing propagates anywhere else.

### Claude

Claude Code custom subagents accept Markdown with rich YAML frontmatter. Verified fields include:

`name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`.

ADK uses this surface to pin a model, declare which skills the subagent may invoke, enable `memory`, set `effort`, and hint UI color.

### Cursor

Cursor custom subagents use Markdown with a much smaller frontmatter:

`name`, `description`, `model`, `readonly`, `is_background`.

`readonly: true` is how a reviewer subagent signals it will not write files. `is_background: true` moves the subagent into a background slot so the main conversation keeps its token budget.

### Codex

Codex custom agents are TOML files, not Markdown. Required:

`name`, `description`, `developer_instructions`.

Common optional fields: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`.

Codex wraps the body inside a `developer_instructions = """..."""` block. It uses `sandbox_mode` to pick read-only vs workspace-write behavior.

## Why independent per provider

Forcing a single canonical source through a projection script meant either lossy projections (drop fields not supported everywhere) or an awkward extension model. The independent-per-provider model:

- Lets each runtime use the full surface its harness provides.
- Removes auto-propagation drift.
- Makes it easy to omit a subagent in a runtime that does not benefit from it.
- Matches the standalone-skill contract used elsewhere in this repo.

The trade-off: if you want the same persona text in all three providers, you have to update three files. That is a deliberate cost.

## Install

`adk-install` symlinks each chosen subagent file into the runtime's agents directory:

- `agents-claude/<name>.md` → `<root>/.claude/agents/<name>.md`
- `agents-cursor/<name>.md` → `<root>/.cursor/agents/<name>.md`
- `agents-codex/<name>.toml` → `<root>/.codex/agents/<name>.toml`

Re-runs prune stale links and recreate the currently-selected ones.

## Subagent vs skill — when to use which

| Situation | Use |
| --- | --- |
| Invoke a workflow end-to-end (plan → build → validate → report) | A **skill** (`/adk-build-feature`, `/adk-review-pr`, ...) |
| Want a focused specialist inside a workflow | A **subagent** (dispatched by the skill) |
| Add a new specialist role | Author the file in each provider's folder you want to support |

## Related

- [Skill Anatomy](./skill-anatomy.md) — how skills decide to dispatch a subagent.
- [Hooks](./hooks.md) — safety and lifecycle checks for both skills and subagents.
- [Agent Reference](../reference/agents/) — per-provider format cheat-sheet.
