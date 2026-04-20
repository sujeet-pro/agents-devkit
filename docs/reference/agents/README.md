---
title: Agent Reference
description: How ADK custom subagents are authored independently per provider (Claude / Cursor / Codex).
order: 2
---

# Agent Reference

Reference for how ADK ships **custom subagents** for each runtime. There is no shared "canonical persona" anymore — every provider's agent files live in their own folder and are independently authored.

## Per-provider folders

```
agents-claude/
├── adk-brainstorm-facilitator.md
├── adk-code-reviewer.md
├── adk-debugger.md
├── adk-doc-writer.md
├── adk-implementer.md
├── adk-plan-reviewer.md
├── adk-research-agent.md
├── adk-security-reviewer.md
└── adk-test-engineer.md

agents-cursor/
├── adk-brainstorm-facilitator.md
├── adk-code-reviewer.md
├── adk-debugger.md
├── adk-doc-writer.md
├── adk-implementer.md
├── adk-plan-reviewer.md
├── adk-research-agent.md
├── adk-security-reviewer.md
└── adk-test-engineer.md

agents-codex/
├── adk-brainstorm-facilitator.toml
├── adk-code-reviewer.toml
├── adk-debugger.toml
├── adk-doc-writer.toml
├── adk-implementer.toml
├── adk-plan-reviewer.toml
├── adk-research-agent.toml
├── adk-security-reviewer.toml
└── adk-test-engineer.toml
```

Each file is fully self-contained: frontmatter (or TOML keys) plus the persona body inlined. Edit the file in the provider's folder; nothing propagates anywhere else.

## Why independent per provider

Different harnesses support different agent capabilities. Claude exposes `model`, `isolation`, `color`, tool-permission lists; Cursor's frontmatter is smaller; Codex uses TOML with `developer_instructions = """..."""` and reasoning-effort fields. Forcing a single source through a projection script meant either lossy projections or an awkward extension model. The independent-per-provider model lets each runtime use the full surface its harness provides.

Lists may differ per provider — a runtime that does not support custom agents simply does not get an entry.

## Frontmatter / TOML cheat-sheet

### Claude (`agents-claude/<name>.md`)

```yaml
---
name: adk-implementer
description: Implement the smallest correct change from an approved plan.
model: claude-sonnet-4-6
maxTurns: 30
memory: local
effort: medium
isolation: worktree
color: cyan
---
```

### Cursor (`agents-cursor/<name>.md`)

```yaml
---
name: "adk-code-reviewer"
description: "Review code for correctness, regressions, and missing validation."
model: "inherit"
readonly: true
is_background: true
---
```

### Codex (`agents-codex/<name>.toml`)

```toml
name = "adk-implementer"
description = "Implement the smallest correct change from an approved plan."
model = "gpt-5.3-codex-spark"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"
nickname_candidates = ["Builder", "Patch", "Forge"]
developer_instructions = """
# Implementer
...
"""
```

## Install

`adk-install` symlinks each chosen file into the runtime's agents directory:

- `agents-claude/<name>.md` → `<root>/.claude/agents/<name>.md`
- `agents-cursor/<name>.md` → `<root>/.cursor/agents/<name>.md`
- `agents-codex/<name>.toml` → `<root>/.codex/agents/<name>.toml`

Re-running prunes stale links and recreates only the currently-selected agents.
