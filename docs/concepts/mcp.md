---
title: MCP Servers
description: When ADK uses Model Context Protocol servers, when it falls back to manual workflows, and how configs ship
order: 6
---

# MCP Servers

ADK skills prefer **direct runtime tool use** over custom MCP plumbing. Most skills do not need a dedicated MCP server to do their job well. The exception is a small set of workflow or connector skills where an MCP server unlocks structured state, authenticated APIs, or specialist tools the runtime does not have natively.

This page explains the ADK MCP policy, the shipped servers, and the optional brainstorming server that sits in a category of its own.

## The Policy

Three rules govern MCP use in ADK:

1. **Public skills must remain useful without any MCP server.** A missing MCP is never a hard failure. It must warn once and fall back to a manual workflow that still meets the skill's output contract.
2. **Workflow-specific MCP servers are allowed when they add real value.** `brainstorming` is the canonical example — it stores iterative design state across turns, which plain context cannot.
3. **Connector MCPs are allowed when they expose external systems.** `github`, `bitbucket`, `confluence`, `jira`, and `google-drive` live here. They exist because authenticated API access is cleaner through a dedicated MCP than through a shell-out every time.

What ADK does **not** ship:

- Public "setup" or "connector" skills whose only purpose is to wrap an MCP server. That work belongs in the runtime's own configuration.
- MCP wrappers around capabilities the runtime already provides natively (file reads, shell execution, web fetches).

## Shipped Server Configs

All pre-configured MCP server definitions live in [`mcp-config/servers/*.json`](https://github.com/sujeet-pro/agents-devkit/tree/main/mcp-config/servers). The installer reads this directory when you run `adk-install` and pick MCP servers in the prompt.

| Server | Service | Required env vars |
| --- | --- | --- |
| `github` | GitHub API | `GITHUB_PAT` |
| `bitbucket` | Bitbucket API | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| `confluence` | Atlassian Confluence | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| `jira` | Atlassian Jira | `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN` |
| `google-drive` | Google Drive | OAuth credentials (see server config) |
| `brainstorming` | Local structured brainstorming | `BRAINSTORMING_MCP_ROOT` pointing to a local `mcp-brainstorming` checkout |

## Per-Runtime Install Paths

| Runtime | Config path |
| --- | --- |
| Claude Code | `~/.claude/mcp.json` |
| Cursor | `.cursor/mcp.json` (project-level) |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Codex | `~/.codex/mcp.json` |

Install with:

```bash
adk-install                # interactive — pick the runtimes and the MCP servers
adk-install --dry-run      # preview only
```

The installer:

- Reads existing values from `~/.zshenv`.
- Prompts for any missing env vars with a one-line "how to get this" hint.
- Appends new exports to `~/.zshenv` (with confirmation).
- Merges each chosen server config into every selected runtime's `mcp.json`, preserving your pre-existing entries.

## Which Skills Use Which MCP

The connector skills prefer their matching MCP but also fall back to shell commands when the MCP is missing:

| Skill | Preferred MCP | Fallback |
| --- | --- | --- |
| `adk-publish-github`, `adk-review-pr` | `github` | `gh` CLI, then raw `git` + GitHub REST |
| `adk-publish-bitbucket` | `bitbucket` | `curl` + Bitbucket API |
| `adk-publish-confluence` | `confluence` | `curl` + Confluence API |
| `adk-publish-gdrive` | `google-drive` | Manual export |
| `adk-plan-brainstorm` | `brainstorming` | Manual workflow mirrored in the conversation |

Each connector skill is expected to warn once when its MCP is missing and continue with the manual path. A skill that silently does nothing because an MCP is missing is considered broken.

## The Brainstorming MCP Is Special

`brainstorming` is the only workflow-specific MCP ADK ships. It is *not* a connector to an external system. It is a local tool that stores structured brainstorming state (current task, options, confidence, route recommendation) so an ambiguous task can be iterated on across multiple turns without losing context.

Two things make it unusual:

1. **It is portable by design.** The server config uses `BRAINSTORMING_MCP_ROOT` instead of a machine-specific checkout path, so the same project-level `.cursor/mcp.json` works on multiple machines.
2. **Skills must degrade gracefully without it.** Each skill that prefers an MCP server ships its own `references/mcp-fallback.md` describing the exact fallback: warn once with install guidance, then mirror the same fields (`task`, `currentState`, `targetState`, `changeTolerance`, `desiredConfidence`, `artifactPreference`) manually in the conversation.

Installing it locally:

```bash
git clone https://github.com/sujeet-pro/mcp-brainstorming "$HOME/code/mcp-brainstorming"
adk-install                # pick `brainstorming` in the MCP step;
                           # the prompt asks for BRAINSTORMING_MCP_ROOT
                           # and persists it to ~/.zshenv
```

When `BRAINSTORMING_MCP_ROOT` is missing, the installed config fails with a clear error rather than pointing at a wrong path.

## Why Not Publish An `adk-mcp-*` Skill?

ADK deliberately does not publish public skills whose only job is to expose an MCP server or wire up a runtime. Runtimes already have their own MCP configuration UX. A public skill that wraps that wiring would duplicate work without owning a specialist job.

Instead:

- The runtime's native config owns MCP setup.
- `mcp-config/servers/*.json` provides reusable configs.
- `adk-install` merges them into the runtime's config.
- Consumer skills *use* MCP tools but do not require them.

## Summary

- MCP is optional for every public ADK skill.
- Each skill that prefers an MCP must warn once and fall back to a manual path.
- ADK ships connector configs for GitHub, Bitbucket, Confluence, Jira, Google Drive, plus the optional local `brainstorming` server.
- Runtime-specific MCP config paths and the `adk-install` interactive flow are the only plumbing you need.
- ADK does not ship public setup or wrapper skills for MCP — that responsibility belongs to the runtime.

## Related

- [Skill Anatomy](./skill-anatomy.md) — the self-sufficient-skill rule that makes MCP optional.
- [Philosophy](./philosophy.md) — the fallback requirement.
- [`mcp-config/README.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/mcp-config/README.md) — the raw installer-facing docs.
