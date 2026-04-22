---
title: Installation
description: Install ADK as a Claude Code plugin from the marketplace (GitHub source, local clone, or npm source) or by pointing claude at the repo with --plugin-dir.
order: 1
---

# Installation

ADK is distributed as a Claude Code plugin via the marketplace at `.claude-plugin/marketplace.json`. The repo IS the [Claude Code plugin](https://code.claude.com/docs/en/plugins) — there is no parallel multi-harness install.

The marketplace exposes three install paths (all use the same `/plugin install` flow inside Claude Code):

| Path | Marketplace source | Plugin source | When to use |
| --- | --- | --- | --- |
| 1 | `sujeet-pro/agents-devkit` (GitHub) | `adk` — github | You want the latest commit on `main`. |
| 2 | `~/code/agents-devkit` (local) | `adk` — github | You have cloned the repo and want your edits to be live + refreshable through the standard `/plugin` lifecycle. |
| 3 | `sujeet-pro/agents-devkit` (GitHub) | `adk-npm` — npm | You want a semver-pinned, reproducible install (CI, locked environments). |

A fourth, dev-only path uses `claude --plugin-dir` to load the plugin directly without registering a marketplace.

## Requirements

- **Claude Code** — `brew install --cask claude-code` (macOS) or follow the [setup guide](https://code.claude.com/en/setup) for your OS.
- **`gh` CLI** — recommended for the publish / review skills. `brew install gh` and `gh auth login`.
- **Docker** — required only by the MCP servers (`github`, `bitbucket`, `jira`, `confluence`) that run as containers. Skip if you are not using those servers.
- Various env vars in `~/.zshenv` (or your shell rc) for MCP credentials. See [Configure MCP servers](#configure-mcp-servers) below.

## What the plugin ships

Every component below is loaded automatically by Claude Code when the plugin is enabled. No extra wiring step.

| Component            | Location                          | Spec |
| -------------------- | --------------------------------- | ---- |
| Manifest             | `.claude-plugin/plugin.json`      | [Plugin manifest](https://code.claude.com/docs/en/plugins-reference#plugin-manifest-schema) |
| Marketplace          | `.claude-plugin/marketplace.json` | [Marketplace](https://code.claude.com/docs/en/plugin-marketplaces#marketplace-schema) |
| Skills               | `skills/<name>/SKILL.md`          | [Skills](https://code.claude.com/docs/en/skills) |
| Subagents            | `agents/<role>.md`                | [Subagents](https://code.claude.com/docs/en/sub-agents) |
| Hooks                | `hooks/hooks.json`                | [Hooks](https://code.claude.com/docs/en/hooks-guide) |
| MCP servers          | `.mcp.json`                       | [MCP](https://code.claude.com/docs/en/mcp) |
| Background monitors  | `monitors/monitors.json`          | [Monitors](https://code.claude.com/docs/en/plugins-reference#monitors) |
| Plugin defaults      | `settings.json`                   | [Settings](https://code.claude.com/docs/en/plugins-reference#file-locations-reference) |
| Bundled CLIs         | `bin/adk-*`                       | [Executables](https://code.claude.com/docs/en/plugins-reference#file-locations-reference) — auto-added to `PATH` |
| System-prompt primer | `bin/canonical/system-prompt.md`  | Injected via `SessionStart` hook of type `command` |

## Path 1 — From the marketplace (GitHub, tracks `main`) — recommended

In Claude Code:

```text
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@sujeet-pro-adk
/reload-plugins
```

The default `adk` entry uses a `github` source with no pinned `ref` or `sha`, so it always tracks the **latest commit on `main`**. To pull in new commits:

```text
/plugin marketplace update sujeet-pro-adk
/reload-plugins
```

To pin the marketplace itself to a specific branch or tag, append `@<ref>` when adding it:

```text
/plugin marketplace add sujeet-pro/agents-devkit@v1.1.0
```

## Path 2 — From a local clone (contributors / live edits)

Use this when you have **cloned the repo** and want Claude Code to install ADK through the regular plugin lifecycle (so `/plugin install`, `/plugin update`, `/plugin disable`, and `/plugin uninstall` all work) **and** keep using your local working tree as the source.

### One-time setup

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
```

```text
# Inside Claude Code, point the marketplace at your local clone:
/plugin marketplace add ~/code/agents-devkit
/plugin install adk@sujeet-pro-adk
/reload-plugins
```

The marketplace name (`sujeet-pro-adk`) is read from `.claude-plugin/marketplace.json`, so the install command is identical to the GitHub path — only the **source** of the marketplace is different.

### Iterate on the plugin

```text
# After editing skills/<name>/SKILL.md, agents/<role>.md, hooks/hooks.json,
# .mcp.json, monitors/monitors.json, or .claude-plugin/plugin.json:
/reload-plugins
```

`/reload-plugins` re-reads every plugin component from disk, so your edits show up live without re-installing.

### Refresh after pulling

```bash
cd ~/code/agents-devkit
git pull
```

```text
/plugin marketplace update sujeet-pro-adk
/reload-plugins
```

## Path 3 — From the npm registry (semver-pinned)

The marketplace also exposes an `adk-npm` entry whose source is the [`agents-devkit`](https://www.npmjs.com/package/agents-devkit) npm package. Use this when you want a pinned, reproducible install — for example in CI or when standardizing across a team — instead of tracking `main`.

```text
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk-npm@sujeet-pro-adk
/reload-plugins
```

Behind the scenes Claude Code runs `npm install` against the public npm registry. To pin an exact version, install through the interactive `/plugin` UI (which lets you set version constraints) or via the CLI:

```bash
claude plugin install adk-npm@sujeet-pro-adk
```

The marketplace entry is configured per the [npm plugin source spec](https://code.claude.com/docs/en/plugin-marketplaces#npm-packages):

```json
{
  "name": "adk-npm",
  "source": {
    "source": "npm",
    "package": "agents-devkit"
  }
}
```

To pin a private registry, set the `version` and `registry` fields on a fork of the marketplace.

> [!NOTE]
> The npm package and the GitHub repo ship the same files — the npm tarball is just a release-tagged snapshot. The Claude plugin layout (`.claude-plugin/plugin.json`, `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `monitors/monitors.json`, `bin/`) is identical. Choose Path 1 for "always latest" or Path 3 for "pinned and reproducible".

## Path 4 — Direct (`--plugin-dir`, no marketplace)

For one-off plugin development against a clone, without registering a marketplace:

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
claude --plugin-dir "$(pwd)"
```

You can pass `--plugin-dir` multiple times to load several plugins at once. See [Test your plugins locally](https://code.claude.com/docs/en/plugins#test-your-plugins-locally).

## Configure MCP servers

`.mcp.json` declares MCP servers with `${ENV_VAR}` placeholders. Claude Code resolves them from your shell environment when it starts the server, so set the credentials in `~/.zshenv` (or your shell's equivalent) **before** launching Claude Code.

| Server | Env vars |
| --- | --- |
| `github` | `GITHUB_PAT` |
| `bitbucket` | `BITBUCKET_USERNAME`, `BITBUCKET_APP_PASSWORD` |
| `jira` / `confluence` | `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`, `JIRA_BASE_URL` / `CONFLUENCE_BASE_URL` |
| `google-drive` | `GDRIVE_CREDENTIALS_PATH` |
| `slack` | `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID` |
| `gmail` | `GMAIL_CREDENTIALS_PATH` |
| `datadog` | `DD_API_KEY`, `DD_APP_KEY`, `DD_SITE` |
| `mixpanel` | `MIXPANEL_PROJECT_ID`, `MIXPANEL_SERVICE_ACCOUNT_USER`, `MIXPANEL_SERVICE_ACCOUNT_SECRET` |
| `chrome-devtools`, `cursor-ide-browser`, `playwright`, `brainstorming` | none |

Servers whose env vars are missing simply fail to start; the dependent ADK skills fall back to documented CLI alternatives (`gh`, `npx playwright`, etc.) where available.

## Scripting / CI: non-interactive `claude plugin` CLI

Every `/plugin` slash command has a non-interactive `claude plugin` CLI equivalent (see the [CLI reference](https://code.claude.com/docs/en/plugins-reference#cli-commands-reference)):

```bash
# Add the marketplace
claude plugin marketplace add sujeet-pro/agents-devkit

# Pin to a branch or tag
claude plugin marketplace add sujeet-pro/agents-devkit@main

# Add from a local clone
claude plugin marketplace add ~/code/agents-devkit

# Install the plugin (user scope by default)
claude plugin install adk@sujeet-pro-adk

# Or install the npm-pinned variant
claude plugin install adk-npm@sujeet-pro-adk

# Project-scoped install (writes to .claude/settings.json so the team picks it up)
claude plugin install adk@sujeet-pro-adk --scope project

# Update / refresh
claude plugin marketplace update sujeet-pro-adk

# Inspect
claude plugin list
claude plugin list --json --available

# Validate a marketplace or plugin checkout
claude plugin validate .

# Remove
claude plugin uninstall adk@sujeet-pro-adk
claude plugin marketplace remove sujeet-pro-adk
```

Background auto-updates against the `sujeet-pro/agents-devkit` GitHub source work without an interactive credential helper if you export `GITHUB_TOKEN` (or `GH_TOKEN`) — see [Private repositories](https://code.claude.com/docs/en/plugin-marketplaces#private-repositories) in the marketplaces guide. The repo is public, so this only matters for forks hosted in private repos.

## Verify

In Claude Code:

```text
/plugin
```

Open the **Installed** tab and confirm `adk@sujeet-pro-adk` is enabled with no errors. Then try:

```text
/help
```

Skills should appear under the `adk` namespace (`/adk:auto`, `/adk:plan-brainstorm`, …).

## Updating

```text
# GitHub-source install (tracks main)
/plugin marketplace update sujeet-pro-adk
/reload-plugins
```

```bash
# Local-clone install
cd ~/code/agents-devkit
git pull
```

```text
/plugin marketplace update sujeet-pro-adk
/reload-plugins
```

```text
# npm-source install (pin to a new semver)
/plugin marketplace update sujeet-pro-adk
/plugin install adk-npm@sujeet-pro-adk     # picks up the latest published version
/reload-plugins
```

## Uninstall

```text
/plugin uninstall adk@sujeet-pro-adk
/plugin marketplace remove sujeet-pro-adk
```

The clone (if any) stays put — delete it manually when you no longer need it.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `/adk:` commands missing in Claude | Plugin not loaded or marketplace not added | `/plugin marketplace list`, `/plugin install adk@sujeet-pro-adk`, `/reload-plugins` |
| Skills present but MCP tools missing | `${ENV_VAR}` missing in shell environment | Add the exports to `~/.zshenv` (see [Configure MCP servers](#configure-mcp-servers)), restart Claude Code |
| Plugin loads but shows errors | Stale plugin cache | `rm -rf ~/.claude/plugins/cache`, restart Claude Code, reinstall the plugin |
| Plugin not seen after edits to a clone | Marketplace not refreshed | `/plugin marketplace update sujeet-pro-adk`, then `/reload-plugins` |

## Next

- [First skill](./first-skill.md) — run `/adk:auto` on a real task.
- [Memory files](../../concepts/memory-files.md) — how `CLAUDE.md` composes with the plugin.
- [Reference](../../reference/skills/README.md) — one page per skill, agent, hook, MCP server, and CLI script.
