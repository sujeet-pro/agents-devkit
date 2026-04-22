---
title: MCP Servers
description: When ADK uses Model Context Protocol servers, when it falls back to manual workflows, and how the bundled .mcp.json registry works under the Claude plugin spec.
order: 6
---

# MCP Servers

ADK skills prefer **direct runtime tool use** over custom MCP plumbing. Most skills do not need a dedicated MCP server to do their job well. The exception is a small set of workflow or connector skills where an MCP server unlocks structured state, authenticated APIs, or specialist tools the runtime does not have natively.

This page explains the ADK MCP policy, the shipped registry, and how the Claude plugin loads it.

## The policy

Three rules govern MCP use in ADK:

1. **Public skills must remain useful without any MCP server.** A missing MCP is never a hard failure. The skill must warn once and fall back to a manual workflow that still meets the skill's output contract.
2. **Workflow-specific MCP servers are allowed when they add real value.** `brainstorming` is the canonical example — it stores iterative design state across turns, which plain context cannot.
3. **Connector MCPs are allowed when they expose external systems.** `github`, `bitbucket`, `confluence`, `jira`, `google-drive`, `slack`, `gmail`, `datadog`, `mixpanel` live here. They exist because authenticated API access is cleaner through a dedicated MCP than through ad-hoc shell-outs.

What ADK does **not** ship:

- Public "setup" or "connector" skills whose only purpose is to wrap an MCP server. That work belongs in the runtime's own configuration.
- MCP wrappers around capabilities the runtime already provides natively (file reads, shell execution, web fetches).

## How the Claude plugin loads MCP

The `adk` Claude Code plugin places its MCP registry at the [default plugin location](https://code.claude.com/docs/en/plugins-reference#standard-plugin-layout): a `.mcp.json` file at the plugin root. The server definitions follow the standard `mcpServers` map shape from the [Claude Code plugins reference — MCP servers](https://code.claude.com/docs/en/plugins-reference#mcp-servers).

When the plugin is enabled, every server in [`.mcp.json`](https://github.com/sujeet-pro/agents-devkit/blob/main/.mcp.json) is started automatically and its tools appear as standard MCP tools in Claude's toolkit. No separate "install MCP" step is required — the Claude plugin host owns it.

## Environment variable substitution

Most servers in `.mcp.json` need credentials. ADK uses the documented `${ENV_VAR}` substitution pattern Claude Code supports for MCP and LSP server configs (see [Environment variables](https://code.claude.com/docs/en/plugins-reference#environment-variables)):

```json
"github": {
  "command": "sh",
  "args": [
    "-c",
    "GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PAT docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server"
  ],
  "env": { "GITHUB_PAT": "${GITHUB_PAT}" }
}
```

`${GITHUB_PAT}` is read from the user's shell environment when Claude Code starts the server. Set the required exports in `~/.zshenv` (or your shell's equivalent) **before** launching Claude Code. The `/adk:setup` skill walks the env vars referenced by `.mcp.json` and reports which are present, missing, or wired correctly.

> [!NOTE]
> The Claude plugin spec also supports a `userConfig` field that prompts the user for values when the plugin is enabled (substituted as `${user_config.KEY}`). ADK currently uses `${ENV_VAR}` so the same shell env can be shared with `gh`, `docker`, and other CLI tools.

## Shipped servers

| Server | Service | Required env vars |
| --- | --- | --- |
| `github` | GitHub API (preferred over `gh` CLI for some skills) | `GITHUB_PAT` |
| `bitbucket` | Bitbucket Cloud | `BITBUCKET_USERNAME`, `BITBUCKET_APP_PASSWORD` |
| `jira` | Atlassian Jira | `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`, `JIRA_BASE_URL` |
| `confluence` | Atlassian Confluence | `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`, `CONFLUENCE_BASE_URL` |
| `google-drive` | Google Drive | `GDRIVE_CREDENTIALS_PATH` |
| `slack` | Slack | `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID` |
| `gmail` | Gmail | `GMAIL_CREDENTIALS_PATH` |
| `datadog` | Datadog | `DD_API_KEY`, `DD_APP_KEY`, `DD_SITE` |
| `mixpanel` | Mixpanel | `MIXPANEL_PROJECT_ID`, `MIXPANEL_SERVICE_ACCOUNT_USER`, `MIXPANEL_SERVICE_ACCOUNT_SECRET` |
| `chrome-devtools` | Chrome DevTools (preferred for `validate-browser`) | none |
| `cursor-ide-browser` | Cursor's bundled browser MCP (2nd pick) | none |
| `playwright` | Playwright (3rd-pick fallback) | none |
| `brainstorming` | Local brainstorming session store | none (npm-resolved) |

## Which skills use which MCP

The connector skills prefer their matching MCP but also fall back to shell commands when the MCP is missing:

| Skill | Preferred MCP | Fallback |
| --- | --- | --- |
| `adk-publish-github`, `adk-review-pr` | `github` | `gh` CLI, then raw `git` + GitHub REST |
| `adk-publish-bitbucket` | `bitbucket` | `curl` + Bitbucket API |
| `adk-publish-confluence` | `confluence` | `curl` + Confluence API |
| `adk-publish-gdrive` | `google-drive` | Manual export |
| `adk-validate-browser` | `chrome-devtools` → `cursor-ide-browser` → `playwright` | Manual screenshot guidance |
| `adk-observability-datadog`, `adk-observability-incident` | `datadog` | `curl` + Datadog API |
| `adk-analytics-mixpanel` | `mixpanel` | `curl` + Mixpanel API |
| `adk-plan-brainstorm` | `brainstorming` | Manual workflow mirrored in the conversation |

Each connector skill is expected to warn once when its MCP is missing and continue with the manual path. A skill that silently does nothing because an MCP is missing is considered broken (the validator flags this).

## Why not publish an `adk-mcp-*` skill?

ADK deliberately does not publish public skills whose only job is to expose an MCP server or wire up a runtime. The Claude plugin format owns MCP setup natively for Claude Code via `.mcp.json` — a public skill that wraps that wiring would duplicate work without owning a specialist job.

## Summary

- MCP is optional for every public ADK skill.
- Each skill that prefers an MCP must warn once and fall back to a manual path.
- The Claude plugin loads `.mcp.json` automatically — no extra wiring step.
- Credentials use `${ENV_VAR}` substitution sourced from your shell environment (typically `~/.zshenv`).

## Related

- [Skill Anatomy](./skill-anatomy.md) — the self-sufficient-skill rule that makes MCP optional.
- [Philosophy](./philosophy.md) — the fallback requirement.
- [Plugins reference — MCP servers](https://code.claude.com/docs/en/plugins-reference#mcp-servers) — Anthropic's authoritative spec.
