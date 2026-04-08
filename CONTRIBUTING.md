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

- **`name` field**: Set to `<skill-name>` matching the directory name (e.g., `name: code-review-pr`). No `adk-` prefix — the plugin provides the `adk:` namespace.
- **Plugin namespace**: `adk:` — Claude plugin users invoke as `/adk:code-review-pr`. The folder name determines the plugin invocation.
- **skills.sh**: Uses the `name` field directly — invoked as `/<skill-name>` (e.g., `/code-review-pr`).
- **Description prefix**: Always starts with `adk -` (e.g., `description: "adk - [full] [review] ..."`). This prefix is retained so skills remain identifiable when installed outside the plugin (e.g., via `npx skills`).
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

Small common files from `templates/skill/common/` (for example `help-format.md`, `project-guidelines.md`, `inline-interaction.md`) and `preflight.py` are still propagated to all skills:

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
   name: skill-name
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
   name: guideline-name
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
   name: platform-name
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
   name: adk-agent-name
   description: "When Claude should delegate to this agent"
   model: opus | sonnet
   tools:
     - Glob
     - Grep
     - Read
   effort: high
   memory: project
   color: blue
   skills:
     - adk-coding
   ---
   ```
2. **`name` field**: Use `adk-<agent-name>` prefix to avoid collisions with user custom agents
3. **`tools`**: Keep tool lists minimal — only grant tools the agent actually needs
4. **`effort: high`**: Default for all ADK agents (higher quality output)
5. **`memory: project`**: Enables cross-session learning stored in `.claude/agent-memory/`
6. **`color`**: Assign by category — blue (code), green (docs), cyan (research), pink (design), yellow (planning), purple (orchestration), orange (quality), red (execution)
7. **`skills`**: Preload relevant helper skills into agent context
8. Add a `## Memory` section to the system prompt body instructing the agent what to learn
9. Skills reference agents by name with `adk-` prefix
10. **Agent teams**: To enable parallel agent orchestration, add `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` to `.claude/settings.json` env

## Conventions

- **Skill descriptions**: start with `adk -` followed by bracket tags and "Use when..."
- **Skill `name` field**: `<skill-name>` matching directory name (no `adk-` prefix; plugin provides the namespace)
- **Workflow tier**: declare in frontmatter (`full`, `abbreviated`, `helper`, `orchestrator`)
- **Skill cross-references**: use `/adk:<skill-name>` format
- **Skill file references**: use `${CLAUDE_SKILL_DIR}/references/` or `${CLAUDE_SKILL_DIR}/scripts/`
- **Self-sufficiency**: task skills include inline fallbacks for all shared knowledge
- **No interactive scripts**: all interactivity via the agent (inline questions, options, confirmations)
- **Human-in-the-loop**: confirm intent, present options, approve plan before executing
- **Auto mode**: support `--auto` flag to skip confirmations
- **Git**: use system identity
- **Intermediary artifacts**: `.temp/<task-slug>/` directory (gitignored; see `/adk:workspace-conventions`)
- **Diagram output**: `diagrams/` folder sibling to the document (or project root for standalone); both light+dark SVG and PNG
- **Output**: markdown by default for all skill outputs

## Upstream Sources

ADK tracks upstream sources in `manifest.json`. Use `/adk:deps-tracker` to manage:

- **diagramkit**: Diagram reference material and rendering
- **superpowers**: Skill patterns and workflows
- **pagesmith**: Markdown features and documentation generation
