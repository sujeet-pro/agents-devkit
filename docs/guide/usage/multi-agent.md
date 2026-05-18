---
title: Multi-agent setup
description: Capability matrix and per-agent caveats for Claude Code, Cursor, Codex CLI, and Junie.
order: 3
---

# Multi-agent setup

`adk` ships native wrappers for four agents. The same content (skills, agents, MCPs, shared guidelines) lives in one repo; `install.sh` translates it to each agent's expected format and location.

## Capability matrix

| Feature | Claude Code | Cursor | Codex CLI | Junie |
|---|---|---|---|---|
| Skills (8 polymorphic) | ✓ full — `~/.claude/skills/adk-*` (symlinks) | ✓ via rules — `~/.cursor/rules/adk-*.mdc` | ⚠ via prompts — `~/.codex/prompts/adk-*.md` | ⚠ via guidelines — `~/.junie/guidelines.md` pointer |
| Subagents (9 personas as agents) | ✓ full — `~/.claude/agents/adk-agent-*.md` | ⚠ inlined into rules | ✗ no separate subagent context | ✗ no separate subagent context |
| Slash commands | ✓ `~/.claude/commands/adk-*.md` (8 commands) | ⚠ Cursor's `/` palette per rule | ✗ invoke via `codex --prompt <name>` | ✗ invoke via Junie chat with explicit prompt |
| MCP merging | ✓ `~/.claude/settings.json` | ✓ `~/.cursor/mcp.json` | ✓ `~/.codex/config.toml` `[[mcp_servers]]` | ⚠ partial; IDE-version dependent. Snippet written to `agents-junie/junie-mcp.json.snippet` for manual paste |
| Hooks (PreToolUse / PostToolUse / SessionStart) | ✓ wired via `install.sh` | ✗ not supported | ✗ not supported | ✗ not supported |
| Skill auto-routing by description | ✓ Claude router reads description (1536-char cap) | ✓ Cursor's "agent-requested" rule mode | ✗ no router; invoke explicitly | ✗ no router; invoke explicitly |
| `paths:` glob frontmatter for auto-attach | n/a | ✓ Cursor uses `globs:` field | n/a | n/a |
| Global guidelines pointer (`AGENTS.md`) | ✓ `~/.claude/CLAUDE.md` append | ✓ `~/.cursor/rules/_adk.mdc` always-rule | ✓ `~/.codex/instructions.md` append | ✓ `~/.junie/guidelines.md` append |

## Claude Code

Full feature parity. The recommended primary agent.

- Skills installed to `~/.claude/skills/adk-*` (symlinks to `<repo>/skills/adk-*`).
- 9 subagents (code-reviewer, security-reviewer, investigator, doc-writer, doc-reviewer, implementer, test-engineer, context-gatherer, explainer) installed to `~/.claude/agents/`.
- 8 slash commands at `~/.claude/commands/adk-{implement,review,investigate,document,sync,setup,improve,explain}.md`.
- All 9 MCPs merged into `~/.claude/settings.json` (RAG skipped unless `RAG_MCP_URL` is set).
- Hooks merged with `_adk_managed: true` marker so they're idempotently updatable and removable.
- `~/.claude/CLAUDE.md` appended with a pointer to `<repo>/AGENTS.md` (idempotent, marker-based).

## Cursor

Solid coverage. Native `.mdc` rule format maps well to skills.

- 8 rules at `~/.cursor/rules/adk-*.mdc` (symlinks); each rule has a `description:` and `globs:` for auto-attach.
- One always-rule at `~/.cursor/rules/_adk.mdc` that points at `AGENTS.md`.
- All 9 MCPs merged into `~/.cursor/mcp.json`.
- **Caveats:** Cursor doesn't have a separate subagent context — `shared/personas/*` are inlined into the rules where relevant. Cursor doesn't have a hooks system equivalent to Claude Code's, so the constitution is enforced by advisor prose only when running in Cursor.

## Codex CLI

Partial. Codex's plugin/skill ecosystem is less mature than Claude or Cursor; we ship what works today and surface gaps honestly.

- 8 prompts at `~/.codex/prompts/adk-*.md` — invoke via `codex --prompt adk-implement` (or whatever Codex's prompt-invocation syntax becomes).
- All 9 MCPs appended as `[[mcp_servers]]` blocks in `~/.codex/config.toml`.
- `~/.codex/instructions.md` appended with the `AGENTS.md` pointer.
- **Gaps**: no skill auto-routing by description; no separate subagent context; no slash commands; no `--auto` / `--plan` flag enforcement beyond what's in the prompt body.

See `agents-codex/README.md` in the repo for the up-to-date capability table.

## Junie (JetBrains AI)

Shallow. Junie's MCP and rule story varies by IDE version.

- `~/.junie/guidelines.md` appended with the `AGENTS.md` pointer.
- `agents-junie/junie-mcp.json.snippet` written; **paste manually** into Junie settings.
- **Gaps**: no skill auto-routing; no separate subagent context; MCP wiring is manual; hooks not supported.

See `agents-junie/README.md` for the up-to-date list of what works.

## When to use which agent

| Task | Best agent | Why |
|---|---|---|
| Multi-file refactor with strict edit-format discipline | **Claude Code** | Hooks enforce constitution; plan/act tool restriction is real; subagents stay in clean contexts |
| Quick inline edits in your IDE | **Cursor** | `globs:`-based auto-attach surfaces the right rule for the file you're in |
| CI / non-interactive context | **Codex CLI** | Headless invocation; no IDE required |
| JetBrains IDE work | **Junie** | Native to the IDE; limited adk integration but usable |

You can run multiple agents in parallel. `git pull` in `~/code/agents-devkit` updates all of them at once.

## Adding a new agent

If a new agent (Aider, OpenHands, Continue, etc.) comes along, add `agents-<env>/` and update `install.py` to handle it. The shared content in `shared/` doesn't need to change — only the per-env translation layer.

## Next

- [overrides.yaml](./overrides-yaml.md) — the single config file every agent reads
- [Project-scoped overrides](./project-scoped.md) — `<repo>/.adk/`, `<repo>/.temp/<task-slug>/`
