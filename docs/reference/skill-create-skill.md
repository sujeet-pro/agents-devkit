---
title: "create-skill"
description: "Scaffold a new ADK skill with proper directory structure and frontmatter"
skill_name: create-skill
category: task
workflow_tier: abbreviated
user_invocable: true
---

# create-skill

Scaffolds a new ADK skill with the correct directory structure, SKILL.md with proper frontmatter, preflight script, and propagated common files. Ensures the new skill follows all ADK conventions from the start.

## Purpose

- Generate a new skill directory under `skills/` with the standard layout (`SKILL.md`, `references/`, `scripts/`)
- Fill in frontmatter fields automatically based on category and family selection
- Copy the preflight script from the shared template
- Run propagation to populate common reference files
- Validate the result with the test suite

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<skill-name>` | kebab-case string | (required) | Directory name for the new skill |
| `--category` | `task`, `guideline`, `connector`, `routing` | `task` | Skill category — determines tier and invocability |
| `--family` | `quick-action`, `standard-task`, `complex-build`, `investigative-loop` | `standard-task` | Workflow family (task skills only) |
| `--auto` | flag | off | Skip confirmations |

## Key Behaviors

### Category to Tier Mapping

| Category | `workflow-tier` | `user-invocable` |
|----------|-----------------|------------------|
| task | `full` or `abbreviated` | `true` |
| guideline | `helper` | `false` |
| connector | `helper` | `false` |
| routing | `orchestrator` | `true` |

### Generated Structure

```
skills/<skill-name>/
├── SKILL.md              # Generated with filled frontmatter
├── references/           # Created empty (propagation fills common files)
└── scripts/
    └── preflight.py      # Copied from shared template
```

### Generated Frontmatter

New skills start with `maturity: experimental`. All required fields are pre-filled:

- `name`: the skill name (matching directory)
- `description`: `"adk - [<tier>] [<area>] Use when <description>"`
- `user-invocable`: based on category
- `workflow-tier`: mapped from category
- `maturity`: `experimental`
- `workflow-family`: the chosen family (task skills only)

### Post-Creation Steps

After scaffolding, the skill creator runs propagation to copy common files and the test suite to validate structure.

## Workflow

Uses the **Quick Action** workflow: confirm → execute → verify.

1. **Confirm**: gather skill name, category, description, and workflow family; confirm with user
2. **Execute**: create directory structure, generate SKILL.md, copy preflight script, run propagation
3. **Verify**: validate structure with test suite, show summary and next steps

## Shared Skills

| Helper Skill | When | Inline Fallback |
|-------------|------|-----------------|
| `workflow` | always | Quick Action: confirm → execute → verify. `--auto` skips confirmations. |
| `communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics. |

## Examples

```
/adk:create-skill my-new-skill
/adk:create-skill my-linter --category guideline
/adk:create-skill api-gateway --category connector
/adk:create-skill my-new-skill --family complex-build
```

## Invoked By

This is a standalone user-invocable skill. It is not automatically invoked by other skills.

## Adjacent Skills

| Skill | Relationship |
|-------|-------------|
| `setup` | Configure tools and MCP servers for a skill's dependencies |
| `use` | Route to the right skill when unsure which to use |
