---
name: create-skill
description: "adk - [abbreviated] [meta] Scaffold a new ADK skill — generates directory structure, SKILL.md with proper frontmatter, preflight script, and runs propagation"
user-invocable: true
argument-hint: "<skill-name> [--category task|guideline|connector|routing] [--family quick-action|standard-task|complex-build|investigative-loop] [--help]"
allowed-tools: [Read, Write, Bash, Glob]
workflow-tier: abbreviated
maturity: stable
workflow-family: quick-action
dependencies:
  commands: [python3]
---

# Create Skill

Scaffolds a new ADK skill with the correct directory structure, frontmatter, preflight script, and propagated common files. Ensures the new skill follows all ADK conventions from the start.

## Shared Skills

This skill **invokes helper skills** for shared behavior. If a **required** helper is unavailable, use the **inline fallback** summary.

| Helper skill | Invoke (Claude plugin) | Invoke (Codex / skills.sh) | When | Inline fallback (1–2 lines) |
|--------------|------------------------|------------------------------|------|----------------------------|
| workflow | `/adk:workflow --family quick-action` | `/workflow --family quick-action` | always | Quick Action workflow: confirm → execute → verify. `--auto` skips confirmations. |
| communication | `/adk:communication` | `/communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<skill-name>` | kebab-case string | (required) | Directory name for the new skill |
| `--category` | `task`, `guideline`, `connector`, `routing` | `task` | Skill category — determines tier and invocability |
| `--family` | `quick-action`, `standard-task`, `complex-build`, `investigative-loop` | `standard-task` | Workflow family (task skills only) |
| `--auto` | flag | off | Skip confirmations |

### Examples

```
/adk:create-skill my-new-skill
/adk:create-skill my-linter --category guideline
/adk:create-skill api-gateway --category connector
/adk:create-skill my-new-skill --family complex-build
```

## Preflight

```
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}
```

## Workflow

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

## Output Format

```markdown
## Skill Created: <skill-name>

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

## Adjacent Skills

- `/adk:setup` / `/setup` — when configuring tools and MCP servers for a skill's dependencies
- `/adk:use` / `/use` — when you're unsure which skill to use and need routing
