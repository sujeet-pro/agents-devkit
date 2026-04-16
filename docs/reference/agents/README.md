---
title: Agent Reference
description: Public ADK skills are self-contained; each skill owns its persona and workflow in its own references/ directory
order: 2
---

# Agent Reference

The public `npx skills` catalog does not depend on installing custom agents.

## Public Model

- public skills are self-contained under `skills/adk-*/`
- each skill owns its persona in `references/persona.md`
- each skill owns its workflow in `references/workflow.md`
- shared guidance (constitution, output-format, research-protocol) is copied from `ai-guidelines/` into `references/_shared/`
- the public install path does not assume Claude-only subagents or persistent project memory

## Repo Maintenance Model

For work on this repository itself:

- repo-only skill wrappers live in `.claude/skills/prj-*`, `.cursor/skills/prj-*`, and `.agents/skills/prj-*`
- canonical reusable personas live in `agent-personas/adk-*/AGENT.md`
- runtime-specific installable agent source files are generated into `agents-claude/`, `agents-cursor/`, and `agents-codex/`
- regenerate projections with `python3 scripts/generate_agent_projections.py`
- runtime-specific hook source files are generated into `hooks/`, `hooks/hooks-cursor/`, and `hooks/hooks-codex/`
- regenerate hook projections with `python3 scripts/generate_hook_projections.py`
- shared guidance mapping is defined in `ai-guidelines/shared-files-map.json`
- run `python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared` to sync shared files

## Verified Runtime Support

Custom agent support is now verified for all three major coding-agent runtimes used in ADK:

| Runtime | Install target | File format | Verified behavior |
| --- | --- | --- | --- |
| Claude Code | `.claude/agents/` | Markdown with YAML frontmatter | Native custom subagents with the richest frontmatter surface |
| Cursor | `.cursor/agents/` | Markdown with YAML frontmatter | Native custom subagents; also loads `.claude/agents/` and `.codex/agents/` for compatibility, but `.cursor/agents/` wins on conflicts |
| Codex | `.codex/agents/` | Standalone TOML | Native custom agents with config-style fields rather than Markdown frontmatter |

## Frontmatter / Schema Matrix

### Claude

Claude project subagents accept Markdown plus YAML frontmatter. Verified supported fields:

- `name`
- `description`
- `tools`
- `disallowedTools`
- `model`
- `permissionMode`
- `maxTurns`
- `skills`
- `mcpServers`
- `hooks`
- `memory`
- `background`
- `effort`
- `isolation`
- `color`
- `initialPrompt`

### Cursor

Cursor project subagents also use Markdown plus YAML frontmatter, but the supported surface is intentionally smaller:

- `name`
- `description`
- `model`
- `readonly`
- `is_background`

### Codex

Codex custom agents are TOML files rather than Markdown frontmatter. Verified required fields:

- `name`
- `description`
- `developer_instructions`

Common verified optional fields:

- `nickname_candidates`
- `model`
- `model_reasoning_effort`
- `sandbox_mode`
- `mcp_servers`
- `skills.config`

## ADK Projection Strategy

ADK keeps the actual persona prompt canonical in `agent-personas/adk-*/AGENT.md` and projects that prompt into installable runtime source files:

- `agents-claude/*.md` uses a richer Claude config surface such as explicit model selection, `skills`, `memory`, `effort`, `background`, `maxTurns`, `color`, and selective `disallowedTools` or `isolation`
- `agents-cursor/*.md` uses the full Cursor-supported field set: `name`, `description`, `model`, `readonly`, `is_background`
- `agents-codex/*.toml` uses `developer_instructions` plus model and sandbox tuning

The installer then symlinks those repo-owned source files into the real runtime target dirs under `~/.claude/agents`, `~/.cursor/agents`, and `~/.codex/agents`.

ADK deliberately does not auto-enable every Claude-only field everywhere. Fields like `memory`, `hooks`, `mcpServers`, and `initialPrompt` are powerful but have repo-side effects or environment assumptions, so they are documented and supported but only enabled when a specific agent genuinely needs them.
