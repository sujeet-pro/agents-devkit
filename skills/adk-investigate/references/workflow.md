# adk-investigate — workflow

Five phases. Read-only throughout.

## Phase 0 — context-gather

- Resolve service from symptom (or `--service` flag) via `overrides.repos[].datadog.apm_service`.
- Anchor a time window: `--window` flag, else symptom-time ±30min, else `last 2h`.
- Fan-out fetch each URL via its classifier (`shared/input-classifiers/*.md`).

## Phase 1 — advise

- Up to 3 questions: scope (just symptom or + prior similar?), window confirm, scale check ("query will scan ~12k logs — proceed?").
- Present sub-flow + sources to use.

## Phase 2 — execute (per sub-flow; sources in parallel where independent)

- All queries pin window; no "recent" / "lately".
- **incident**: Datadog logs + metrics + traces + monitors in parallel; recent deploys via `gh run list`; optional Slack scrape.
- **rca**: incident + Statsig audit-log (±2h around symptom) + git blame on suspected files + optional Mixpanel user-impact.
- **experiment**: Statsig pulse + Mixpanel project metric + DD guardrails over experiment window.

## Phase 3 — validate

- ≥2 independent sources required before naming a root cause.
- Confidence stated per claim (low / medium / high).
- Constitution check (no mutations to monitors / gates / data).

## Phase 4 — report

- Timeline + hypothesis + blast-radius-ordered next actions.
- Honest gap reporting: `[<source>: skipped — <reason>]` when an MCP unreachable.
- Suggest `/adk-document --type rca` or `--type incident-summary` if appropriate.

## Personas + guidelines

- `shared/personas/investigator.md` (always).
- `shared/personas/context-gatherer.md` (Phase 0 fan-out).
- `shared/guidelines/observability.md` (always).
- `shared/guidelines/security.md` (if symptom hints exploit).
- `shared/guidelines/performance.md` (if symptom is latency / throughput).
