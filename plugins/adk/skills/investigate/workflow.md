# investigate — workflow

Five phases, read-only throughout. The phased process is the contract; the **Workflow tool** drives the multi-source sweep that makes the two-source-minimum real.

## Phase 0 — gather + pin

- Classify the input per `dispatch.md` → sub-flow + the data sources it implies.
- **Pin the window.** Resolve an explicit `[T_start, T_end]` from `--window`, the alert fire time, or the symptom's first-seen. No "recent"/"lately". If none can be derived, **ask** (`rules.md`).
- Identify the service(s) and the metric that defines the symptom ("slow" = which? p99, error rate, throughput).

## Phase 1 — frame

- State the question in one line, the window, the service, and the symptom metric.
- Decide the sources to sweep (from `dispatch.md`) and which is likely the strongest signal.
- In `-i` mode, confirm window + service + metric before querying.

## Phase 2 — sweep (the Workflow: multi-modal, blind, parallel)

Drive a **Workflow** that fans out one agent **per data source**, each blind to the others — this is what stops you anchoring on the first plausible cause:

- **Datadog** (`adk-datadog` MCP) — logs, metrics, traces, monitors, error-tracking in the pinned window.
- **Recent deploys** — `gh` (`gh api`, `gh pr list --state merged`, `git log`) to find what shipped near `T`.
- **Slack** (`adk-slack` MCP) — chatter / prior incidents around the window.
- **Statsig** (`adk-statsig` MCP) — audit log of gate/experiment changes near `T` (±2h for RCA).
- **Mixpanel / Snowflake / Looker** (their MCPs) — user-impact / analytics, when in scope. Read-only queries only.

Each agent returns its findings with a ≤15-word quote + timestamp. Honest degradation: if an MCP is unreachable, mark `[<source>: skipped]` and lower the confidence of any conclusion that would have leaned on it.

## Phase 3 — correlate + adversarially check

- Build a timeline from the independent signals.
- Form a hypothesis **only when ≥2 independent sources agree** in direction (and ideally magnitude). One source = "leading hypothesis", not root cause.
- Spawn a **skeptic** (`investigator` agent) to hunt for a *contradicting* signal — a deploy that doesn't line up, a metric that moved before the suspect change, a flag that was already on. The hypothesis survives only if the skeptic can't refute it.
- State confidence (low / med / high) per `persona.md` anchors. Never name a person — name the system/process gap.

## Phase 4 — report

- **Timeline** (T-anchored, each line cited + confidence) → **Hypothesis** (root cause + contributing + evidence count) → **Next action by blast radius** (`rollback > flag-off > restart > investigate-which-PR > escalate`), lowest first, marked recommended.
- Recommend; never execute. Publishing the report to Slack/Jira is gated and out of this skill's default scope (`rules.md`).

## Narrate

State the pinned window up front, each source swept (and any skipped), the correlation, the skeptic's verdict, and the confidence on the final call.
