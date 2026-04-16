# ADK Repository Guidance -- Codex CLI

Read `AGENTS.md` first for the full skill catalog and intent mapping.

## Codex-Specific Notes

Codex CLI uses the Agent Skills standard with some differences:

- Skills live in `.codex/skills/*/SKILL.md`
- Custom agents live in `.codex/agents/*.toml`
- Native Codex hook config lives in `.codex/hooks.json`
- Arguments use `$ARGNAME` (uppercase) variable syntax instead of `{{argname}}`
- ADK does not ship a separate prompt wrapper layer; use skills directly.
- Codex custom agents are generated from `agent-personas/adk-*/AGENT.md` into `agents-codex/` with `python3 scripts/generate_agent_projections.py`
- Codex hook config is generated into `hooks/hooks-codex/hooks.json` with `python3 scripts/generate_hook_projections.py`

## Installation

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.agents-devkit
cd ~/.agents-devkit
./scripts/install.sh --agents codex --global
./scripts/install-mcp.sh --agent codex
```

## Skill Format Differences

| Feature | Claude/Cursor | Codex |
| --- | --- | --- |
| Skill location | `.claude/skills/*/SKILL.md` | `.codex/skills/*/SKILL.md` |
| Command layer in this repo | none | none |
| Agent source in this repo | `agents-claude/*.md` or `agents-cursor/*.md` | `agents-codex/*.toml` |
| Arguments | `{{argname}}` | `$ARGNAME` |
| Invocation | skill-native | skill-native |
| Frontmatter | Full YAML | `description` + `argument-hint` |

## Custom Agents

Codex now supports project-scoped custom agents via `.codex/agents/*.toml`.

- Required fields: `name`, `description`, `developer_instructions`
- Common optional fields: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`
- ADK keeps the canonical persona text in `agent-personas/adk-*/AGENT.md` and generates Codex TOML projections into `agents-codex/` for installation

## Hooks

Codex hooks are experimental.

- Install target: `.codex/hooks.json`
- Repo source: `hooks/hooks-codex/hooks.json`
- Feature flag required in `~/.codex/config.toml` or `.codex/config.toml`:

```toml
[features]
codex_hooks = true
```

Regenerate them with:

```bash
python3 scripts/generate_agent_projections.py
python3 scripts/generate_hook_projections.py
```

## Available Skills

All ADK skills documented in `AGENTS.md` are available via the symlink installer. Skills are installed as symlinks from `.codex/skills/adk-*` to `skills/adk-*` in this repo.
