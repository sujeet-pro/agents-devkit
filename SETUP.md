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
| `docker` | Required by the GitHub MCP (which runs as a Docker container). Optional if you use the `gh` CLI fallback only |

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

Three custom MCPs ship with adk because no claude.ai workspace connector covers them.

Claude Code can load these from each plugin's `.mcp.json`. Claude Desktop does not load plugin-local `.mcp.json`; configure the equivalent custom connector in Desktop before running a skill that requires it. If you are using a dry-run mode that does not need remote writes, you can tell the skill to skip a write-capability check, but the skill still verifies whatever read path is required to gather evidence.

### 4.1 GitHub — `plugins/adk-review/.mcp.json`

Single canonical implementation: GitHub's own `github/github-mcp-server`, distributed only as a Docker image on GHCR. Pinned to `v1.0.3`.

**Env vars:**

```bash
# https://github.com/settings/personal-access-tokens/new
# Required: Contents:Read, Pull Requests:Read+Write, Issues:Read+Write,
#           Actions:Read, Metadata:Read, read:org, read:project, notifications
export GITHUB_PAT="github_pat_..."
export GITHUB_TOOLSETS="context,repos,issues,pull_requests,actions,users"   # optional
export GITHUB_READ_ONLY="1"   # default; flip to 0 only inside skills that post
```

**Verifier:**

```bash
curl -sS -H "Authorization: Bearer $GITHUB_PAT" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/user | jq .login
```

**Fallback:** every adk skill that uses this MCP also supports the `gh` CLI for the same operations. Phase-1 preflight prefers `gh` if both Docker and `gh` are available (faster cold start; doesn't need Docker running).

### 4.2 Datadog — `plugins/adk-investigate/.mcp.json`

Datadog Bits AI MCP, hosted at `mcp.datadoghq.com` (Preview).

**Env vars:**

```bash
# https://app.datadoghq.com/organization-settings/api-keys
export DD_API_KEY="..."
# https://app.datadoghq.com/organization-settings/application-keys
# Required scope: mcp_read (and mcp_write only if you actually need to mute monitors)
export DD_APP_KEY="..."
# US1 = datadoghq.com (default); also: datadoghq.eu, us3.datadoghq.com,
# us5.datadoghq.com, ap1.datadoghq.com, ap2.datadoghq.com
export DD_SITE="datadoghq.com"
# Optional override (defaults to https://mcp.datadoghq.com/api/unstable/mcp-server/mcp)
# export DD_MCP_URL="..."
```

The plugin-local MCP config sends these values to Datadog using the current
MCP HTTP header names `DD_API_KEY` and `DD_APPLICATION_KEY`. The REST API
verifier below still uses Datadog's standard REST headers with hyphens.

**Verifiers:**

```bash
# REST API surface check
curl -sS -G "https://api.${DD_SITE}/api/v2/logs/events" \
  -H "DD-API-KEY: $DD_API_KEY" \
  -H "DD-APPLICATION-KEY: $DD_APP_KEY" \
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
export GITHUB_PAT="github_pat_..."
export GITHUB_READ_ONLY="1"
export GITHUB_TOOLSETS="context,repos,issues,pull_requests,actions,users"

export DD_API_KEY="..."
export DD_APP_KEY="..."
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
  - github                 ✓ Connected (Docker v1.0.3)        [gh CLI: also available]
  - datadog                ✓ Connected (https://mcp.datadoghq.com)
  - statsig                ✓ Connected (https://api.statsig.com/v1/mcp)

env vars referenced by adk plugins:
  - GITHUB_PAT             present
  - DD_API_KEY             present
  - DD_APP_KEY             present
  - DD_SITE                present (datadoghq.com)
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
| `/adk-investigate:investigate-datadog` says "DD MCP not reachable" | `DD_API_KEY` or `DD_APP_KEY` missing in Claude Code's env | Add to `~/.zshenv`, restart Claude Code |
| GitHub MCP times out on first call | Docker not running | `open -a Docker`, wait for the whale, retry |
| Statsig MCP returns 401 | API key wrong scope | Mint a new key with `omni_read_only` scope |
| Workspace connector says "Not connected" | Workspace admin hasn't enabled it | Ask your Claude admin to enable Atlassian / Slack / etc. |
| `adk-info` outputs `unset` for a `${ENV_VAR}` field | env var not exported | Add the `export` line to `~/.zshenv`, restart shell + Claude Code |
| `/adk-core:setup` complains about an invalid `~/.config/adk/<topic>.md` | YAML front-matter parse error | Re-open the file, fix the YAML, re-run `setup --target <topic>` |

For deeper issues, run:

```text
/adk-core:info --check
```

This validates every meta-info file's schema and lists keys that skills want but aren't set.
