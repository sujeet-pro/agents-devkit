---
title: 'create-skill'
description: 'Scaffold a new ADK skill — generates directory structure, SKILL.md with proper frontmatter, preflight script, and runs propagation'
skill_name: create-skill
category: task
workflow_tier: abbreviated
user_invocable: true
---

# create-skill

Use `create-skill` to scaffold a new ADK skill — generates directory structure, SKILL.md with proper frontmatter, preflight script, and runs propagation. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`create-skill` belongs to the `task` layer and is declared at the `abbreviated` tier with the `quick-action` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<skill-name>` | kebab-case string | (required) | Directory name for the new skill |
| `--category` | `task`, `guideline`, `connector`, `routing` | `task` | Skill category — determines tier and invocability |
| `--family` | `quick-action`, `standard-task`, `complex-build`, `investigative-loop` | `standard-task` | Workflow family (task skills only) |
| `--auto` | flag | off | Skip confirmations |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill **invokes helper skills** for shared behavior. If a **required** helper is unavailable, use the **inline fallback** summary.

| Helper skill | Invoke (Claude plugin) | Invoke (Codex / skills.sh) | When | Inline fallback (1–2 lines) |
|--------------|------------------------|------------------------------|------|----------------------------|
| workflow | `/adk:workflow --family quick-action` | `/workflow --family quick-action` | always | Quick Action workflow: confirm → execute → verify. `--auto` skips confirmations. |
| communication | `/adk:communication` | `/communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |

### Preflight

```
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}
```

### Workflow

### 1. Confirm

Gather the skill parameters:

1. **Skill name**: Must be kebab-case, unique (not already in `skills/`)
2. **Category**: task (default), guideline, connector, or routing
3. **Description**: What the skill does — "Use when..."
4. **Workflow family**: For task skills only (default: standard-task)

Map category to tier and invocability:

| Category | `workflow-tier` | `user-invocable` |
|----------|-----------------|------------------|
| task | `full` or `abbreviated` | `true` |
| guideline | `helper` | `false` |
| connector | `helper` | `false` |
| routing | `orchestrator` | `true` |

Confirm the plan with the user (unless `--auto`).

### 2. Execute

Create the skill directory structure:

```
skills/<skill-name>/
├── SKILL.md              # Generated from template with filled frontmatter
├── references/           # Created empty (propagate.py fills common files)
└── scripts/
    └── preflight.py      # Copied from templates/skill/scripts/preflight.py
```

Generate `SKILL.md` with:

1. **Frontmatter** — all required fields filled:
   - `name`: the skill name
   - `description`: `"adk - [<tier>] [<area>] Use when <description>"`
   - `user-invocable`: based on category
   - `argument-hint`: placeholder for the skill's arguments
   - `allowed-tools`: sensible defaults based on category
   - `workflow-tier`: mapped from category
   - `maturity`: `experimental` (new skills start experimental)
   - `workflow-family`: the chosen family (task skills only)
   - `dependencies`: empty dict or with `commands: [git]`

2. **Shared Skills table** — pre-filled with standard helpers (workflow, communication, preflight-check, output-format). For task skills, also include principal-engineer, agentic-teams, and interaction.

3. **Workflow section** — skeleton steps matching the chosen family shape

4. **Output Format section** — markdown template placeholder

5. **Adjacent Skills section** — empty placeholder

Then run propagation to copy common files:

```bash
python3 templates/skill/scripts/propagate.py
```

### 3. Verify

1. Confirm the directory structure was created correctly
2. Run the test suite to validate the new skill:

```bash
python3 tests/test_skills.py
```

3. Show the user a summary of what was created and next steps:
   - Edit `SKILL.md` to fill in the workflow logic
   - Add skill-specific references under `references/`
   - Add stages under `stages/` if multi-mode
   - Update README.md skill tables
   - Update CONTRIBUTING.md if adding a new category

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```markdown

## Related Skills

### Adjacent Skills

- `/adk:setup` / `/setup` — when configuring tools and MCP servers for a skill's dependencies
- `/adk:use` / `/use` — when you're unsure which skill to use and need routing

## Additional Reference

### Skill Created: <skill-name>

### Structure
- `skills/<skill-name>/SKILL.md` — frontmatter + skeleton
- `skills/<skill-name>/scripts/preflight.py` — preflight checks
- `skills/<skill-name>/references/` — common files propagated

### Frontmatter
<show the generated frontmatter>

### Next Steps
1. Edit `SKILL.md` to add your workflow logic
2. Add references under `references/` for skill-specific material
3. Add `stages/` directory if multi-mode
4. Run `/adk:create-skill --help` to see the template again
```

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:create-skill <name>
/adk:create-skill my-new-skill
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:create-skill my-new-skill --family complex-build
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:create-skill <name> --auto
```
