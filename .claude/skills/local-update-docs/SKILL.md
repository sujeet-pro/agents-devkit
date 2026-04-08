---
name: local-update-docs
description: "Auto-update docs/guide/ use-case articles, docs/reference/skills/, and docs/reference/agents/ from current definitions"
user-invocable: true
argument-hint: "[--dry-run] [--section guide|skills|agents|all]"
---

# Update Documentation

Scans `skills/` and `agents/` for currently available definitions, then updates the documentation site under `docs/` to stay in sync. Adds pages for new skills/agents, removes pages for deleted ones, and refreshes content from source files.

**Important**: Reference pages are deep-dive documentation, not copies of SKILL.md. Guide pages explain how to use skills for a task. See [Content Philosophy](#content-philosophy) for the distinction.

## Pagesmith Reference

This project uses `@pagesmith/docs` for the documentation site. Before making structural changes (meta.json5, frontmatter, content layout), read the pagesmith reference:

- **Full reference**: `node_modules/@pagesmith/docs/REFERENCE.md` — config, CLI, content structure, frontmatter, markdown, navigation, deployment
- **Agent usage & prompts**: `node_modules/@pagesmith/docs/docs/agents/usage.md` — expected structure, agent integration prompts
- **Recipes**: `node_modules/@pagesmith/docs/docs/agents/recipes.md` — step-by-step task recipes for common doc operations
- **AI context index**: `node_modules/@pagesmith/docs/docs/llms-full.txt` — full AI reference with priority order and key rules

Key pagesmith rules:
- Use `meta.json5` and frontmatter for ordering and labels, not hardcoded nav lists
- `meta.json5` supports nested `items` arrays for sidebar sub-groups
- Frontmatter fields: `title`, `description`, `order`, `draft`, `sidebarLabel`, `navLabel`
- Content directory is `docs/` (configured in `pagesmith.config.json5`)

## Content Philosophy

### Guide vs Reference

| Aspect | Guide (`docs/guide/`) | Reference (`docs/reference/`) |
|--------|----------------------|------------------------------|
| **Purpose** | How to accomplish a task | Deep dive into a specific tool |
| **Audience** | User who wants to do something | User who wants to understand everything about a tool |
| **Structure** | Task-oriented: "Code Reviews" covers all review skills together | Tool-oriented: one page per skill/agent |
| **Tone** | Tutorial, step-by-step, "here's how" | Reference, comprehensive, "here's what it does and why" |
| **Examples** | "To review a PR, run..." | Multiple examples organized by outcome/use-case |

### Reference Page Principles

Reference pages are **not** copies of SKILL.md. They are authored documentation that:

1. **Explain the philosophy** — why the skill/agent exists, what problem it solves, design decisions behind it
2. **Cover every flag** — all parameters with types, defaults, and contextual explanation (not just a table)
3. **Describe the workflow** — how the skill works internally, decision points, auto-detection logic
4. **Show real examples** — concrete examples organized by use case, showing different outcomes

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

### Phase 1: Read Pagesmith Docs

Read `node_modules/@pagesmith/docs/REFERENCE.md` sections on Content Structure, Frontmatter, and Section Meta to understand current conventions before making changes.

### Phase 2: Inventory

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
   - **Design rationale** — why the skill exists, what gap it fills
   - **Key design decisions** — auto-detection logic, conditional stages, fallback behavior
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
   - Review priorities/focus areas (from body)
   - Process/methodology (from body)
   - Key rules and constraints (from body)
   - Memory behavior (from body)

### Phase 3: Diff

1. **Skill references** (`docs/reference/`): List existing `.md` files matching skill names (excluding overview READMEs, `LANDSCAPE.md`, `INSPIRATION-MAP.md`, `CATEGORY-ROUTING.md`, and agent files). Compare against skill inventory.
2. **Agent references** (`docs/reference/`): List existing `.md` files matching agent names. Compare against agents inventory.
3. **Guide use-case articles** (`docs/guide/`): Check use-case directories (`code-reviews/`, `development/`, `documentation/`, `diagrams/`, `research-planning/`, `audits-quality/`, `project-management/`, `setup-config/`).

For each section, identify:
- **Missing**: definitions without a matching doc page
- **Orphaned**: doc pages without a matching definition
- **Stale**: pages where content differs from the source definition

### Phase 4: Present Changes

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

### Phase 5: Execute

#### Updating Skill Reference Pages (`docs/reference/<skill-name>.md`)

Each skill reference page is a **deep-dive document**, not a SKILL.md copy. Write it as documentation a user would read to fully understand the skill.

Template structure:

```markdown
---
title: "<skill-name>"
description: "<one-line description — written for the docs reader>"
skill_name: <name from SKILL.md>
category: <task|routing|guideline|connector>
workflow_tier: <full|abbreviated|orchestrator|helper>
user_invocable: <true|false>
---

# <skill-name>

<Opening paragraph: what problem this skill solves and why it exists.
Not a copy of the SKILL.md description — write this as documentation
explaining the value proposition to someone discovering the skill.>

## Overview

<2-3 paragraphs covering:
- The design philosophy behind the skill
- Where it fits in the ADK ecosystem (what category, what it complements)
- Key design decisions (why auto-detection, why conditional stages, etc.)
- What makes it different from adjacent skills>

## Parameters

<Full parameter table from SKILL.md. After the table, expand on
non-obvious parameters with prose explanations:
- What each flag actually does in practice
- Interaction between flags (e.g., --focus changes what --mode does)
- Defaults and auto-detection logic>

## How It Works

<Prose explanation of the skill's internal workflow. Written for a
user who wants to understand what happens when they run the skill.

Cover:
- The overall flow (phases, stages, decision points)
- Auto-detection logic (how it picks modes/actions/sources)
- Conditional behavior (what changes based on context)
- How it composes with other skills (what it invokes and when)

This is NOT a copy of the phase table. It's a narrative explanation
of the skill's behavior.>

## Modes & Variations

<If the skill has modes or behavior variations, explain each one:
- What triggers it
- What it does differently
- When to use it vs other modes>

## Output

<What the skill produces. Structure, format, and how to read the output.
Include a brief example of output structure if helpful.>

## Examples

<Concrete examples organized by use case. Each example group shows a
real scenario with the command and what outcome to expect.

Organize by OUTCOME not by flag:

### Reviewing a Pull Request
### Fixing Review Comments
### Generating a PR Description
### Running a Security-Focused Review
...

Each example:
- Brief description of the scenario (1-2 lines)
- The command
- What happens / expected outcome (1-2 lines)>
```

**Writing guidelines for skill reference pages:**
- Write the Overview section fresh — do not copy the SKILL.md intro verbatim
- The Parameters table can match SKILL.md, but add prose below it explaining non-obvious interactions
- How It Works must be prose documentation, not a phase table
- Examples must be organized by use case/outcome, with scenario context — not just a list of commands
- Mention adjacent skills briefly but don't duplicate their reference pages
- For routing skills: explain the routing logic and when each sub-skill is selected
- For helper skills: explain what invokes them and what they provide
- For connector skills: explain the API operations and authentication

#### Updating Agent Reference Pages (`docs/reference/<agent-name>.md`)

Each agent reference page follows the same deep-dive principle. Write it as documentation about a specialized team member.

Template structure:

```markdown
---
title: "<agent-name>"
description: "<one-line description — written for docs>"
name: <adk-agent-name>
model: <model>
---

# <agent-name>

<Opening paragraph: what this agent does and why it exists as a
dedicated agent rather than inline logic. What expertise it brings.>

## Overview

<2-3 paragraphs covering:
- The agent's purpose and specialization
- Why this is a separate agent (what domain expertise it encapsulates)
- How it fits into team compositions
- Key design decisions (model choice, tool selection, skill preloading)>

## How It Works

<Prose explanation of the agent's process:
- Step-by-step methodology it follows
- How it prioritizes findings/output
- Decision logic and analysis approach
- What it reads, what it produces>

## Focus Areas

<The agent's review/analysis priorities, ordered by importance.
For each area, explain what it looks for and why it matters.
Write as prose with examples, not just a bullet list copy.>

## Configuration

### Model & Tools

<What model it uses and why. What tools it has access to and how
it uses them. What skills are preloaded and what they provide.>

## Output Format

<What the agent produces. Structure, format conventions, and how
to interpret the output. Include a brief structural example.>

## Key Rules

<Constraints and principles the agent follows. What it will and
won't do. Quality bars and evidence requirements.>

## Integration

<Which skills invoke this agent and in what context. What team
shapes it participates in. How multiple instances coordinate.>

## Examples

<Concrete scenarios organized by use case:

### Reviewing a PR for Security Issues
### Auditing Repository Architecture
### Debugging a Test Failure
...

Each example:
- Scenario context (1-2 lines)
- How the agent is invoked (which skill triggers it)
- What it produces in this scenario>
```

**Writing guidelines for agent reference pages:**
- The Overview should explain WHY this is a separate agent, not just what it does
- How It Works is the agent's methodology — its expertise distilled into a process
- Focus Areas should be written as prose with examples, not a bullet list lifted from the agent file
- Integration section is critical — users need to know which skills trigger this agent
- Examples should show real scenarios where the agent adds value

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

#### Updating Sidebar Navigation (`meta.json5`)

Use pagesmith `meta.json5` conventions (see `node_modules/@pagesmith/docs/REFERENCE.md` Section Meta) for sidebar structure:

1. **`docs/reference/meta.json5`** — flat `items` array listing ALL skill and agent slugs in display order, with `series` for visual grouping by category (skills by function, agents by domain)
2. **`docs/guide/meta.json5`** — add/remove entries for use-case categories

#### Updating Index Pages

1. **`docs/reference/skills/README.md`** — rebuild skill tables from current inventory
2. **`docs/reference/agents/README.md`** — rebuild agent tables from current inventory

#### Removing Orphaned Pages

- Delete `docs/reference/<name>.md` for skills that no longer exist in `skills/`
- Delete `docs/reference/<name>.md` for agents that no longer exist in `agents/`
- Remove the slug from `docs/reference/meta.json5` `items` array and matching `series` entry
- If a use-case category has zero matching skills, remove its directory from `docs/guide/`

### Phase 6: Validate

1. Verify all reference pages link to existing definitions
2. Verify all guide articles reference existing skills
3. Check for broken cross-references between guide and reference pages
4. Report a summary of changes made

## File Layout

All skill and agent reference pages live directly under `reference/` (flat structure) so the sidebar shows everything in one view. The `meta.json5` uses `series` for visual grouping.

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
│   ├── code-reviews/README.md          # Use-case guide (how to do code reviews)
│   ├── development/README.md
│   ├── documentation/README.md
│   ├── diagrams/README.md
│   ├── research-planning/README.md
│   ├── audits-quality/README.md
│   ├── project-management/README.md
│   └── setup-config/README.md
└── reference/
    ├── meta.json5                      # ALL items with series grouping
    ├── skills/README.md                # Skill reference index (overview page)
    ├── agents/README.md                # Agent reference index (overview page)
    ├── <skill-name>.md                 # Deep-dive reference per skill (flat)
    ├── <agent-name>.md                 # Deep-dive reference per agent (flat)
    ├── LANDSCAPE.md                    # (not managed)
    ├── INSPIRATION-MAP.md              # (not managed)
    ├── CATEGORY-ROUTING.md             # (not managed)
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
