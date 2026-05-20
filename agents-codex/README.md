# agents-codex/ — OpenAI Codex CLI wrappers

> **Partial support.** Codex's plugin/skill ecosystem is less mature than Claude or Cursor. This folder ships what works today and lists gaps explicitly.

## What works

- **MCP servers**: Codex CLI reads `[[mcp_servers]]` blocks from `~/.codex/config.toml`. `install.sh --target codex` auto-generates one block per `mcp/adk-mcp-*.json` (the shared source-of-truth used by Claude / Cursor / Junie too) and writes them between `# adk-marker:start` / `# adk-marker:end`. Re-running install replaces the block; uninstall strips it.
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

## Where MCP entries come from

`install.py:merge_mcp_into_codex` reads every `mcp/adk-mcp-*.json` and generates the corresponding `[[mcp_servers]]` TOML block (http URLs with `Authorization: Bearer ${VAR}` collapse to `authorization_token_env`; stdio servers get `command`/`args`/`[mcp_servers.env]`). To add a new MCP for Codex, drop a JSON file under `mcp/` and re-run `install.sh` — there's no Codex-specific file to edit.
