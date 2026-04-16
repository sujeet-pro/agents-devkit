# Agent Development Kit (ADK)

Public, self-contained engineering skills, agent personas, runtime hooks, MCP configs, and workflows for coding agents. Works with Claude Code, Cursor, Codex, Antigravity, Junie, and Gemini CLI.

## Installation

### Method 1: npx skills (skills only)

```bash
# Install all skills
npx skills add sujeet-pro/agents-devkit --all

# Install a specific skill
npx skills add sujeet-pro/agents-devkit/skills/adk-build

# List available skills
npx skills add . --list
```

### Method 2: Clone + Symlink (full platform)

Clone once, symlink everywhere. Get skills, agents, hooks, and MCP configs with automatic sync.

```bash
# Clone the repo
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.agents-devkit
cd ~/.agents-devkit

# Install skills and runtime-specific agents for your tools
./scripts/install.sh --agents claude,cursor,codex --global

# Install MCP server configs
./scripts/install-mcp.sh --agent claude-code,cursor

# Optional: enable the structured brainstorming MCP
export BRAINSTORMING_MCP_ROOT="$HOME/path/to/mcp-brainstorming"
./scripts/install-mcp.sh --agent claude-code,cursor --servers brainstorming

# After repo updates, sync symlinks (adds new, prunes removed)
./scripts/sync-links.sh --global
```

#### Symlink Script Options

```bash
# Install to specific agents
./scripts/install.sh --agents claude,cursor,codex,antigravity,junie --global

# Install to a custom directory (future agent support)
./scripts/install.sh --target ~/.future-agents

# Preview changes without making them
./scripts/install.sh --dry-run

# Remove all ADK symlinks
./scripts/uninstall.sh --global
```

## Repository Structure

```
agents-devkit/
├── skills/                    # Published installable skills (adk-*)
├── agent-personas/            # Canonical reusable agent personas (adk-*)
├── agents-claude/             # Generated Claude agent sources
├── agents-cursor/             # Generated Cursor agent sources
├── agents-codex/              # Generated Codex agent sources
├── hooks/                     # Lifecycle hooks for agent sessions
├── mcp-config/                # MCP server configurations with install script
├── workflows/                 # Composable multi-skill pipelines (YAML)
├── templates/                 # Scaffolding templates for new skills
├── ai-guidelines/             # Shared source of truth (constitution, protocols)
├── scripts/                   # Build, install, and maintenance scripts
├── docs/                      # Documentation site (Pagesmith)
├── tests/                     # Validation test suite
├── AGENTS.md                  # Cross-agent entry point with intent mapping
├── CLAUDE.md                  # Claude Code specifics
├── CODEX.md                   # Codex CLI specifics
└── GEMINI.md                  # Gemini CLI specifics
```

## Public Skills

| Skill | Use When |
| --- | --- |
| `adk-brainstorm` | A task needs design closure, option comparison, or artifact routing before work starts |
| `adk-plan` | A request needs an executable plan before work starts |
| `adk-research` | External facts, upstream behavior, or source-backed comparison matters |
| `adk-build` | Implementing, fixing, or enhancing code |
| `adk-refactor` | Restructuring code without changing behavior |
| `adk-migrate` | Framework, dependency, or pattern migration |
| `adk-review-pr` | Reviewing a PR or branch diff before merge |
| `adk-review-local-changes` | Reviewing local work before commit or PR |
| `adk-address-review-feedback` | Fixing review comments and closing the loop |
| `adk-review-docs` | Reviewing documentation for accuracy and clarity |
| `adk-write-docs` | Writing or updating engineering documentation |
| `adk-spec` | Writing functional specs with acceptance criteria |
| `adk-audit-repo` | Auditing a repository for risk and quality |
| `adk-audit-site` | Auditing a live site for health, SEO, and quality |
| `adk-test` | Verifying behavior through acceptance, regression, or webapp checks |
| `adk-design` | Creating or auditing UI and frontend experience |
| `adk-diagram` | Creating editable diagrams with rendered SVG output |
| `adk-chart` | Turning data into reusable charts |
| `adk-commit` | Drafting commit, PR, and changelog-ready summaries |
| `adk-github` | GitHub operations (PRs, issues, releases) |
| `adk-bitbucket` | Bitbucket operations (PRs, pipelines) |
| `adk-confluence` | Confluence page publishing |
| `adk-google-drive` | Google Drive file operations |
| `adk-handoff` | Session continuity and context handoff |
| `adk-deps` | Dependency analysis and updates |
| `adk-create-skill` | Scaffolding new ADK skills |

## Agent Personas

Reusable subagent roles dispatched by skills for parallel work:

| Agent | Role |
| --- | --- |
| `adk-brainstorm-facilitator` | Iterative brainstorming, trade-off analysis, and route selection |
| `adk-code-reviewer` | Code review with severity-ordered findings |
| `adk-security-reviewer` | Security-focused vulnerability analysis |
| `adk-test-engineer` | Test writing, execution, and coverage |
| `adk-doc-writer` | Documentation authoring from code evidence |
| `adk-research-agent` | Deep technical research with citations |
| `adk-plan-reviewer` | Plan critique and gap analysis |
| `adk-implementer` | Focused code implementation |
| `adk-debugger` | Systematic root-cause debugging |

Canonical persona prompts live in `agent-personas/adk-*/AGENT.md`.

Installable runtime agent sources live in:

- `agents-claude/*.md` for Claude
- `agents-cursor/*.md` for Cursor
- `agents-codex/*.toml` for Codex

Installable runtime hook sources live in:

- `hooks/settings.json` for Claude
- `hooks/hooks-cursor/hooks.json` for Cursor
- `hooks/hooks-codex/hooks.json` for Codex

Regenerate them with:

```bash
python3 scripts/generate_agent_projections.py
python3 scripts/generate_hook_projections.py
```

## Philosophy

- **Human-in-the-Loop** -- decisions happen interactively, execution happens automatically
- **Plan First** -- every non-trivial task follows a phased workflow with approval gates
- **Concise by Default** -- short version first, offer to elaborate
- **Self-Sufficient Skills** -- every skill works independently with inline fallbacks
- **Parallel Agentic Teams** -- non-trivial work uses child agents with distinct roles
- **Principal Engineer Lens** -- do we need this? simplest version? alternatives?
- **Markdown by Default** -- all outputs are markdown unless requested otherwise
- **Auto Mode** -- pass `--auto` to skip confirmations and run end-to-end

## Multi-Agent Support

| Provider | Skills | Agents | Hooks | MCP |
| --- | --- | --- | --- | --- |
| Claude Code | `.claude/skills/` | `.claude/agents/` | `.claude/settings.json` | `~/.claude/mcp.json` |
| Cursor | `.cursor/skills/` | `.cursor/agents/` | `.cursor/hooks.json` | `.cursor/mcp.json` |
| Codex | `.codex/skills/` | `.codex/agents/` | `.codex/hooks.json` | `~/.codex/mcp.json` |
| Agents (generic) | `.agents/skills/` | -- | -- | -- |
| Antigravity | `.antigravity/skills/` | -- | -- | -- |
| Junie | `.junie/skills/` | -- | -- | -- |
| Gemini CLI | `GEMINI.md` imports | -- | -- | -- |

Agent support is not symmetric across runtimes:

- Claude custom subagents use Markdown files with rich YAML frontmatter.
- Cursor custom subagents use Markdown files with a smaller YAML frontmatter surface.
- Codex custom agents use standalone TOML files, not Markdown frontmatter.
- ADK no longer ships a separate slash-command layer; skills are the only command surface in this repo.
- Claude, Cursor, and Codex hooks also differ in path and config schema, so ADK keeps runtime-specific hook source files under `hooks/`.
- See `docs/reference/agents/README.md` for the verified field matrix and projection strategy used in this repo.

## Repo Maintenance

Read these first when changing ADK itself:

- `AGENTS.md`
- `ai-guidelines/README.md`
- `ai-guidelines/constitution.md`
- `ai-guidelines/skill-architecture.md`
- `ai-guidelines/update-scope-policy.md`

Useful commands:

```bash
# Check skill status
python3 ai-guidelines/scripts/refresh_adk_skills.py status

# Propagate shared guidance to all skills
python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared

# Regenerate manifest
python3 scripts/generate-skills-manifest.py

# Regenerate runtime-specific custom agent files
python3 scripts/generate_agent_projections.py

# Regenerate runtime-specific hook files
python3 scripts/generate_hook_projections.py

# Run validation suite
python3 tests/test_skills.py
python3 tests/test_agents.py
python3 tests/test_hooks.py

# Sync symlinks after repo changes
./scripts/sync-links.sh

# Build docs
npm run docs:build
```

## Attribution

ADK takes direct inspiration from these projects, documented in `NOTICE.md` and `ai-guidelines/sources/registry.json`:

- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [obra/superpowers](https://github.com/obra/superpowers)
- [pbakaus/impeccable](https://github.com/pbakaus/impeccable)
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)
- [sujeet-pro/diagramkit](https://github.com/sujeet-pro/diagramkit)
- [browser-use/browser-use](https://github.com/browser-use/browser-use)
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)
- [squirrelscan/skills](https://github.com/squirrelscan/skills)
- [modelcontextprotocol/servers/tree/main/src/sequentialthinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
