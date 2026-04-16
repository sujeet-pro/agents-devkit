# MCP Setup

MCP is optional for the public `npx skills` catalog.

## Current Model

- public skills must remain useful without plugin packaging
- runtime-specific MCP configuration is handled by the target agent
- repo maintenance guidance lives in `AGENTS.md` and `ai-guidelines/`
- workflow-specific MCP servers may be preferred when available, but they must have a warning path and a manual fallback

## Repo Guidance

Use per-runtime configuration files for MCP, for example:

- Claude Code: `~/.claude.json` or project `.mcp.json`
- Cursor: `~/.cursor/mcp.json` or project `.cursor/mcp.json`
- Codex: `~/.codex/config.toml`

## Rule

Do not make public ADK skills depend on plugin-scoped MCP wiring.

## Brainstorming MCP

The `brainstorming` MCP server is the default structured state layer for design-before-implementation work, but it is still optional for the public catalog.

- skills should prefer it when available
- skills must warn once and continue with the shared manual brainstorming workflow when it is missing
- tracked config must stay portable, so use `BRAINSTORMING_MCP_ROOT` instead of a machine-specific checkout path