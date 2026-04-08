---
name: local-update-docs
description: "Auto-update docs/guide/ use-case articles, docs/reference/skills/, and docs/reference/agents/ from current definitions"
user-invocable: true
argument-hint: "[--dry-run] [--section guide|skills|agents|all]"
---

# Update Documentation

Scans `skills/` and `agents/` for currently available definitions, then updates the documentation site under `docs/` to stay in sync. Adds pages for new skills/agents, removes pages for deleted ones, and refreshes parameters/workflows from source files.

## When to Run

- After adding, removing, or modifying a skill
- After adding, removing, or modifying an agent
- After changing parameters or workflow phases in a SKILL.md
- As a periodic docs health check

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--dry-run` | flag | off | Show what would change without modifying files |
| `--section` | `guide`, `skills`, `agents`, `all` | `all` | Which doc section to update |
| `--auto` | flag | off | Skip confirmations |

## Procedure

### Phase 1: Inventory

#### Skills Inventory

1. List all directories under `skills/` to get the current skill set
2. For each skill, read `SKILL.md` and extract:
   - `name` (from frontmatter)
   - `description` (from frontmatter)
   - `workflow-tier` (from frontmatter: `full`, `abbreviated`, `orchestrator`, `helper`)
   - `user-invocable` (from frontmatter, default `true`)
   - Category tags from description (e.g., `[full] [code-review]`, `[helper] [guideline]`)
   - Parameters table (from `## Help` or `### Parameters` section)
   - Behavior variations / modes
   - Phase applicability table
   - Shared skills table
   - Examples section
3. Categorize each skill:
   - **Task skills**: `user-invocable: true` AND tier is `full` or `abbreviated`
   - **Routing skills**: tier is `orchestrator` or category contains `[routing]`
   - **Helper skills**: `user-invocable: false` or tier is `helper`
   - **Connector skills**: category contains `[connector]`

#### Agents Inventory

1. List all `.md` files under `agents/` (excluding `README.md`)
2. For each agent, read the file and extract:
   - Agent name (from frontmatter `name` field or filename)
   - Description (from frontmatter)
   - Model (from frontmatter)
   - Allowed tools (from frontmatter)
   - Role description (from body)

### Phase 2: Diff

1. **Skill references** (`docs/reference/skills/`): List existing `.md` files (excluding `README.md`, `LANDSCAPE.md`, `INSPIRATION-MAP.md`, `CATEGORY-ROUTING.md`). Compare against skill inventory.
2. **Agent references** (`docs/reference/agents/`): List existing `.md` files (excluding `README.md`). Compare against agents inventory.
3. **Guide use-case articles** (`docs/guide/`): Check use-case directories (`code-reviews/`, `development/`, `documentation/`, `diagrams/`, `research-planning/`, `audits-quality/`, `project-management/`, `setup-config/`).

For each section, identify:
- **Missing**: definitions without a matching doc page
- **Orphaned**: doc pages without a matching definition
- **Stale**: pages where content differs from the source definition

### Phase 3: Present Changes

If not `--auto`, display a summary table:

```
Docs Update Plan
================

Skill references to ADD:    [list]
Skill references to REMOVE: [list]
Skill references to UPDATE: [list]
Agent references to ADD:    [list]
Agent references to REMOVE: [list]
Agent references to UPDATE: [list]
Guide articles:             [changes]

Proceed? [y/n]
```

### Phase 4: Execute

#### Updating Skill Reference Pages (`docs/reference/skills/<skill-name>.md`)

For each skill, generate or update its reference page with:

```markdown
---
title: "<skill-name>"
description: <description from SKILL.md>
skill_name: <name from SKILL.md>
category: <task|routing|guideline|connector>
workflow_tier: <full|abbreviated|orchestrator|helper>
user_invocable: <true|false>
---

# <skill-name>

<First paragraph from SKILL.md>

## When to Use / Purpose
<From SKILL.md>

## Parameters
<Parameters table from SKILL.md>

## Workflow
<Phase applicability from SKILL.md>

## Shared Skills / Invoked By
<From SKILL.md>

## Examples
<From SKILL.md>
```

#### Updating Agent Reference Pages (`docs/reference/agents/<agent-name>.md`)

For each agent, generate or update its reference page with:

```markdown
---
title: "<agent-name>"
description: <description from agent file>
model: <model from agent file>
---

# <agent-name>

<Description>

## Role
<From agent system prompt body>

## Allowed Tools
<From frontmatter>

## Used By
<Skills that reference this agent>
```

#### Updating Guide Use-Case Articles (`docs/guide/<category>/README.md`)

For each use-case category, scan matching skills and update:
- The scenarios list (add new skills, remove deleted ones)
- The "Which Skill to Use?" table
- Parameter examples for new or changed parameters

Use-case category mapping:

| Category Directory | Matching Skill Tags |
|-------------------|---------------------|
| `code-reviews/` | `[code-review]` |
| `development/` | `[dev]` |
| `documentation/` | `[docs]` |
| `diagrams/` | `[diagram]` |
| `research-planning/` | `[research]`, `[plan]`, `[spec]` |
| `audits-quality/` | `[audit]`, `[utility]` (test), `[chart]` |
| `project-management/` | `[project]`, `[handoff]`, `[team]` |
| `setup-config/` | `[setup]` |

#### Updating Index Pages

1. **`docs/reference/skills/README.md`** — rebuild skill tables from current inventory
2. **`docs/reference/agents/README.md`** — rebuild agent tables from current inventory
3. **`docs/guide/meta.json5`** — add/remove entries for use-case categories

#### Removing Orphaned Pages

- Delete `docs/reference/skills/<name>.md` for skills that no longer exist in `skills/`
- Delete `docs/reference/agents/<name>.md` for agents that no longer exist in `agents/`
- If a use-case category has zero matching skills, remove its directory from `docs/guide/`

### Phase 5: Validate

1. Verify all reference pages link to existing definitions
2. Verify all guide articles reference existing skills
3. Check for broken cross-references between guide and reference pages
4. Report a summary of changes made

## File Layout

```
docs/
├── meta.json5                          # Top-level: Guide, Reference
├── guide/
│   ├── meta.json5                      # Includes use-case categories
│   ├── prerequisites/README.md
│   ├── getting-started/README.md
│   ├── philosophy/README.md
│   ├── skills/README.md
│   ├── workflow/README.md
│   ├── code-reviews/README.md          # Use-case guide
│   ├── development/README.md
│   ├── documentation/README.md
│   ├── diagrams/README.md
│   ├── research-planning/README.md
│   ├── audits-quality/README.md
│   ├── project-management/README.md
│   └── setup-config/README.md
└── reference/
    ├── meta.json5                      # Skills, Agents, Config, Guidelines
    ├── skills/
    │   ├── README.md                   # Skill reference index (ALL skills)
    │   ├── <skill-name>.md             # One page per skill (task + helper + connector)
    │   ├── LANDSCAPE.md                # (not managed)
    │   ├── INSPIRATION-MAP.md          # (not managed)
    │   └── CATEGORY-ROUTING.md         # (not managed)
    ├── agents/
    │   ├── README.md                   # Agent reference index
    │   └── <agent-name>.md             # One page per agent
    ├── config/README.md
    └── guidelines/README.md
```

## Examples

```text
# Update all docs
/local-update-docs

# See what would change
/local-update-docs --dry-run

# Only update skill reference pages
/local-update-docs --section skills

# Only update agent reference pages
/local-update-docs --section agents

# Only update guide use-case articles
/local-update-docs --section guide

# Update everything without confirmations
/local-update-docs --auto
```
