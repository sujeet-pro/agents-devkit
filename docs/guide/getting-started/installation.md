---
title: Installation
description: Clone the repo, run install.sh per agent, set env vars, scaffold overrides.yaml. Full walkthrough for Claude Code, Cursor, Codex CLI, and Junie.
order: 2
---

# Installation

`adk` is a clone-and-link repo. No marketplace install, no `/plugin install`. One `install.sh` per agent target.

## Requirements

- **macOS** primary; **Linux** works with the same tools. Windows is unsupported.
- CLI: `gh`, `jq`, `fd`, `ripgrep`, `fzf`, `node` ≥ 18, `uv`, `python3` ≥ 3.10.

```bash
brew install gh jq fd ripgrep fzf node uv python@3.12
gh auth login
```

| Tool | Why |
|---|---|
| `gh` | Primary GitHub transport (MCP fallback chain: hosted MCP → `gh` CLI → direct REST). |
| `jq` | JSON wrangling in shell. |
| `node` ≥ 18 | Slack MCP runs via `npx`. |
| `uv` | Atlassian MCP runs via `uvx`. |
| `python3` | `scripts/*.py` + `install.py`. |
| `fd`, `rg`, `fzf` | Used by various skills for fast file ops. |

## Clone

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
```

Pick any directory. Symlinks point at this clone, so `git pull` propagates updates instantly.

## Env vars

Add to `~/.zshenv` (or `~/.bashrc` on bash). **Restart your agent** after editing — env is read at process start.

```bash
# GitHub — fine-grained PAT (preferred) or classic
export GITHUB_TOKEN_CRED="github_pat_..."

# Datadog
export DATADOG_API_KEY_CRED="..."
export DATADOG_APP_KEY_CRED="..."
export DD_SITE="datadoghq.com"                  # or datadoghq.eu / us3.* / us5.* / ap1.* / ap2.*

# Statsig
export STATSIG_CONSOLE_API_KEY_CRED="console-..."

# Atlassian (Jira + Confluence, via uvx mcp-atlassian)
export ATLASSIAN_SITE="acme.atlassian.net"      # bare host, no scheme, no /wiki
export ATLASSIAN_USERNAME="you@acme.com"
export ATLASSIAN_API_TOKEN_CRED="ATATT..."

# Mixpanel — OAuth on first MCP connect; no env var needed.

# Snowflake (optional — only used by /adk-investigate --use snowflake)
export SNOWFLAKE_ACCOUNT="..."
export SNOWFLAKE_USER="..."
export SNOWFLAKE_PASSWORD="..."                 # or SSO with SNOWFLAKE_AUTHENTICATOR=externalbrowser
export SNOWFLAKE_WAREHOUSE="..."
export SNOWFLAKE_ROLE="..."

# Looker (optional)
export LOOKER_BASE_URL="https://acme.cloud.looker.com"
export LOOKER_CLIENT_ID="..."
export LOOKER_CLIENT_SECRET_CRED="..."

# Slack — shell-sourceable file (chmod 600) that exports SLACK_BOT_TOKEN and/or SLACK_USER_TOKEN
export SLACK_CREDENTIALS_FILE="$ADK_CONFIG_HOME/slack-credentials.sh"

# RAG — optional company knowledge base MCP
export RAG_MCP_URL="https://your-rag.example.com/mcp"
export RAG_MCP_TOKEN_CRED="..."
```

The Slack credentials file template:

```bash
# $ADK_CONFIG_HOME/slack-credentials.sh — chmod 600
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_USER_TOKEN="xoxp-..."     # optional
```

```bash
chmod 600 $ADK_CONFIG_HOME/slack-credentials.sh
```

## install.sh

```bash
./install.sh                            # autodetect installed agents + wire them up
./install.sh --target claude            # one agent
./install.sh --target claude,cursor     # several
./install.sh --target all               # everyone, even unstubbed
./install.sh --uninstall                # remove everything by marker
./install.sh --dry-run                  # show what would change
```

What it does:

1. Creates `$ADK_CONFIG_HOME/` skeleton (learning/, metadata/, memory/).
2. Symlinks `skills/adk-*` + `agents-claude/agents/*` + `agents-claude/commands/*` into the agent's config dir.
3. Merges `mcp/*.json` into the agent's MCP config (idempotent, JSON merge).
4. Appends a marker block to the agent's global guidelines file pointing at `<repo>/AGENTS.md`.
5. (Claude only) Merges `hooks/hooks.json` into `~/.claude/settings.json` `hooks` block with `_adk_managed: true` markers.
6. Seeds `$ADK_DATA_HOME/improve/learning/decisions.jsonl` from `shared/seed-decisions.jsonl` on first install (so `/adk-improve` has evidence from day one).
7. Prints a verification table.

## Per-agent install paths

| Agent | What `install.sh` writes |
|---|---|
| Claude Code | `~/.claude/skills/adk-*` (symlinks), `~/.claude/agents/adk-agent-*.md` (symlinks), `~/.claude/commands/adk-*.md` (symlinks), `~/.claude/settings.json` (mcpServers + hooks merged), `~/.claude/CLAUDE.md` (`@<repo>/AGENTS.md` pointer) |
| Cursor | `~/.cursor/rules/adk-*.mdc` (symlinks), `~/.cursor/rules/_adk.mdc` (always-rule pointer), `~/.cursor/mcp.json` (merged) |
| Codex CLI | `~/.codex/prompts/adk-*.md` (symlinks), `~/.codex/config.toml` (mcp_servers block), `~/.codex/instructions.md` (pointer) |
| Junie | `~/.junie/guidelines.md` (pointer append), `agents-junie/junie-mcp.json.snippet` (paste manually into Junie settings) |

See per-env caveats in [Multi-agent setup](../usage/multi-agent.md).

## Bootstrap configuration

`install.sh` handled the **wiring**. `/adk-setup` (which you run inside your agent) handles your **user-level config**.

| `install.sh` (shell, deterministic) | `/adk-setup` (inside agent, conversational) |
|---|---|
| Symlink skills + agents + commands | Scaffold `$ADK_CONFIG_HOME/overrides.yaml` |
| Merge MCP configs | Query MCPs and build the metadata cache |
| Wire hooks (Claude only) | Verify env + MCP reachability (incl. stdio MCPs) |
| Append `AGENTS.md` pointer | — |

`/adk-setup` does NOT install brew packages — that's your job (see §Requirements above). It does NOT modify your shell rc — env vars are yours to add.

After install, scaffold your overrides file:

```text
/adk-setup --init             # conversational scaffolding of overrides.yaml + v2 migrate if found
```

Edit `$ADK_CONFIG_HOME/overrides.yaml` to fill workspaces, repos, and data sources. See [overrides.yaml](../usage/overrides-yaml.md) for the schema.

Then enrich + verify:

```text
/adk-setup --enrich           # query every reachable MCP, populate enriched.* + metadata cache
/adk-setup --check            # verify env + MCPs reachable (also tests stdio MCPs via real MCP-client invocation)
/adk-setup --diff             # read-only preview of --enrich
```

`--check` is a superset of `python3 scripts/adk_mcp_health.py --probe`: it also invokes stdio MCPs (Atlassian via uvx, Slack via npx, Snowflake) using the agent's MCP client — which curl-based probing can't reach — and offers conversational guidance to fix anything broken.

## Update later

`git pull` propagates everything since symlinks point at the clone. No re-install needed for content changes.

```bash
cd ~/code/agents-devkit
git pull
```

If `install.sh` itself or any wrapper template changed, re-run install:

```bash
./install.sh --target claude --dry-run     # preview
./install.sh --target claude               # apply
```

## Uninstall

```bash
./install.sh --uninstall --target claude
```

Removes all `adk-*` symlinks, strips the marker block from `CLAUDE.md`, removes `_adk_managed` hook entries. Your `$ADK_CONFIG_HOME/` data (overrides + decision log + metadata) is left untouched.

## Verify

```text
/adk-setup --check
```

Sample output (good):

```
[adk:setup --check]
agents:
  - claude    ✓ installed
  - cursor    ✓ installed
  - codex     ✗ not detected (skipped)
  - junie     ✗ not detected (skipped)

mcps:
  - adk-mcp-github      ✓ reachable
  - adk-mcp-datadog     ✓ reachable
  - adk-mcp-statsig     ✓ reachable
  - adk-mcp-atlassian   ✓ reachable
  - adk-mcp-mixpanel    ⚠ not yet OAuthed — first call pops the browser
  - adk-mcp-slack       ✓ reachable
  - adk-mcp-snowflake   ✗ env missing: SNOWFLAKE_ACCOUNT
  - adk-mcp-looker      ✗ env missing: LOOKER_BASE_URL
  - adk-mcp-rag         ✗ disabled (rag.enabled: false in overrides)

overrides:
  workspaces: 2 configured
  repos: 5 configured
  data_sources.snowflake: 1 database, 3 schemas, 12 tables described
```

Or run the script directly:

```bash
python3 scripts/adk_mcp_health.py --probe
```

## Next

- [Multi-agent setup](../usage/multi-agent.md) — per-agent capabilities
- [overrides.yaml](../usage/overrides-yaml.md) — config schema
- [Project-scoped overrides](../usage/project-scoped.md) — `.adk/`, `.temp/<task-slug>/`
- [SETUP.md](https://github.com/sujeet-pro/agents-devkit/blob/main/SETUP.md) (repo source)
