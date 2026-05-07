# `investigate-incident` — workflow detail

## Phase 0 — prompt expansion

The input may be free-form text ("checkout 500s since 13:00") OR one or more URLs (Slack permalink to an alert / chatter, Datadog incident / monitor / dashboard / log-explorer link, PagerDuty / OpsGenie / Statuspage URL, GitHub issue). URLs are resolved BEFORE the rest of Phase 0 runs.

### 0a — link resolution (only if prompt contains URLs)

1. Detect URLs and classify by host:
   - `*.slack.com/archives/*` → Slack permalink
   - `app.datadoghq.*/incidents/*` → DD incident
   - `app.datadoghq.*/monitors/*` → DD monitor
   - `app.datadoghq.*/dashboard/*` → DD dashboard
   - `app.datadoghq.*/logs?*` / `*/apm/*` / `*/rum/*` → DD log-explorer / APM / RUM query
   - `*.pagerduty.com/incidents/*` / `*.opsgenie.com/alert/*` → pager incident
   - `github.com/*/issues/*` → GitHub issue
2. Run `/adk-core:context-gather <urls>` to fetch the linked content (one hop only). For Datadog incident / monitor / dashboard URLs the Datadog MCP is used directly (`get_datadog_incident` / `search_datadog_monitors` / `get_datadog_dashboard`) instead of the connector. For Slack, the workspace Slack connector pulls the parent message + thread.
3. Save fetched evidence to `.temp/task-<slug>/investigation/incident/raw/source-link-<n>.{md,json}` with the original URL + retrieval timestamp.
4. Extract from each fetched source:
   - **Symptom sentence** — the alert title, monitor name, incident summary, or first message of the thread.
   - **Service** — `service:<tag>`, `@service:<tag>`, monitor `service` scope, or repo name in the GH issue.
   - **Symptom timestamp** — alert fired-at, monitor transition-at, message ts, or incident created-at.
   - **Window hint** — explicit window in a DD log/APM/RUM query if present.
5. If multiple URLs disagree on service or timestamp, surface the conflict and prefer (in order) DD monitor → DD incident → Slack alert message → Slack chatter → GH issue.

### 0b — symptom + entity resolution

1. **Restate** the symptom in one sentence (use the extracted symptom from 0a if a URL was given; else the user's text).
2. **Resolve service:**
   - From 0a if the link gave one.
   - Else, if the prompt names a service literal → use it.
   - Else, parse the symptom for service shorthand ("checkout broken" → look up `~/.config/adk/datadog.md.service_aliases.checkout`).
   - Else, ask the user (list services from `repos.md`).
3. **Resolve repo(s)** for the service. A service may map to multiple repos:
   - Read `~/.config/adk/repos.md.repos[].datadog_service` for matches.
   - All matching repos go into the deploy-timeline phase.
4. **Resolve window:**
   - `--window` flag wins.
   - Else if 0a extracted a window hint from a DD query → use it.
   - Else if `--symptom-time T` set → `[T-30m, T+30m]`.
   - Else if user said "since 13:00" → `[13:00, now]`.
   - Else if user said "last 2h" → `last 2h`.
   - Else default `last 2h`.
5. **Resolve symptom timestamp:**
   - From 0a if the link gave one.
   - Else `--symptom-time` flag, OR parsed from the prompt ("at 13:02"), OR "now" if neither.

Output: `entities.md` table — also lists the source URL(s) and which fields each one contributed.

## Phase 1 — preflight

1. `bin/adk-mcp-health --shipped --workspace`. Required: `datadog` + (if Slack scrape requested) `slack-workspace`.
2. `gh --version` and `gh auth status` for the deploy-timeline sub-skill.
3. `bin/adk-info --check info repos datadog slack` returns 0.
4. If `slack-workspace` MCP not reachable but `--slack-channel` was set: surface "Slack scrape skipped" in the report; continue (Slack is optional, not required).

## Phase 2 — define window

(Already done in Phase 0; re-confirmed here for the report header.)

## Phase 3 — Datadog passes (parallel)

Spawn the `incident-investigator` agent (loaded with this skill). The agent runs in parallel:

1. **Logs**: `aggregate_logs` group-by `error.message` for `service:<svc> env:prod status:error` over `<window>`. Top 5 classes + top sample per class.
2. **Metrics**: `get_metrics` for `error_rate`, `p99_latency_ms`, `throughput`. Compute baseline against `[window-shifted-by-24h]`.
3. **Traces**: `list_spans` filtered by `service:<svc> status:error`, sorted by duration desc. Top 5.
4. **Monitors**: `get_monitors --tag service:<svc> --state Alert,Warn,No\ Data`. Capture state + last triggered.

Save raw to `.temp/task-<slug>/investigation/incident/raw/dd-*.json`.

## Phase 4 — Deploy timeline

For each repo mapped to the service, call `/adk-investigate:investigate-deploy <repo> --window <window> --symptom-time <T>`.

Aggregate results into the report. Per-repo near-symptom flags are computed by the deploy skill; this skill surfaces them at the top.

## Phase 5 — Optional Slack scrape

If `slack-workspace` connector reachable, scrape up to **two** channels:

1. **Chatter channel.** `--slack-channel <#name>` if passed; else `slack.md.incident_channel` (org-wide incident room). Captures live team discussion.
2. **Alert channel.** `slack.md.alert_channels.<service>` for the resolved service tag (e.g. `storefront-bff` → `#datadog-alerts-bff`, `quince-site` → `#datadog-alerts-website`, SAND services → `#storefront-ex-alerts`). Captures which monitors fired and when. Skip if no entry exists for the service.

For each:

1. Pull last `<N>` messages (default `N=50`).
2. Filter to messages mentioning the service or symptom keywords.
3. Summarize each thread in ≤15 words; preserve the thread permalink.
4. De-duplicate threads across the two feeds before passing to correlation.
5. Identify if the team has already named a cause; preserve it for the correlation phase.

If the connector is unreachable: skip both; flag the gap in the report. If only one channel is reachable, scrape it and note the missing one.

## Phase 6 — Correlate (the multi-source protocol)

Apply the rules in `multi-source-protocol.md`. Walk in this order:

1. **Deploy + log signal.** A near-symptom deploy + a new error class in the same window → strong candidate. Confidence depends on diff overlap.
2. **Monitor cluster.** ≥4 monitors from one service triggered ±5min → that service's recent change is likely.
3. **Host / pod isolation.** Errors only on certain hosts → bad node / partial rollout.
4. **Slack pre-knowledge.** Team in `#incidents` already named a cause → strong directional signal; verify before adopting.
5. **No correlation.** No two-source agreement → "no leading hypothesis". Do NOT invent one.

Require **at least two independent signals** before naming a root cause. If only one source agrees, the verdict is "leading candidate", not "root cause".

## Phase 7 — Root-cause hypothesis

One paragraph. Format:

```
**Hypothesis:** <one or two sentences>

**Evidence:**
- <Source 1>: <what we observed; link>
- <Source 2>: <what we observed; link>
- <Source 3 if applicable>: <what we observed; link>

**Confidence:** <low | medium | high> — <one sentence anchored to confidence-language.md rules>
```

If multiple plausible hypotheses, list each with its own confidence.

## Phase 8 — Prioritized next actions

Per `next-action-priorities.md`:

1. **Rollback** if a deploy is the leading candidate AND the deploy is recent enough that rollback is sane.
2. **Flag-off** if a Statsig gate is the candidate (the operator runs the toggle in the Statsig console).
3. **Restart hosts** if errors are isolated to a subset of hosts.
4. **Investigate which PR** if the deploy diff has multiple suspects.
5. **Escalate** to the on-call channel / next on-call engineer.

For each action:
- Concrete command / link the operator can run.
- Estimated time.
- Reversibility note ("rollback is reversible in <5 min").

NEVER auto-trigger any action.

## Phase 9 — Emit `incident.md` and (optional) hand-off

Per `output-format.md`. Return path to caller.

If the operator wants to chain the fix, suggest in the report's `Follow-up` section:

```markdown
## Follow-up
- If the rollback (option 1) confirms the diagnosis: `/adk-code:code-bugfix "<root-cause sentence>" --repo <repo>`.
- For the post-mortem doc: `/adk-investigate:investigate-rca "<symptom>" --window <window>` (this skill + Statsig audit + git blame).
```

## Loop control

- Cap parallel subagents at 4 (the dispatcher's hard limit).
- After 3 consecutive MCP failures from the same source, surface the connection issue and continue with what's available.
- If both Datadog AND deploy-timeline fail → stop with a clear "two sources unreachable" error; do not produce a single-source report.
