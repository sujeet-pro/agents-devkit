# ADK Repository Guidance

## Read First
- `ai-guidelines/README.md`
- `ai-guidelines/constitution.md`
- `ai-guidelines/brainstorming-workflow.md`
- `ai-guidelines/skill-architecture.md`
- `ai-guidelines/update-scope-policy.md`
- `ai-guidelines/sources/registry.json`

## Repository Structure

| Directory | Purpose | Naming |
| --- | --- | --- |
| `skills/adk-*` | Published installable skills | `adk-` prefix |
| `agent-personas/adk-*` | Canonical reusable agent personas for parallel teams | `adk-` prefix |
| `agents-claude/` | Claude-specific generated agent sources | Markdown |
| `agents-cursor/` | Cursor-specific generated agent sources | Markdown |
| `agents-codex/` | Codex-specific generated agent sources | TOML |
| `hooks/settings.json` | Claude hook source | generated JSON |
| `hooks/hooks-cursor/` | Cursor hook source | generated JSON |
| `hooks/hooks-codex/` | Codex hook source | generated JSON |
| `mcp-config/` | MCP server configurations | per-server JSON |
| `workflows/` | Composable multi-skill pipelines | YAML files |
| `ai-guidelines/` | Shared source of truth | canonical guidance |
| `.claude/skills/prj-*` | Repo-only Claude maintenance skills | `prj-` prefix |
| `.cursor/skills/prj-*` | Repo-only Cursor maintenance skills | `prj-` prefix |
| `.agents/skills/prj-*` | Repo-only Codex/OpenCode maintenance skills | `prj-` prefix |

## Intent to Skill Mapping

| User Intent | Skill |
| --- | --- |
| Close ambiguity before planning or implementation | `adk-brainstorm` |
| Plan a feature or task | `adk-plan` |
| Research a technical question | `adk-research` |
| Build, fix, or enhance code | `adk-build` |
| Refactor code structure | `adk-refactor` |
| Migrate frameworks or libraries | `adk-migrate` |
| Review a pull request | `adk-review-pr` |
| Review local changes | `adk-review-local-changes` |
| Address review feedback | `adk-address-review-feedback` |
| Review documentation | `adk-review-docs` |
| Write documentation | `adk-write-docs` |
| Write a spec | `adk-spec` |
| Audit a repository | `adk-audit-repo` |
| Audit a website | `adk-audit-site` |
| Test and verify | `adk-test` |
| Design UI/frontend | `adk-design` |
| Create diagrams | `adk-diagram` |
| Create charts | `adk-chart` |
| Commit, PR, changelog | `adk-commit` |
| GitHub operations | `adk-github` |
| Bitbucket operations | `adk-bitbucket` |
| Confluence publishing | `adk-confluence` |
| Google Drive operations | `adk-google-drive` |
| Session handoff | `adk-handoff` |
| Dependency analysis | `adk-deps` |
| Create a new skill | `adk-create-skill` |

## Core Rules
- Accuracy over speed
- Plan before implementation
- Validate every meaningful change
- Keep output concise and bullet-first
- Do not present inference as fact
- Use the update-scope rules before bulk skill edits

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

# Optional: enable the structured brainstorming MCP
export BRAINSTORMING_MCP_ROOT="$HOME/path/to/mcp-brainstorming"
./scripts/install-mcp.sh --agent claude-code,cursor --servers brainstorming
```

## Suggested User-Level Prompt

Add a snippet like this to user-level `AGENTS.md` or `CLAUDE.md` when you want design-first behavior:

```md
When a task involves design, trade-offs, ambiguity, or meaningful risk, start with the ADK brainstorming workflow.

1. Prefer the brainstorming MCP if available.
2. If it is missing, warn once with install guidance and continue using the fallback workflow.
3. Capture current state, target state, acceptable blast radius, desired confidence, and preferred artifact output.
4. Research unknowns, present options, and ask follow-up questions until confidence is high enough for the task.
5. Route into the right skill: brainstorm, spec, plan, write-docs, build, refactor, migrate, or design.
```

## Repo Maintenance Commands

```bash
python3 ai-guidelines/scripts/refresh_adk_skills.py status
python3 ai-guidelines/scripts/refresh_adk_skills.py scope --changed-path <path>
python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared --dry-run
python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared
python3 scripts/generate_agent_projections.py --check
python3 scripts/generate_hook_projections.py --check
python3 scripts/generate-skills-manifest.py --check
python3 tests/test_skills.py
python3 tests/test_agents.py
python3 tests/test_hooks.py
npm run docs:build
npx skills add . --list
./scripts/sync-links.sh --dry-run
```

## Provider-Specific Guidance

| Provider | Entry Point | Skills Dir | Agents Dir |
| --- | --- | --- | --- |
| Claude Code | `CLAUDE.md` | `.claude/skills/` | `.claude/agents/` |
| Cursor | `AGENTS.md` | `.cursor/skills/` | `.cursor/agents/` |
| Codex/OpenCode | `AGENTS.md` | `.agents/skills/` and `.codex/skills/` | `.codex/agents/` |
| Gemini CLI | `GEMINI.md` | -- | -- |
| Antigravity | `AGENTS.md` | `.antigravity/skills/` | -- |
| Junie | `AGENTS.md` | `.junie/skills/` | -- |

Notes:
- `agent-personas/adk-*/AGENT.md` remains the canonical persona source.
- Claude, Cursor, and Codex install sources live in `agents-claude/`, `agents-cursor/`, and `agents-codex/`.
- Runtime-specific custom agent files are generated with `python3 scripts/generate_agent_projections.py`.
- Runtime-specific hook files are generated with `python3 scripts/generate_hook_projections.py` into `hooks/`.
- Claude, Cursor, and Codex each support custom agents, but their file formats and supported fields differ.
- ADK no longer ships slash-command wrappers; skills are the only task invocation surface in this repo.
