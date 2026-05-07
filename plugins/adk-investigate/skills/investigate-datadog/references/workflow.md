# `investigate-datadog` — workflow detail

## Phase 0 — prompt expansion

1. **Restate** the user's question in one sentence. ("How many 5xx in checkout in the last hour?")
2. **Resolve target.** Pull entity table:
   - Repo / service: read `~/.config/adk/repos.md` + `datadog.md.service_aliases`. ("checkout" → `checkout-api`.)
   - Endpoint / route: from the prompt verbatim.
   - Log filter / metric name: from the prompt verbatim.
3. **Resolve time window.** `--time` flag wins; else parse natural language ("last 1h", "since 13:00", "yesterday"); else default to `datadog.md.default_window`.
4. **Resolve env.** `--env` flag wins; else `datadog.md.default_env`.
5. **Pick `--use`** if not given:
   - "errors / 5xx / exceptions in `<service>`" → `investigate` (logs)
   - "p50 / p99 / latency / throughput on `<service>` or `<endpoint>`" → `investigate` (metrics)
   - "trace / span for `<id>`" → `investigate` (traces)
   - "which monitors are firing" / "alert status" → `alert-triage`
   - "summarize the `<dashboard-name>` dashboard" → `dashboard-summary`

Output: `entities.md` table in `.temp/task-<slug>/investigation/`.

## Phase 1 — preflight

1. `bin/adk-mcp-health --shipped` — confirms `datadog` MCP is `connected`.
2. `bin/adk-info --check datadog` — confirms `~/.config/adk/datadog.md` parses and has the keys this query needs (service if shorthand was used; dashboard id if `--use dashboard-summary` was named by name, etc.).
3. Confirms `DATADOG_API_KEY` and `DATADOG_APP_KEY` env vars are present (legacy `DD_API_KEY` / `DD_APP_KEY` are also accepted via shell alias — `bin/adk-mcp-health` treats either as present).
4. If anything fails, stop with the exact missing-thing list and the suggested `/adk-core:setup --target datadog` invocation. Never auto-install.

## Phase 2 — execute (per `--use`)

### `--use investigate`

1. **Decide source** based on the prompt:
   - Errors / exceptions / 5xx / panic / crash → `logs`
   - p50 / p99 / latency / throughput / qps / saturation → `metrics`
   - Trace id / span / request-id → `traces`
   - "what changed" / "deploy event" → `events`
   - "users affected by error X" → `error_tracking`
2. **Build query** from `~/.config/adk/datadog.md.common_queries` if matched (by name or shape); else compose:

   ```text
   logs:    service:<svc> env:<env> status:error          [last <window>]
   metrics: avg:trace.servlet.request.errors{service:<svc>,env:<env>} by {resource}.as_count()  [last <window>]
   metrics: percentile(95, trace.servlet.request.duration{service:<svc>,env:<env>})  [last <window>]
   traces:  service:<svc> env:<env> status:error          [last <window>]
   ```

3. **Execute** via the right MCP tool (see `mcp-tools-catalog.md`):
   - `get_logs` (top results) + `aggregate_logs` (group by status/error class).
   - `get_metrics` (current value) + `list_metrics` (discover what's available).
   - `list_spans` (top errored / slow) + `get_trace` (drill into one trace id).
   - `error_tracking_list` for top error groups.
4. **Capture** top 5–10 results with timestamps + DD UI links.
5. **Compute baselines** where applicable:
   - Same query against `[window-shifted-by-24h]` for "vs same time yesterday".
   - Same query against `[window-shifted-by-7d]` for "vs same time last week".

### `--use dashboard-summary`

1. **Resolve `<dashboard-id>`.** If user gave a name, look it up in `datadog.md.common_dashboards`. If not found, list the common ones and ask.
2. **Fetch dashboard.** `list_dashboards` + per-tile fetch.
3. **For each tile**, run its underlying query at the resolved window/env.
4. **Summarize** each tile in one line. Highlight anomalies (>2σ from baseline if available, or >50% delta if not).
5. **Link** to the dashboard at the resolved window.

### `--use alert-triage`

1. **List monitors** with state in `[Alert, Warn, No Data]`. Filter by `--monitor-tag` if given (e.g. `team:checkout`, `service:checkout-api`).
2. **For each**: when triggered, severity, last evaluation time, related deploys (cross-reference `gh run list` for the implicated repo if known).
3. **Group** by likely root cause (same service / same dashboard / same time-bucket). E.g. 4 monitors for `checkout-api` triggered at 13:02 → likely a single root cause.
4. **Suggest follow-ups** — typically `/adk-investigate:investigate-incident` for the leading group.

## Phase 3 — summarize

1. **Top trends** — biggest delta from baseline (or absolute number if no baseline).
2. **Anomalies** — outlier values, error spikes, missing data points.
3. **DD UI links** — every result has a clickable link.
4. **Follow-up queries** — suggest 1–3 targeted next steps the operator might run.

## Phase 4 — report

Emit `.temp/task-<slug>/investigation/datadog.md` per `output-format.md`. Return the path to the caller (or to `/adk-core:auto`'s dispatcher).

## Loop control

- After 3 failed MCP calls in a row, stop and surface the connection issue. Do not loop forever.
- After 5 queries in one Phase 2 invocation, stop and ask the user — investigation is iterative; force the operator into the loop.
- Same query repeated > 2 times in one session is dropped silently from the followup-suggestions list.
