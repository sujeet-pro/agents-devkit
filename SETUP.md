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
# GitHub — fine-grained PAT (preferred) or classic
export GITHUB_TOKEN_CRED="github_pat_..."

# Datadog
export DATADOG_API_KEY_CRED="..."
export DATADOG_APP_KEY_CRED="..."
export DD_SITE="datadoghq.com"          # or datadoghq.eu, us3., us5., ap1., ap2.

# Statsig
export STATSIG_CONSOLE_API_KEY_CRED="console-..."

# Atlassian (Jira + Confluence; uvx mcp-atlassian)
export ATLASSIAN_SITE="acme.atlassian.net"    # bare host, no scheme, no /wiki
export ATLASSIAN_USERNAME="you@acme.com"
export ATLASSIAN_API_TOKEN_CRED="ATATT..."         # https://id.atlassian.com/manage-profile/security/api-tokens

# Mixpanel — OAuth on first MCP connect; no env var needed

# Snowflake (optional — only needed by /adk-investigate's snowflake sub-flow)
export SNOWFLAKE_ACCOUNT="..."
export SNOWFLAKE_USER="..."
export SNOWFLAKE_PASSWORD="..."               # or SSO; see mcp/README.md
export SNOWFLAKE_WAREHOUSE="..."
export SNOWFLAKE_ROLE="..."

# Looker (optional)
export LOOKER_SITE="https://acme.cloud.looker.com"
export LOOKER_CLIENT_ID="..."
export LOOKER_CLIENT_SECRET_CRED="..."

# Google — required for `creds_login_google` to mint a token AND for the
# Google Workspace MCP. Same client_id/secret feeds both. Scopes requested
# at OAuth time live in ~/.config/creds/google/app.json.
export GOOGLE_CLIENT_ID="..."
export GOOGLE_CLIENT_SECRET_CRED="..."
# Optional: default email for the Workspace MCP single-user auth flow.
# export USER_GOOGLE_EMAIL="you@example.com"

# Slack — optional override; defaults to ~/.config/creds/slack/slack.token.json
# export SLACK_CREDENTIALS_FILE="$HOME/.config/creds/slack/slack.token.json"

# Slack — required for `creds_login_slack` to mint a token (from mac-setup)
export SLACK_CLIENT_ID="..."
export SLACK_CLIENT_SECRET_CRED="..."

# RAG — optional company knowledge base MCP
export RAG_MCP_URL="https://your-rag.example.com/mcp"
export RAG_MCP_TOKEN_CRED="..."
```

**Google Workspace MCP** (taylorwilsdon/google_workspace_mcp via `uvx workspace-mcp`) is wired with the same `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET_CRED` env vars. **First tool invocation opens a browser for the MCP's own OAuth dance** — tokens land in `~/.google_workspace_mcp/credentials/`. This is independent of `creds_login_google`'s `~/.config/creds/google/google.token.json` (used by `creds_validate` and other mac-setup scripts). Both can coexist. Make sure every scope in `~/.config/creds/google/app.json` is added to your GCP OAuth consent screen, or the dance fails with `invalid_scope`.

Slack credentials are JSON, minted by [`creds_login_slack`](https://github.com/sujeet-pro/mac-setup/tree/main/user_scripts/creds) (mac-setup):

```
~/.config/creds/slack/
├── app.json          # YOU edit this — scope superset requested at OAuth time
└── slack.token.json  # auto: written by creds_login_slack (chmod 600)
                      #       holds { bot_token: "xoxb-...", user_token: "xoxp-..." }
```

The Slack MCP wrapper reads `slack.token.json` directly — no shell sourcing, no env-var plumbing. Both tokens land in the server: `SLACK_MCP_XOXB_TOKEN` (bot) and `SLACK_MCP_XOXP_TOKEN` (user). Posting requires the bot token.

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
2. Symlinks skills + agents + commands into each detected agent's config dir. Junie now gets the full `skills/adk-*` set under `~/.junie/skills/` (same auto-discovery model as Claude Code).
3. **Replaces** each agent's MCP server list with the `mcp/*.json` adk set: Claude → `~/.claude.json`, Cursor → `~/.cursor/mcp.json`, Codex → `~/.codex/config.toml` (marker block), Junie → `~/.junie/mcp/mcp.json`. Any pre-configured user MCPs are stashed under `_adkRemovedMcpServers` and put back on `--uninstall`.
4. Merges `shared/permissions/*` into each agent's settings file so all safe / read tool calls are auto-approved and only dangerous actions prompt. See `shared/permissions/README.md`.
5. Appends a one-line reference to `AGENTS.md` in each agent's global guidelines file.
6. Seeds `~/.config/adk/learning/decisions.jsonl` with foundational design decisions (your earlier Q&A) so the first `/adk-improve` run has evidence.
7. Prints a verification table.

### Tool-call permissions

`./install.sh` writes a permission policy into each agent's settings so the
agent does **not** prompt on safe / read-only tool calls but **does** prompt
on dangerous actions (`rm`, `git push`, `git reset --hard`, `terraform
apply/destroy`, `kubectl delete`, `docker system prune`, `npm publish`, …).

The policy is sourced from `shared/permissions/`:

| File | Goes to |
|---|---|
| `shared/permissions/claude.json` | `~/.claude/settings.json` (`permissions.{allow,ask,deny,defaultMode}`) |
| `shared/permissions/cursor.json` | `~/.cursor/cli-config.json` (`permissions`, `approvalMode`, `sandbox`) |
| `shared/permissions/codex.toml`  | `~/.codex/config.toml` (marker block: `approval_policy`, `sandbox_mode`) |
| `shared/permissions/junie-allowlist.json` | `~/.junie/allowlist.json` (whole file, guarded by `"_adk_managed": true`) |

The merge is idempotent: re-running `./install.sh` refreshes the policy
without duplicating entries, and `./install.sh --uninstall` removes only the
entries adk added (user entries are preserved). To customise, edit the files
under `shared/permissions/` and re-run `./install.sh`.

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
  - adk-mcp-looker      ✗ env missing: LOOKER_SITE
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
| Slack MCP says "no token" | `~/.config/creds/slack/slack.token.json` missing or has no `bot_token` / `user_token`. Run `creds_login_slack` (mac-setup) to mint one. Override path with `SLACK_CREDENTIALS_FILE` if you store the file elsewhere. |
| `/adk-improve` says "no decisions to analyze" | run a few skills first; decision logs accumulate |
| Cursor doesn't load adk MCPs | `./install.sh --target cursor` was project-scoped; either re-run with global flag or run in your project root |
| Junie shows partial behavior | see `agents-junie/README.md` for the capability table |

## 7. Layout

```
~/.config/adk/
├── overrides.yaml          # YOU edit this
├── env.example             # cheat-sheet
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
