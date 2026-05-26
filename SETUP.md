# adk SETUP

## 1. CLI dependencies

```bash
brew install gh jq fd ripgrep fzf node uv python@3.12

# /adk-pr-review only (optional for the other skills):
brew install ollama
ollama pull nomic-embed-text                 # default embedding model
brew install scip                            # SCIP tooling (optional but recommended)
# Per-language SCIP indexers (install only the ones you need):
npm i -g @sourcegraph/scip-typescript        # TypeScript / JavaScript
pipx install scip-python                     # Python
brew install scip-go                         # Go
# scip-java: see https://github.com/sourcegraph/scip-java
pip install -r skills/adk-pr-review/scripts/requirements.txt   # lancedb + requests + pyarrow

gh auth login
```

| Tool | Why |
|---|---|
| `gh` | Primary GitHub transport (MCP fallback chain: hosted MCP → `gh` CLI → direct REST). |
| `jq` | JSON in shell (used by `scripts/`, `install.sh`). |
| `node` ≥ 18 | Runs Slack MCP (`npx slack-mcp-server`). |
| `uv` | Runs Atlassian MCP (`uvx mcp-atlassian@latest`). Install: `curl -LsSf https://astral.sh/uv/install.sh \| sh` or `brew install uv`. |
| `python@3.12` | `scripts/*.py` + `install.py` + `skills/adk-pr-review/scripts/*.py`. |
| `fd`, `rg`, `fzf` | Used by various skills for fast file ops. |
| `ollama` (optional) | **Required by `/adk-pr-review` only.** Local embeddings for code-index. Default model `nomic-embed-text` (768-dim). Other skills do not need ollama. |
| `scip-*` (optional) | **Used by `/adk-pr-review` for symbol resolution.** Missing binaries fall back to grep + chunker `parent_symbol` matching; the skill works without them, just less accurately. |
| `lancedb` (pip, optional) | **Required by `/adk-pr-review` only.** Vector store for the code-index. See `skills/adk-pr-review/scripts/requirements.txt`. |

## 2. Env vars

Add to `~/.zshenv` (or `~/.bashrc`). Reload your shell and **restart your agent** after editing (env is read at process start).

```bash
# Bitbucket Cloud — needed only for /adk-pr-review on Bitbucket PRs (and the adk-mcp-bitbucket MCP).
# Per the credential convention (constitution §VII), the env var name is
# BITBUCKET_TOKEN_CRED (the _CRED suffix is canonical; the script does NOT fall back
# to a non-suffixed name). Atlassian unified API token preferred — pair with
# BITBUCKET_USERNAME (your Atlassian account email) for HTTP Basic auth.
# Source from ~/.config/creds/bitbucket/creds.sh; don't inline the value here.
# Required: BITBUCKET_TOKEN_CRED, BITBUCKET_USERNAME
# Optional: BITBUCKET_WORKSPACE (default workspace for tools that take one)

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

1. Enforces an ADK-only agent profile before installing fresh files. It removes non-ADK skills/rules/prompts/MCP descriptor caches from Cursor, Claude, Codex, and Junie; deletes non-ADK plugin/import caches; and quarantines legacy ADK v2/v3 state under `$ADK_DATA_HOME/legacy/<timestamp>/`.
2. Creates `$ADK_CONFIG_HOME/` if missing and scaffolds minimal v5 templates (`core.json5`, `workspaces.json5`, `teams.json5`, etc.) — edit them to add your details. See §4.
3. Symlinks skills + agents + commands into each detected agent's config dir wherever the agent supports symlinks. Cursor requestable rules, Junie command files, and JSON/TOML config are generated deterministically because those formats need rendered absolute paths/content.
4. **Replaces** each agent's MCP server list with the `mcp/*.json` adk set: Claude → `~/.claude.json`, Cursor → `~/.cursor/mcp.json`, Codex → `~/.codex/config.toml` (marker block), Junie → `~/.junie/mcp/mcp.json`. Any pre-configured user MCPs are stashed under `_adkRemovedMcpServers` and put back on `--uninstall`.
5. Merges `shared/permissions/*` into each agent's settings file so all safe / read tool calls are auto-approved and only dangerous actions prompt. See `shared/permissions/README.md`.
6. Appends a one-line reference to `AGENTS.md` in each agent's global guidelines file.
7. Seeds `$ADK_MEMORY_HOME/learning/decisions.jsonl` with foundational design decisions (your earlier Q&A) so the first `/adk-improve` run has evidence.
8. Prints a JSON manifest of cleanup + install actions. In `--dry-run`, the same manifest is emitted with `would-*` statuses and no filesystem changes.

### ADK-only cleanup and repeatability

`install.sh` is safe to run repeatedly. Each run first clears stale/non-ADK agent integrations, then recreates the ADK state from `~/personal/agents-devkit`.

- Cursor: keeps only `~/.cursor/rules/_adk.mdc` and `~/.cursor/rules/adk-*.mdc`, removes Cursor skill/plugin caches, clears per-project MCP descriptor caches, and rewrites `~/.cursor/mcp.json` from `mcp/adk-mcp-*.json`.
- Claude: keeps only `adk-*` skills/agents/commands, removes plugin registries/caches/marketplaces, deduplicates ADK hooks, and rewrites `~/.claude.json` from `mcp/adk-mcp-*.json`.
- Codex: keeps only `adk-*` prompts, removes bundled/imported plugin skill caches, removes non-ADK MCP blocks from `~/.codex/config.toml`, then rewrites the ADK marker blocks.
- Junie: keeps only `adk-*` skills/commands, removes bundled/custom non-ADK skills, and rewrites `~/.junie/mcp/mcp.json`.

The cleanup is allowlisted to agent config directories and explicitly avoids credential stores such as `~/.config/creds`.

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
| Fill in `$ADK_CONFIG_HOME/{core.json5,workspaces.json5,repos.json5,connectors/*.json5}` (identity, workspaces, repos, data sources) | Edit the scaffolded templates directly, or run `/adk-setup --init` (in your agent) for a conversational walkthrough | Data dictionary needs your judgment. |
| Query MCPs and populate `$ADK_DATA_HOME/metadata/<source>.json` + propose `connectors/<name>.json5` updates | `/adk-setup --enrich` | Uses the agent's MCP client to invoke stdio MCPs (uvx/npx) that `curl` can't. AI summarizes large lists. |
| Verify env + MCPs reachable | `/adk-setup --check` or `python3 scripts/adk_mcp_health.py --probe` | The skill version also tests stdio MCPs via real MCP-client invocation and offers conversational fix-it guidance. The script is faster for repeated checks. |

```text
/adk-setup --init       # conversational walkthrough to fill $ADK_CONFIG_HOME/{core.json5,workspaces.json5,repos.json5,...}
/adk-setup --enrich     # query every reachable MCP, populate services/dashboards and metadata cache
/adk-setup --check      # superset of scripts/adk_mcp_health.py (also tests stdio MCPs)
/adk-setup --diff       # show what --enrich would change (read-only)
```

Edit `$ADK_CONFIG_HOME/core.json5` for your identity and defaults; `$ADK_CONFIG_HOME/workspaces.json5` for your workspaces; `$ADK_CONFIG_HOME/repos.json5` for the repos you work in; `$ADK_CONFIG_HOME/connectors/*.json5` for each data source (Snowflake/Looker/Mixpanel/Datadog/etc). The skills won't be useful until at least one workspace and one repo entry are filled.

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
$ADK_CONFIG_HOME/           # YOU edit — synced across machines
├── core.json5              # user identity, org, bot persona, defaults
├── workspaces.json5        # workspace definitions
├── teams.json5             # teams + members (cross-platform identities)
├── repos.json5             # repo definitions
├── services.json5          # service definitions
├── channels.json5          # Slack channel inventory
├── dashboards.json5        # dashboard links
├── datadog-apps.json5      # Datadog application config
├── statsig.json5           # Statsig project config
├── mixpanel.json5          # Mixpanel project config
├── snowflake.json5         # Snowflake connection config
├── atlassian.json5         # Atlassian config
├── relations.json5         # cross-entity graph (replaces links.json5)
├── connectors/             # one .json5 per data source (auth + source config)
├── adk-cli.json5           # adk pr-sync / pr-scan / pr-review-all config
└── pr-queue.json5          # PR-review queue (curated by adk pr-scan)

$ADK_MEMORY_HOME/           # auto: cross-session learning state — synced
└── learning/               # decisions.jsonl + sessions/ + archive/ + proposals/

$ADK_DATA_HOME/             # auto: machine-local scratch — not synced
├── metadata/               # one <source>.json per MCP (regenerable)
├── repos/<name>/           # tracked repo clones + per-branch indices
├── skill-pr-review/        # one folder per PR being reviewed
├── skill-investigate/      # one folder per investigation
├── skill-review/  skill-sync/  skill-setup/  skill-improve/  skill-document/  skill-implement/  skill-explain/
└── logs/                   # CLI log output (pr-sync, pr-queue, …)
```

Inside any repo you work on:

```
<repo>/.adk/                  # optional repo-level overrides
<repo>/ai-guidelines/         # OR <repo>/docs/ — repo-specific conventions adk reads
<repo>/.temp/<task-slug>/     # gitignored; intermediate artifacts (plan, proposal, findings, report)
```

## 8. Privacy

- No skill ever uploads `$ADK_CONFIG_HOME/*` anywhere.
- Tokens live in `~/.zshenv` (or shell rc) only. `core.json5` / `connectors/*.json5` / `adk-cli.json5` can reference env var names but **must not** contain raw token values; a post-write hook enforces this with a regex check.
- Decision logs are local-only; `/adk-improve` proposals stay local until you accept them.
