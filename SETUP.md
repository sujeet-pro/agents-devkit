# adk SETUP

## 1. CLI dependencies

```bash
brew install gh jq fd ripgrep fzf node uv python@3.12
gh auth login
```

| Tool | Why |
|---|---|
| `gh` | Primary GitHub transport (MCP fallback chain: hosted MCP → `gh` CLI → direct REST). |
| `jq` | JSON in shell (used by `scripts/`, `install.sh`). |
| `node` ≥ 18 | Runs Slack MCP (`npx slack-mcp-server`). |
| `uv` | Runs Atlassian MCP (`uvx mcp-atlassian@latest`). Install: `curl -LsSf https://astral.sh/uv/install.sh \| sh` or `brew install uv`. |
| `python@3.12` | `scripts/*.py` + `install.py`. |
| `fd`, `rg`, `fzf` | Used by various skills for fast file ops. |

## 2. Env vars

Add to `~/.zshenv` (or `~/.bashrc`). Reload your shell and **restart your agent** after editing (env is read at process start).

```bash
# GitHub — fine-grained preferred; classic auto-fallback
export GITHUB_PAT="github_pat_..."
export GITHUB_PAT_CLASSIC="ghp_..."

# Datadog
export DATADOG_API_KEY="..."
export DATADOG_APP_KEY="..."
export DD_SITE="datadoghq.com"          # or datadoghq.eu, us3., us5., ap1., ap2.

# Statsig
export STATSIG_CONSOLE_API_KEY="console-..."

# Atlassian (Jira + Confluence; uvx mcp-atlassian)
export ATLASSIAN_SITE="acme.atlassian.net"    # bare host, no scheme, no /wiki
export ATLASSIAN_USERNAME="you@acme.com"
export ATLASSIAN_API_TOKEN="ATATT..."         # https://id.atlassian.com/manage-profile/security/api-tokens

# Mixpanel — OAuth on first MCP connect; no env var needed

# Snowflake (optional — only needed by /adk-investigate's snowflake sub-flow)
export SNOWFLAKE_ACCOUNT="..."
export SNOWFLAKE_USER="..."
export SNOWFLAKE_PASSWORD="..."               # or SSO; see mcp/README.md
export SNOWFLAKE_WAREHOUSE="..."
export SNOWFLAKE_ROLE="..."

# Looker (optional)
export LOOKER_BASE_URL="https://acme.cloud.looker.com"
export LOOKER_CLIENT_ID="..."
export LOOKER_CLIENT_SECRET="..."

# Slack — single file the MCP sources; file MUST export SLACK_BOT_TOKEN and/or SLACK_USER_TOKEN
export SLACK_CREDENTIALS_FILE="$HOME/.config/adk/slack-credentials.sh"

# RAG — optional company knowledge base MCP
export RAG_MCP_URL="https://your-rag.example.com/mcp"
export RAG_MCP_TOKEN="..."
```

Slack credentials file template (`~/.config/adk/slack-credentials.sh`):

```bash
# This file is sourced by the slack MCP wrapper. Chmod 600.
export SLACK_BOT_TOKEN="xoxb-..."     # required for posting + reading channels the bot is in
export SLACK_USER_TOKEN="xoxp-..."    # optional; full workspace read on your behalf
```

```bash
chmod 600 ~/.config/adk/slack-credentials.sh
```

## 3. Install

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
./install.sh                            # autodetect agents + wire them up
./install.sh --target claude            # one agent
./install.sh --target claude,cursor     # several
./install.sh --target all               # everyone, including stubs
./install.sh --uninstall                # removes everything by marker
./install.sh --dry-run                  # show what would change
```

The installer:

1. Creates `~/.config/adk/` if missing; scaffolds `overrides.yaml` (with comments — empty workspaces table for you to fill).
2. Symlinks skills + agents + commands into each detected agent's config dir.
3. Merges `mcp/*.json` into each agent's MCP config (idempotent JSON/TOML merge).
4. Appends a one-line reference to `AGENTS.md` in each agent's global guidelines file.
5. Seeds `~/.config/adk/learning/decisions.jsonl` with foundational design decisions (your earlier Q&A) so the first `/adk-improve` run has evidence.
6. Prints a verification table.

## 4. Bootstrap overrides

`install.sh` handles the **wiring** (symlinks, MCP merges, hooks). `/adk-setup` picks up where install.sh stops: filling your user-level **config** + introspecting MCPs.

Division of labor:

| Step | Who does it | Why |
|---|---|---|
| Install brew, gh, jq, uv, node, python | **You.** See §1 above. | adk doesn't run brew on your machine. |
| Export env vars in `~/.zshenv` | **You.** See §2 above. | adk doesn't modify shell rc. |
| Symlink skills/agents/commands; merge MCP config; wire hooks | `install.sh` | Filesystem wiring. Deterministic; no AI needed. |
| Scaffold `~/.config/adk/overrides.yaml` (workspaces, repos, data dictionary) | `/adk-setup --init` (in your agent) | Conversational walkthrough; data dictionary needs your judgment. |
| Query MCPs and populate `enriched:` block + `~/.config/adk/metadata/<source>.json` | `/adk-setup --enrich` | Uses the agent's MCP client to invoke stdio MCPs (uvx/npx) that `curl` can't. AI summarizes large lists. |
| Verify env + MCPs reachable | `/adk-setup --check` or `python3 scripts/adk_mcp_health.py --probe` | The skill version also tests stdio MCPs via real MCP-client invocation and offers conversational fix-it guidance. The script is faster for repeated checks. |

```text
/adk-setup --init       # scaffold ~/.config/adk/overrides.yaml with comments + v2 migrate if found
/adk-setup --enrich     # query every reachable MCP, populate the enriched.* block + metadata cache
/adk-setup --check      # superset of scripts/adk_mcp_health.py (also tests stdio MCPs)
/adk-setup --diff       # show what --enrich would change (read-only)
```

Edit `~/.config/adk/overrides.yaml` to fill in your workspaces (work + personal + side orgs), the repos you work in, and the data dictionary for Snowflake/Looker/Mixpanel. The skills won't be useful until at least `workspaces` and one `repos` entry are filled.

## 5. Verify

```text
/adk-setup --check
```

Sample output (good):

```
[adk:setup --check]
agents:
  - claude    ✓ installed   (~/.claude/skills/adk-* + ~/.claude/agents/adk-agent-*)
  - cursor    ✓ installed
  - codex     ✗ not detected (skipped)
  - junie     ✗ not detected (skipped)

mcps:
  - adk-mcp-github      ✓ reachable   (PAT auth)
  - adk-mcp-datadog     ✓ reachable
  - adk-mcp-statsig     ✓ reachable
  - adk-mcp-atlassian   ✓ reachable
  - adk-mcp-mixpanel    ⚠ not yet OAuthed — first /adk-investigate run will pop the browser
  - adk-mcp-slack       ✓ reachable   (bot token present)
  - adk-mcp-snowflake   ✗ env missing: SNOWFLAKE_ACCOUNT
  - adk-mcp-looker      ✗ env missing: LOOKER_BASE_URL
  - adk-mcp-rag         ✗ disabled    (rag.enabled: false in overrides)

overrides:
  workspaces: 2 configured
  repos: 5 configured
  data_sources.snowflake: 1 database, 3 schemas, 12 tables described
  defaults: present
```

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| Agent doesn't see `/adk-*` slash commands | re-run `./install.sh --target <agent>`; restart the agent |
| MCP returns 401 | check env var with `env \| grep <NAME>`; restart agent so it picks up the var |
| Atlassian MCP fails to start | `uv` not installed; run `brew install uv` |
| Slack MCP says "no token" | `SLACK_CREDENTIALS_FILE` not set, or the file doesn't export `SLACK_BOT_TOKEN`/`SLACK_USER_TOKEN`. `cat $SLACK_CREDENTIALS_FILE` to inspect (without leaking — the wrapper sources, doesn't print). |
| `/adk-improve` says "no decisions to analyze" | run a few skills first; decision logs accumulate |
| Cursor doesn't load adk MCPs | `./install.sh --target cursor` was project-scoped; either re-run with global flag or run in your project root |
| Junie shows partial behavior | see `agents-junie/README.md` for the capability table |

## 7. Layout

```
~/.config/adk/
├── overrides.yaml          # YOU edit this
├── env.example             # cheat-sheet
├── slack-credentials.sh    # YOU edit this (chmod 600)
├── metadata/               # auto: discovered dashboards, tables, etc.
├── learning/               # auto: decision logs, summaries, proposals
└── memory/                 # auto: resolved caches
```

Inside any repo you work on:

```
<repo>/.adk/                  # optional repo-level overrides
<repo>/ai-guidelines/         # OR <repo>/docs/ — repo-specific conventions adk reads
<repo>/.temp/<task-slug>/     # gitignored; intermediate artifacts (plan, proposal, findings, report)
```

## 8. Privacy

- No skill ever uploads `~/.config/adk/*` anywhere.
- Tokens live in `~/.zshenv` (or shell rc) only. `overrides.yaml` can reference env vars by name but **must not** contain raw token values; the installer enforces this with a regex check.
- Decision logs are local-only; `/adk-improve` proposals stay local until you accept them.
