# Skill Architecture

## Goal

Separate:

- public installable skills
- reusable agent personas
- lifecycle hooks
- MCP server configurations
- composable workflows
- repo-only maintenance skills
- shared source-of-truth guidance
- compatibility-only runtime shims

## Surfaces


| Surface | Purpose | Rules |
| --- | --- | --- |
| `skills/adk-*` | Published skills installed with `npx skills` | Self-contained. Low-arg. User-facing. |
| `agent-personas/adk-*` | Canonical reusable agent personas | Focused role. Hard rules. Output format. |
| `agents-claude/`, `agents-cursor/`, `agents-codex/` | Generated runtime-specific agent install sources | Never edit by hand. Generated from canonical personas. |
| `hooks/` | Lifecycle hooks for agent sessions | Safety and validation. |
| `mcp-config/` | MCP server configurations | Per-server JSON. Install scripts. |
| `workflows/` | Composable multi-skill pipelines | YAML. Sequential steps. |
| `.claude/skills/prj-*` | Repo-only Claude maintenance skills | Thin wrappers to `ai-guidelines/`. |
| `.cursor/skills/prj-*` | Repo-only Cursor maintenance skills | Thin wrappers to `ai-guidelines/`. |
| `.agents/skills/prj-*` | Repo-only Codex/OpenCode maintenance skills | Thin wrappers to `ai-guidelines/`. |
| `.codex/` | Compatibility output only | Never the canonical source. |
| `ai-guidelines/` | Shared source of truth | Author here first. |


## Published Skill Contract

- Directory name matches frontmatter `name`.
- Name must start with `adk-`.
- Each published skill must stand alone when copied out of this repo.
- Each published skill may contain:
  - `SKILL.md`
  - `references/`
  - `scripts/`
  - optional `assets/`
- Each published skill must carry the local copies it needs for:
  - constitution
  - shared brainstorming workflow
  - research method
  - validation bar
  - task-specific workflow
  - task-specific persona
- Published skills must not rely on helper skills being separately installed.
- Published skills may prefer a workflow-specific MCP server, but only when the skill also defines explicit warning and fallback behavior.
- Published skills should keep arguments narrow enough that a user can remember them without a cheatsheet.
- Each skill must define a customized workflow that suits its specific task.
- Skills should dispatch subagents for non-trivial validation and review.

## Agent Persona Contract

- Directory name matches the agent purpose with `adk-` prefix.
- Each agent persona lives in `agent-personas/adk-*/AGENT.md`.
- Agent personas define: mission, scope, hard rules, output format, anti-patterns.
- Runtime-native custom agent projections are generated from each canonical persona into installable source files under `agents-claude/`, `agents-cursor/`, and `agents-codex/`.
- Agent personas are dispatched by skills as subagents for focused work.
- Agent personas are reusable across multiple skills.

## Project Skill Contract

- Project-only skills are for maintaining this repository.
- Project-only skill names must start with `prj-`.
- They may point directly to `ai-guidelines/` files.
- They should stay thin and readable.
- They should not duplicate long shared text.
- They may reference local repo scripts and docs generation flows.

## Compatibility Matrix


| Runtime | Preferred Project Surface | Notes |
| --- | --- | --- |
| Claude Code | `.claude/skills/` plus `CLAUDE.md` | Skills, custom agents, and hooks. ADK stores installable Claude agent sources under `agents-claude/` and symlinks them into `.claude/agents/`. |
| Cursor | `.cursor/skills/`, `.cursor/rules/`, and `.cursor/agents/` plus `AGENTS.md` | Skills and custom subagents. ADK stores installable Cursor agent sources under `agents-cursor/` and symlinks them into `.cursor/agents/`. |
| Codex / OpenAI | `AGENTS.md` plus `.agents/skills/`, `.codex/skills/`, and `.codex/agents/` | Skills via `.codex/skills/` or `.agents/skills/`; custom agents use TOML instead of Markdown frontmatter and are sourced from `agents-codex/`. |
| Gemini CLI | `GEMINI.md` with `@./` imports | Modular root-level skill files. |
| Antigravity | `AGENTS.md` plus `.antigravity/skills/` | Skills via symlink. |
| Junie | `AGENTS.md` plus `.junie/skills/` | Skills via symlink. |
| `.codex/` | Compatibility shim only | Keep it documented as non-canonical. |


## Naming Rules

- Prefix every published skill with `adk-`.
- Prefix every project maintenance skill with `prj-`.
- Prefix every agent persona with `adk-`.
- Group names by use case for autocomplete:
  - `adk-review-*`
  - `adk-build`, `adk-refactor`, `adk-migrate`
  - `adk-write-*`, `adk-audit-*`
  - `prj-audit-*`, `prj-refresh-*`, `prj-update-*`
- Prefer professional, literal names over clever names.

## Catalog Rules

- Keep the published catalog focused.
- Organize around user intent, not internal implementation layers.
- Avoid exposing helper or guideline skills as first-class installables unless they are useful on their own.
- Do not publish connector or setup skills whose only job is to expose a tool, MCP server, or runtime configuration surface.
- It is acceptable to publish a workflow skill when the workflow itself is the user-facing outcome, such as iterative brainstorming before design or implementation.
- Prefer direct runtime MCP/tool use and existing built-in skills over duplicating those capabilities in the public ADK catalog.
- Retire or hide legacy skills instead of keeping them in the default user-facing list.

## Persona Rules

- Each published skill owns its persona in `references/persona.md`.
- Personas are skill-specific -- they are not shared or copied by the refresh script.
- Personas must define:
  - mission
  - scope
  - hard rules
  - evidence expectations
  - output style

## Installation

### Method 1: npx skills (skills only)
```bash
npx skills add sujeet-pro/agents-devkit --all
```

### Method 2: Clone + Symlink (full platform)
```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.agents-devkit
cd ~/.agents-devkit
./scripts/install.sh --agents claude,cursor,codex --global
./scripts/install-mcp.sh --agent claude-code,cursor
```

### Symlink Sync
```bash
./scripts/sync-links.sh          # add missing, prune stale
./scripts/sync-links.sh --dry-run # preview changes
./scripts/uninstall.sh            # remove all adk-* symlinks
```

## Shared Guidance Flow

1. Edit shared guidance in `ai-guidelines/` (constitution, output-format, research-protocol, or README).
2. Run `python3 ai-guidelines/scripts/refresh_adk_skills.py scope --changed-path <path>` to check impact.
3. Run `python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared` to sync to all skills.
4. The mapping is defined in `ai-guidelines/shared-files-map.json`.
5. Regenerate manifest and run tests to validate.
