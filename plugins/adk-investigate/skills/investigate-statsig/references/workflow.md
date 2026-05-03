# `investigate-statsig` — workflow detail

## Phase 0 — prompt expansion

1. **Restate** the user's question in one sentence.
2. **Resolve experiment / gate name** from `~/.config/adk/statsig.md.common_experiments` / `common_gates`. If a literal name is given but not in the meta-info, use it as `inferred` and proceed.
3. **Resolve metric name(s)** if relevant from `statsig.md.exposure_metric_conventions` (especially `guardrail_metrics`). For full discovery, defer to `List_Metrics` in Phase 2.
4. **Resolve time window** for `audit-log` and `pulse`:
   - `audit-log` default: `last 60m` (per spec — "what broke prod" needs short window).
   - `pulse` default: `since experiment_start` (full lifetime to date).
   - `--window` flag wins for both.
5. **Pick `--use`**:
   - "pulse for `<exp>`" / "experiment results" → `pulse`
   - "what changed" / "audit log" / "config history" → `audit-log`
   - "list gates" / "stale gates" → `gates-list`
   - "details for gate `<name>`" / "gate exposures" → `gates-detail`
   - "metric definition" / "what is metric" → `metrics-catalog`

Output: `entities.md` table in `.temp/task-<slug>/investigation/statsig/`.

## Phase 1 — preflight

1. `bin/adk-mcp-health --shipped` — confirms `statsig` MCP is `connected`.
2. `STATSIG_CONSOLE_API_KEY` env var present.
3. `bin/adk-info --check statsig` — confirms `~/.config/adk/statsig.md` parses.
4. (Cheap warmup) `Get_List_of_Gates --limit 1` to mask hosted MCP cold-start.

## Phase 2 — execute (per `--use`)

### `--use pulse`

1. **Fetch results.** `Get_Experiment_Results --experiment-id <id>` (lifetime by default, or `--window <window>` for a slice).
2. **Extract:**
   - Primary metric: name, value (control vs treatment), delta, p-value, confidence interval.
   - Secondary metrics: same shape, listed.
   - Guardrail metrics: name, direction-of-good (e.g. `error_rate` lower is better), value, p-value.
   - Sample size: per arm.
   - Time in experiment: days since start.
3. **Evaluate.** Apply the rubric in `pulse-evaluation.md`:
   - Recommended action = `ship | iterate | kill`.
   - For each guardrail moving the wrong way at `p<0.1`, this is a **veto** (cannot ship).
4. **Ownership context.** If `statsig.md.common_experiments[].repo` is set, fetch last 5 commits from that repo — useful for "did the implementation change recently?".

### `--use gates-list`

1. `Get_List_of_Gates`, optionally with filters:
   - `--stale` → not evaluated in last `<X>` days (default 30).
   - `--recent` → modified in last `<X>` days (default 7).
   - `--tag` → filter by tag (e.g. `team:checkout`).
2. Render as a table: name, owner, status (passing/disabled), last-modified, exposures last 7d.

### `--use gates-detail`

1. `Get_Gate_Details_by_ID --gate-id <id>`.
2. `Get_Gate_Results --gate-id <id> --window <window>` for exposures by env, pass rate, top targeting rules.
3. Audit slice for this gate (same call as `audit-log` filtered by gate id).

### `--use audit-log`

1. `Get_Audit_Logs --since <window.start> --until <window.end>`.
2. Filter to entries of type `gate_change`, `experiment_change`, `config_change`, `metric_change`.
3. Group by `object` (gate / experiment / metric) and `actor`.
4. Surface the 1–5 most recent in a timeline.

### `--use metrics-catalog`

1. `List_Metrics` to find the metric.
2. `Get_Metric_Definition --metric-id <id>` for the formal definition.
3. Surface: source events, computation, type (count / sum / unique / ratio / percentile), is-guardrail flag.

## Phase 3 — summarize

- For `pulse`: lead with the recommendation (`ship` / `iterate` / `kill`); include the rubric inputs (lift, p-value, guardrails, sample size, days-in-experiment).
- For `audit-log`: timeline with `timestamp + actor + object + action`; link each to the Statsig console.
- For `gates-list`: a sorted table (by recency or staleness).
- For `gates-detail`: current state + recent change.
- For `metrics-catalog`: the formal definition + caveats.

## Phase 4 — report

Emit `.temp/task-<slug>/investigation/statsig.md` per `output-format.md`. Return path to caller.

## Loop control

- Cap Phase 2 at 5 calls per skill invocation (excluding cheap `List_*` calls).
- After 3 consecutive MCP errors, surface and stop.
- Never re-fetch the same `Get_Experiment_Results` more than twice in a session — the data hasn't moved.
