# Contributing to ADK

## Quick Start

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.devkit
cd ~/.devkit
claude --plugin-dir .
```

## Project Structure

```
agents-devkit/
├── .claude-plugin/plugin.json   Plugin manifest
├── .mcp.json                    MCP server configurations
├── hooks/hooks.json             Hook configurations
├── settings.json                Default settings
├── templates/skill/             Common files and propagation
│   ├── SKILL-TEMPLATE.md        Boilerplate for new skills
│   ├── references/              Legacy master copies (deprecated — now guideline skills)
│   ├── common/                  Cross-skill files (help-format, project-guidelines)
│   └── scripts/                 Preflight and propagation scripts
├── agents/                      Shared agent definitions (one .md per agent)
├── settings/                    MCP configuration guide
└── skills/                      Skill library (41 skills: 12 guideline, 27 task, 2 routing)
```

## Skill Categories

| Category | Purpose | Examples |
|----------|---------|---------|
| **Guideline** (helper) | Reusable knowledge auto-invoked by task skills | `workflow`, `communication`, `coding`, `review-standards` |
| **Connector** (helper) | Platform API wrappers with MCP fallback, auto-invoked by task skills | `github`, `bitbucket`, `confluence`, `jira` |
| **Task** (user-facing) | Specific engineering tasks, self-sufficient with inline fallbacks | `code-review-pr`, `dev-build`, `docs-write`, `dev-migrate` |
| **Routing** (orchestrator) | Coordinate and route across other skills | `use`, `team` |

## Skill Architecture

### Workflow Tiers

Every skill declares a `workflow-tier` in its YAML frontmatter:

| Tier | Description | Skills |
| ---- | ----------- | ------ |
| `full` | Full 6-phase framework with human-in-the-loop | code-review-pr, code-review-repo, code-review-fix, docs-review, docs-write, dev-build, dev-refactor, dev-migrate, dev-commit, plan, diagram, diagram-*, spec, project, audit, research, design, handoff, team, docs-repo, docs-crud, deps-tracker |
| `abbreviated` | Framework with permanently skipped phases | test, setup |
| `helper` | Auto-invoked by other skills, no workflow ownership | workflow, communication, principal-engineer, agentic-teams, output-format, interaction, preflight-check, review-standards, coding, docs-guidelines, docs-md, architecture, github, bitbucket, confluence, jira |
| `orchestrator` | Multi-skill pipeline manager | use |

### Naming Convention

- **`name` field**: Set to `adk-<skill-name>` (e.g., `name: adk-code-review-pr`). Used by skills.sh for invocation as `/adk-code-review-pr`.
- **Plugin namespace**: `adk:` — Claude plugin users invoke as `/adk:code-review-pr`. The folder name determines the plugin invocation.
- **Description prefix**: Always starts with `adk -` (e.g., `description: "adk - [full] [review] ..."`)
- **No interactive scripts**: All interactivity is via the agent itself.

### Self-Sufficiency Rule

**Every task skill must be self-sufficient.** Each task skill includes a "Shared Skills" section with:

1. **Skill invocation**: Which guideline skill to invoke when available
2. **Inline fallback**: A brief summary of the shared knowledge, used when the guideline skill is not installed

This means a skill installed via skills.sh works correctly even without the guideline skills installed.

Example pattern in task skills:

```markdown
## Shared Skills

| Skill | Invoked | Inline Fallback |
|-------|---------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. |
| `/adk:communication` | always | Lead with conclusion. No preamble. Concrete specifics. |
```

When a skill needs another skill's capability, it invokes that skill by name (e.g., "invoke `/adk:coding`"), never references its sub-files.

### Common Files Propagation

Small common files (`help-format.md`, `project-guidelines.md`) and `preflight.py` are still propagated to all skills:

```bash
python3 templates/skill/scripts/propagate.py
python3 templates/skill/scripts/propagate.py --dry-run       # Preview changes
python3 templates/skill/scripts/propagate.py --clean-refs     # Remove deprecated reference files
```

## Adding a Skill

1. **Create the skill directory**: `skills/<skill-name>/`
2. **Create `SKILL.md`** with frontmatter:
   ```yaml
   ---
   name: adk-skill-name
   description: "adk - [tier] [area] Use when..."
   user-invocable: true
   argument-hint: "<required-arg> [--optional-arg]"
   allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, Agent]
   workflow-tier: full
   dependencies:
     commands: [git]
   ---
   ```
3. **Add the "Shared Skills" section** with the guideline skills your skill uses and their inline fallbacks
4. **Create `references/`** for skill-specific reference material
5. **Create `scripts/preflight.py`** — copy from `templates/skill/scripts/preflight.py`
6. **Add the Phase Applicability table** to SKILL.md
7. **Add the Output Format section** defining the markdown output structure
8. **Add the Adjacent Skills section** listing related skills with `/adk:` prefix
9. Use `${CLAUDE_SKILL_DIR}` to reference files within the skill directory
10. **Test**: Run the skill with `--help` to verify

## Adding a Guideline Skill

1. Create `skills/<guideline-name>/SKILL.md` with:
   ```yaml
   ---
   name: adk-guideline-name
   description: "adk - [helper] [guideline] ..."
   user-invocable: false
   workflow-tier: helper
   ---
   ```
2. Include the full guideline content directly in SKILL.md
3. Update the "Shared Skills" section in all task skills that should use this guideline
4. Add the inline fallback summary to each consuming skill

## Adding a Connector Skill

1. Create `skills/<platform-name>/SKILL.md` with:
   ```yaml
   ---
   name: adk-platform-name
   description: "adk - [helper] [connector] ..."
   user-invocable: false
   workflow-tier: helper
   dependencies:
     commands: [curl, jq]
   ---
   ```
2. Include auth validation (env vars from `~/.zshenv`), MCP connector detection, and routing to references
3. Create `references/routing.md` mapping use cases to operations
4. Create domain-specific references (e.g., `pr-operations.md`, `comment-operations.md`)
5. Create `scripts/` with bash scripts wrapping the platform API (not needed for CLI-based connectors like `github` which uses `gh`)
6. Update the "Shared Skills" section in all task skills that use this platform
7. Add the inline fallback summary to each consuming skill

## Adding a Coding/Doc Guideline

1. **Coding guidelines**: Add to `skills/coding/references/coding-guidelines/<name>.md`
2. **Document guidelines**: Add to `skills/docs-guidelines/references/doc-guidelines/<name>.md`
3. Cite authoritative sources (specs, official docs) over blog posts

## Adding an Agent

1. Create `agents/<agent-name>.md` with YAML frontmatter:
   ```yaml
   ---
   name: agent-name
   description: "..."
   model: opus | sonnet
   allowed-tools:
     - Glob
     - Grep
     - Read
   ---
   ```
2. Keep tool lists minimal and realistic
3. Skills reference agents by name

## Conventions

- **Skill descriptions**: start with `adk -` followed by bracket tags and "Use when..."
- **Skill `name` field**: `adk-<skill-name>` for dual-install support
- **Workflow tier**: declare in frontmatter (`full`, `abbreviated`, `helper`, `orchestrator`)
- **Skill cross-references**: use `/adk:<skill-name>` format
- **Skill file references**: use `${CLAUDE_SKILL_DIR}/references/` or `${CLAUDE_SKILL_DIR}/scripts/`
- **Self-sufficiency**: task skills include inline fallbacks for all shared knowledge
- **No interactive scripts**: all interactivity via the agent (inline questions, options, confirmations)
- **Human-in-the-loop**: confirm intent, present options, approve plan before executing
- **Auto mode**: support `--auto` flag to skip confirmations
- **Git**: use system identity
- **Intermediary artifacts**: `.temp/` directory (gitignored)
- **Output**: markdown by default for all skill outputs

## Upstream Sources

ADK tracks upstream sources in `manifest.json`. Use `/adk:deps-tracker` to manage:

- **diagramkit**: Diagram reference material and rendering
- **superpowers**: Skill patterns and workflows
- **pagesmith**: Markdown features and documentation generation
