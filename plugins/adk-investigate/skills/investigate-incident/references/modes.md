# `investigate-incident` — mode contract

`investigate-incident` is **read-only**. It supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` — investigation produces evidence and recommendations, not actions.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks documented defaults at every decision:
  - `--service` resolved from symptom via meta-info.
  - `--window` `last 2h` (or `±30min` if `--symptom-time` set).
  - `--slack-channel` from `slack.md.incident_channel`.
- Spawns the `incident-investigator` subagent for parallel reads (max 4 parallel per the dispatcher rule).
- Still validates after every phase.
- Still surfaces a final report with confidence-stated hypothesis and prioritized next actions.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
  - Phase 0: shows resolved service + window + channel, asks "proceed?".
  - Phase 3: shows the planned DD calls, asks "run them?".
  - Phase 5: asks "scrape Slack?" (default yes if channel reachable).
  - Phase 7: shows the hypothesis + confidence, asks "publish?".
  - Phase 8: shows the prioritized actions, asks "any to surface to operator immediately?".

## `--fix` is not supported

- This skill is read-only. The actions it recommends (rollback, flag-off, restart) are operator-executed via existing tools, not by this skill.
- If the operator passes `--fix`, the skill rejects with: "investigate-incident produces evidence and recommendations only; chain to `/adk-code:code-bugfix` after the diagnosis is confirmed".

## What `--auto` will NEVER do

1. Trigger a rollback. Always asks.
2. Toggle a Statsig gate. Always asks (and the toggle isn't even in scope for this plugin — the operator does it in the Statsig console).
3. Restart hosts.
4. Mute / silence a Datadog monitor.
5. Modify a workflow / deploy config.
6. Auto-invoke `/adk-code:code-bugfix` (the bugfix skill has its own approval gates; chaining is suggested in the report's `Follow-up`).
7. Name an individual as root cause.
8. Single-source diagnose.

## Composition with `--auto --fix` (from `/adk-core:auto`)

If the operator invokes `/adk-core:auto "<symptom>" --auto --fix`:

- `auto` propagates `--fix` to dispatched skills.
- This skill (`investigate-incident`) does NOT have `--fix`; it ignores the flag with a note in the report.
- The downstream `/adk-code:code-bugfix` (if chained) DOES have `--fix` and applies it per its own contract.

The investigation phase remains read-only; the *fix* phase is where mutation happens.
