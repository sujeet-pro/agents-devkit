---
title: 'agents-codex'
description: 'adk wrappers for codex. See agents-codex/README.md (if present) for capability status.'
env: 'codex'
source: 'agents-codex/'
group: 'agent-envs'
order: 5002
---
# agents-codex

Wrappers that install adk into `codex` at user level. Installed via `./install.sh --target codex`.

### Prompts (8)

- `agents-codex/prompts/adk-document.md`
- `agents-codex/prompts/adk-explain.md`
- `agents-codex/prompts/adk-implement.md`
- `agents-codex/prompts/adk-improve.md`
- `agents-codex/prompts/adk-investigate.md`
- `agents-codex/prompts/adk-review.md`
- `agents-codex/prompts/adk-setup.md`
- `agents-codex/prompts/adk-sync.md`

### Append templates

- `agents-codex/codex-config.toml.append`

## README

# agents-codex/ — OpenAI Codex CLI wrappers

> **Partial support.** Codex's plugin/skill ecosystem is less mature than Claude or Cursor. This folder ships what works today and lists gaps explicitly.

## What works

- **MCP servers**: Codex CLI reads `[[mcp_servers]]` blocks from `~/.codex/config.toml`. `install.sh --target codex` appends our entries (one per `mcp/adk-mcp-*.json`, translated to TOML).
- **Custom prompts**: Codex supports `~/.codex/prompts/<name>.md` for invokable prompt templates. `install.sh` symlinks our `agents-codex/prompts/*.md` there.
- **Global instructions**: `~/.codex/instructions.md` gets a one-line append pointing at `AGENTS.md`.

## What's partial / unsupported

| Feature | Status | Workaround |
|---|---|---|
| Skill auto-routing by description | Not supported (Codex doesn't have skill matchers) | Invoke explicitly via prompt name |
| Subagents (separate persona context) | Not supported | All adk-agent-* personas concatenated into the parent prompt |
| Per-skill MCP scope | Not supported (global config only) | All MCPs available to all prompts |
| `--auto` / `--fix` mode flags | Implementation-dependent | Skill scripts respect `ADK_MODE` env var as fallback |
| Slash-command UX | Limited | Use `codex` CLI with `--prompt adk-implement` or similar |

## Verifying after install

```bash
codex --help 2>&1 | grep -i prompt    # confirm prompts loaded
cat ~/.codex/config.toml | grep -A2 'name = "adk-mcp-'  # confirm MCP entries
```

## Prompts shipped

| File | Skill it wraps |
|---|---|
| `prompts/adk-implement.md` | `/adk-implement` |
| `prompts/adk-review.md` | `/adk-review` |
| `prompts/adk-investigate.md` | `/adk-investigate` |
| `prompts/adk-document.md` | `/adk-document` |
| `prompts/adk-sync.md` | `/adk-sync` |
| `prompts/adk-setup.md` | `/adk-setup` |
| `prompts/adk-improve.md` | `/adk-improve` |
| `prompts/adk-explain.md` | `/adk-explain` |

## Config snippet appended to ~/.codex/config.toml

See `agents-codex/codex-config.toml.append` for the canonical block (with `{{ADK_REPO}}` placeholders that `install.py` substitutes).
