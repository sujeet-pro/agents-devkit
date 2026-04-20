---
title: Configuration Reference
description: Where ADK configuration lives, how it's installed, and how to validate it.
order: 3
---

# Configuration Reference

ADK configuration is split between the package itself and the install root the CLI writes into.

## Package surfaces

| Path | Purpose |
| --- | --- |
| `skills/<name>/` | One self-contained skill: `SKILL.md` + flat `references/` |
| `agents-claude/<name>.md` | Self-contained Claude custom subagent |
| `agents-cursor/<name>.md` | Self-contained Cursor custom subagent |
| `agents-codex/<name>.toml` | Self-contained Codex custom agent |
| `hooks/{claude,cursor,codex}.json` | Per-runtime hook config (independent files) |
| `mcp-config/servers/<name>.json` | One JSON per MCP server, with `${ENV_VAR}` placeholders |
| `global-prompts/<name>.md` | Always-on prompt that lands in the runtime memory file |
| `workflows/<name>.yaml` | Composable multi-skill pipeline (optional) |
| `skills-manifest.json` | Public catalog (regenerate with `npm run skills:manifest`) |

## Install root surfaces

`adk-install` writes here. `<root>` is `$HOME` for global mode and the project root for project mode.

| Path | Purpose |
| --- | --- |
| `<root>/.agents/skills/<name>` | Hub: managed `adk-*` symlinks + your own skill dirs |
| `<root>/.claude/skills/<name>` | Symlink to hub |
| `<root>/.cursor/skills/<name>` | Symlink to hub |
| `<root>/.codex/skills/<name>` | Symlink to hub |
| `<root>/.antigravity/skills/<name>` | Symlink to hub |
| `<root>/.junie/skills/<name>` | Symlink to hub |
| `<root>/.claude/agents/<name>.md` | Symlink to package's `agents-claude/<name>.md` |
| `<root>/.cursor/agents/<name>.md` | Symlink to package's `agents-cursor/<name>.md` |
| `<root>/.codex/agents/<name>.toml` | Symlink to package's `agents-codex/<name>.toml` |
| `<root>/.<runtime>/{settings,hooks,mcp}.json` | Hooks symlinked, MCP merged |
| `<root>/.<runtime>/<MEMORY>.md` | Managed `<!-- adk:global-prompts:start/end -->` block |

## Settings

| Scope | Path | Format | When |
| --- | --- | --- | --- |
| User | `~/.config/adk/settings.json5` | json5 | Always |
| Project | `<project>/.adk/settings.json5` | json5 | Only `--mode project` |

The user file also stores `knownPackagePaths`, used by Stage A to prune symlinks pointing to a previous install location after the package moves.

## Validation

```bash
npm run validate          # validate skills, agents, hooks
npm run skills:manifest   # regenerate skills-manifest.json
npm run setup:dry         # preview an install plan
npm run docs:build        # rebuild gh-pages/
```

## MCP

MCP is per-runtime and optional. See [`mcp-setup`](./mcp-setup.md) for the env-var workflow.

Skills that prefer an MCP server (brainstorming, github, bitbucket, confluence, gdrive) ship a `references/mcp-fallback.md` that warns once and runs the manual workflow when the server is missing.
