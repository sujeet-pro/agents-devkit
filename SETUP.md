# adk — environment setup

This file walks through CLI dependencies, env vars, MCP setup, and per-user meta-info bootstrap. After completing these steps, every adk skill should run end-to-end on your machine.

> **Quick path:** if you already have `gh`, `jq`, `fd`, `rg`, `node`, `docker` installed, run `/adk-core:setup` from inside Claude Code. It walks every check below, tells you exactly what to add to your shell rc, and reports any connector setup still needed for Claude Desktop.

---

## 1. Platform

- **macOS** is the primary supported platform.
- **Linux** works with the same tools (replace `brew install` with `apt install` / `dnf install`).
- **Windows** is unsupported (use WSL2).

---

## 2. CLI dependencies

```bash
brew install gh jq fd ripgrep fzf node
brew install --cask docker
gh auth login              # one-time GitHub auth
```

| Tool | Why adk needs it |
| --- | --- |
| `gh` | GitHub CLI — fallback when the GitHub MCP isn't available; preferred for many ops |
| `jq` | JSON wrangling in shell (used by `bin/adk-info`, `bin/adk-mcp-health`) |
| `fd` | Fast file finding (used by some skills) |
| `ripgrep` (`rg`) | Fast in-file search (used everywhere) |
| `fzf` | Optional interactive picker for `adk-core:setup` |
| `node` ≥ 18 | Used by `bin/adk-info` (parses `~/.config/adk/*.md` to JSON) |
| `docker` | Optional. Used to be required by the GitHub MCP; the plugin now points at GitHub's hosted MCP (`api.githubcopilot.com/mcp/`), so Docker is no longer needed for adk itself |

---

## 3. Per-user meta-info — `~/.config/adk/*.md`

Every skill that needs company- or repo-specific facts reads them from `~/.config/adk/<topic>.md`. The `adk-core:setup` skill scaffolds these from templates the first time.

```text
/adk-core:setup                          # walk every topic
/adk-core:setup --target repos           # just one topic
```

The 10 topics:

| File | Owner skill(s) | Contents |
| --- | --- | --- |
| `info.md` | all | Operator name, email, role, default editor |
| `repos.md` | all | Repo → local-folder mapping; primary language; default base branch |
| `github.md` | `adk-review:*`, `adk-docs:docs-pr-description`, `adk-investigate:investigate-deploy` / incident / RCA | Default org, default reviewers, PR template path, CODEOWNERS conventions |
| `datadog.md` | `adk-investigate:investigate-datadog`, incident / experiment / RCA, `adk-code:code-perf` | Site (US/EU), default env, repo → service-name mapping, common dashboards/queries, SLO thresholds |
| `mixpanel.md` | `adk-investigate:investigate-mixpanel`, experiment, optional RCA user-impact pass | Project ID, important events, common funnels, common cohorts |
| `statsig.md` | `adk-investigate:investigate-statsig`, experiment, RCA | Project ID, common gates, common experiments, exposure metric conventions |
| `snowflake.md` | `adk-investigate:investigate-snowflake` | Default warehouse, default role, common schemas/pods, PII guardrail rules |
| `slack.md` | `adk-investigate:investigate-incident`, `investigate-rca` | Incident channel, deploys channel, on-call channel |
| `review.md` | `adk-review:*` | Severity bar overrides, comment template overrides, "ignore these checks for this repo" lists |
| `docs.md` | `adk-docs:*`, `adk-docs:docs-publish-*` | Default Confluence space, default GDrive folder, doc templates path |

Files are plain markdown with YAML front-matter. The `adk-info` bin script parses them into JSON for skill consumption. They live **only** on your machine — adk never uploads them.

---

## 4. Custom MCP servers (shipped by adk)

Four custom MCPs ship with adk because no claude.ai workspace connector covers them.

Claude Code can load these from each plugin's `.mcp.json`. Claude Desktop does not load plugin-local `.mcp.json`; configure the equivalent custom connector in Desktop before running a skill that requires it. If you are using a dry-run mode that does not need remote writes, you can tell the skill to skip a write-capability check, but the skill still verifies whatever read path is required to gather evidence.

### 4.1 GitHub — `plugins/adk-review/.mcp.json`

Points at GitHub's hosted/remote MCP at `https://api.githubcopilot.com/mcp/` (see [github/github-mcp-server](https://github.com/github/github-mcp-server)). No Docker, no local image. Read-only by default — the plugin's URL ends in `/readonly`. Skills that post (`review-pr`, `review-feedback`, `audit-pr` postback) prefer the `gh` CLI fallback rather than flipping to write mode.

**Authentication — PAT preferred, OAuth fallback:**

| Mode  | Setup                                                                                                                                                                                                                                       |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PAT   | Default. Set `GITHUB_PAT` in `~/.zshenv`; the plugin sends it as `Authorization: Bearer $GITHUB_PAT`.                                                                                                                                       |
| OAuth | Delete the `headers` block from `plugins/adk-review/.mcp.json`. Claude Code runs the OAuth flow on first connect (browser pop-up, then cached). No env var needed. Re-add the `headers` block to switch back. |

Claude Code's static `.mcp.json` does not branch on env-var presence, so there is no automatic "PAT if set, OAuth otherwise". Pick one by editing the headers block.

**Env vars (PAT mode):**

```bash
# https://github.com/settings/personal-access-tokens/new
# Required scopes: Contents:Read, Pull Requests:Read+Write, Issues:Read+Write,
#                  Actions:Read, Metadata:Read, read:org, read:project, notifications
export GITHUB_PAT="github_pat_..."
```

**Verifiers:**

```bash
# REST API surface check (PAT validity)
curl -sS -H "Authorization: Bearer $GITHUB_PAT" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/user | jq .login

# MCP endpoint reachability (expect 401 without auth, 200 with valid PAT)
curl -sS -o /dev/null -w "%{http_code}\n" -X POST \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{}}}' \
  https://api.githubcopilot.com/mcp/readonly
```

**Fallback:** every adk skill that uses this MCP also supports the `gh` CLI for the same operations. The `gh` path is preferred for write operations (already authenticated via `gh auth login`, and avoids the read-only / write-mode URL split).

### 4.2 Datadog — `plugins/adk-investigate/.mcp.json`

Datadog Bits AI MCP, hosted at `mcp.datadoghq.com` (Preview).

**Env vars:**

```bash
# https://app.datadoghq.com/organization-settings/api-keys
export DATADOG_API_KEY="..."
# https://app.datadoghq.com/organization-settings/application-keys
# Required scope: mcp_read (and mcp_write only if you actually need to mute monitors)
export DATADOG_APP_KEY="..."
# US1 = datadoghq.com (default); also: datadoghq.eu, us3.datadoghq.com,
# us5.datadoghq.com, ap1.datadoghq.com, ap2.datadoghq.com
export DD_SITE="datadoghq.com"
# Optional override (defaults to https://mcp.datadoghq.com/api/unstable/mcp-server/mcp)
# export DD_MCP_URL="..."
```

`DATADOG_API_KEY` / `DATADOG_APP_KEY` are the canonical names. Legacy
`DD_API_KEY` / `DD_APP_KEY` are also accepted: alias them in your shell rc so
the canonical `.mcp.json` wiring picks them up:

```bash
# legacy compat — only if you already have DD_* set
export DATADOG_API_KEY="$DD_API_KEY"
export DATADOG_APP_KEY="$DD_APP_KEY"
```

The plugin-local MCP config sends these values to Datadog using the current
MCP HTTP header names `DD_API_KEY` and `DD_APPLICATION_KEY` (the header names
on the wire, not the env var names you set). The REST API verifier below
still uses Datadog's standard REST headers with hyphens.

**Verifiers:**

```bash
# REST API surface check
curl -sS -G "https://api.${DD_SITE}/api/v2/logs/events" \
  -H "DD-API-KEY: $DATADOG_API_KEY" \
  -H "DD-APPLICATION-KEY: $DATADOG_APP_KEY" \
  --data-urlencode "filter[query]=*" \
  --data-urlencode "page[limit]=1" | jq '.meta'

# MCP endpoint reachability (expect 401 with no auth)
curl -sS -o /dev/null -w "%{http_code}\n" -X POST \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{}}}' \
  https://mcp.datadoghq.com/api/unstable/mcp-server/mcp
```

**Notes:**

- HIPAA-eligible. **NOT** GovCloud-eligible.
- Rate limits: 50 req/10s burst, 5,000 daily, 50,000 monthly tool calls.
- Tool surface (incident triage working set): `get_logs`, `aggregate_logs`, `list_spans`, `get_trace`, `get_metrics`, `list_metrics`, `get_monitors`, `list_incidents`, `get_incident`, `list_dashboards`, `error_tracking_*`, `feature_flags_*`.

### 4.3 Statsig — `plugins/adk-investigate/.mcp.json`

Statsig hosted MCP at `api.statsig.com/v1/mcp` (no public source repo).

**Env vars:**

```bash
# https://console.statsig.com/api_keys
# Type: Console; Scope: omni_read_only (use omni_write only if you actually toggle gates)
export STATSIG_CONSOLE_API_KEY="console-..."
```

**Verifiers:**

```bash
# REST API surface check
curl -sS https://statsigapi.net/console/v1/gates?limit=1 \
  -H "STATSIG-API-KEY: $STATSIG_CONSOLE_API_KEY" | jq '.data | length'

# MCP endpoint reachability (expect 200 if key valid, 401 otherwise)
curl -sS -o /dev/null -w "%{http_code}\n" -X POST \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -H "statsig-api-key: $STATSIG_CONSOLE_API_KEY" \
  --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{}}}' \
  https://api.statsig.com/v1/mcp
```

**Tool surface (PE working set):** `Get_Audit_Logs` (last 60m of changes — gold for "what broke prod"), `Get_List_of_Gates`, `Get_Gate_Details_by_ID`, `Get_Gate_Results`, `Get_List_of_Experiments`, `Get_Experiment_Details_by_ID`, `Get_Experiment_Results`, `List_Metrics`.

### 4.4 Bitbucket — `plugins/adk-review/.mcp.json`

Sibling to the GitHub MCP for teams whose code lives on Bitbucket Cloud (or who mirror across both hosts). Runs the npm-published [`bitbucket-mcp`](https://www.npmjs.com/package/bitbucket-mcp) package via `npx -y` (no Docker). Surface includes PR read / comment / approve, pipelines, branching model, and repo metadata.

> Note: the existing `adk-review` skills (`review-pr`, `review-feedback`, `audit-pr`) are written against GitHub. The Bitbucket MCP is shipped so you have it available in the same Claude Code session; downstream skill support is opportunistic for now.

**Env vars:**

```bash
# Bitbucket Cloud workspace access token (preferred) or app password
# https://bitbucket.org/account/settings/app-passwords/
export BITBUCKET_USERNAME="your-bitbucket-username"
export BITBUCKET_TOKEN="ATBB..."           # workspace access token or app password
```

**Verifier:**

```bash
# REST API surface check
curl -sS -u "$BITBUCKET_USERNAME:$BITBUCKET_TOKEN" \
  https://api.bitbucket.org/2.0/user | jq '.username'
```

---

## 5. claude.ai workspace connectors (consumed, not shipped)

Already enabled on Claude workspaces; **no `.mcp.json` entries needed**. Each adk skill that uses one falls back to a documented alternative if the connector isn't enabled on your workspace.

| Connector | Endpoint | adk skills consuming |
| --- | --- | --- |
| Atlassian (Rovo) | `https://mcp.atlassian.com/v1/mcp` | `adk-docs:docs-publish-confluence`, `adk-docs:docs-review`, `adk-investigate:investigate-incident` |
| Google Drive | `https://drivemcp.googleapis.com/mcp/v1` | `adk-docs:docs-publish-gdrive`, `adk-docs:docs-review` |
| Gmail | `https://gmailmcp.googleapis.com/mcp/v1` | `adk-investigate:investigate-incident` |
| Google Calendar | `https://calendarmcp.googleapis.com/mcp/v1` | `adk-investigate:investigate-incident` |
| Slack | `https://mcp.slack.com/mcp` | `adk-investigate:investigate-incident`, `adk-investigate:investigate-rca` |
| Mixpanel | `https://mcp.mixpanel.com/mcp` | `adk-investigate:investigate-mixpanel`, `adk-investigate:investigate-experiment` |
| Snowflake (e.g. Quince's QDP_SNOWFLAKE_MCP_SERVER) | per-workspace | `adk-investigate:investigate-snowflake` |

If your workspace doesn't have one of these, ask your Claude admin to enable it. The depending skill will stop with a clear error and tell you what to enable.

---

## 6. Adding env vars to your shell

Add the exports to `~/.zshenv` (or `~/.bashrc` on bash):

```bash
# adk env vars
export GITHUB_PAT="github_pat_..."   # omit to use OAuth instead (see §4.1)

export BITBUCKET_USERNAME="..."
export BITBUCKET_TOKEN="ATBB..."     # workspace access token or app password (§4.4)

export DATADOG_API_KEY="..."
export DATADOG_APP_KEY="..."
export DD_SITE="datadoghq.com"

export STATSIG_CONSOLE_API_KEY="console-..."
```

Then **reload your shell and restart Claude Code** (`source ~/.zshenv` is not enough — Claude Code reads env vars at process start).

> The `adk-core:setup` skill prints exactly these export lines for any env var that's missing. It does **NOT** modify your `~/.zshenv` automatically.

---

## 7. Verification

After all the above:

```text
/adk-core:setup --auto
```

This runs `bin/adk-mcp-health` and reports per-MCP / per-env-var status. Sample output:

```
[adk-mcp-health] platform=darwin
- workspace connectors:
  - Atlassian              ✓ Connected
  - Google Drive           ✓ Connected
  - Gmail                  ✓ Connected
  - Google Calendar        ✓ Connected
  - Slack                  ✓ Connected
  - Mixpanel               ✓ Connected
  - Snowflake (workspace)  ✓ Connected
- shipped MCPs:
  - github                 ✓ Connected (hosted, PAT auth)     [gh CLI: also available]
  - bitbucket              ✓ Connected (npx bitbucket-mcp)
  - datadog                ✓ Connected (https://mcp.datadoghq.com)
  - statsig                ✓ Connected (https://api.statsig.com/v1/mcp)

env vars referenced by adk plugins:
  - GITHUB_PAT              present
  - BITBUCKET_USERNAME      present
  - BITBUCKET_TOKEN         present
  - DATADOG_API_KEY         present
  - DATADOG_APP_KEY         present
  - DD_SITE                 present (datadoghq.com)
  - STATSIG_CONSOLE_API_KEY present
```

If any line is `MISSING` or `Not connected`, the report shows the exact `export` line or admin action to fix it.

---

## 8. Privacy & secrets

- Files under `~/.config/adk/` may reference `${ENV_VAR}` for secrets but **MUST NOT** contain raw tokens. The `setup` skill enforces this with a regex check.
- Tokens live in `~/.zshenv` (or your shell rc), **never** in `~/.config/adk/*.md`, **never** in the repo, **never** in a prompt.
- All meta-info is **local only**. No skill ever uploads these files anywhere.
- Per the 2026 plugin spec, secrets passed via `userConfig` with `sensitive: true` are routed to the OS keychain. `adk-core:setup` may use this path for users who prefer it; the default remains shell env vars.

---

## 9. Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `/adk-investigate:investigate-datadog` says "DD MCP not reachable" | `DATADOG_API_KEY` or `DATADOG_APP_KEY` missing in Claude Code's env (or you set legacy `DD_*` but never aliased them) | Add to `~/.zshenv`, restart Claude Code |
| GitHub MCP returns 401 / "needs authentication" | `GITHUB_PAT` not exported, expired, or missing scopes | Re-mint PAT (see §4.1), `export GITHUB_PAT=...` in `~/.zshenv`, restart Claude Code. Or remove the `headers` block from `plugins/adk-review/.mcp.json` to switch to OAuth. |
| Statsig MCP returns 401 | API key wrong scope | Mint a new key with `omni_read_only` scope |
| Workspace connector says "Not connected" | Workspace admin hasn't enabled it | Ask your Claude admin to enable Atlassian / Slack / etc. |
| `adk-info` outputs `unset` for a `${ENV_VAR}` field | env var not exported | Add the `export` line to `~/.zshenv`, restart shell + Claude Code |
| `/adk-core:setup` complains about an invalid `~/.config/adk/<topic>.md` | YAML front-matter parse error | Re-open the file, fix the YAML, re-run `setup --target <topic>` |

For deeper issues, run:

```text
/adk-core:info --check
```

This validates every meta-info file's schema and lists keys that skills want but aren't set.
