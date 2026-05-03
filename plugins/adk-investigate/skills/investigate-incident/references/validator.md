# `investigate-incident` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/investigate-incident.md`.

## Phase 0 — pre-execution

- [ ] Symptom captured verbatim.
- [ ] Service resolved to a canonical tag (`verified` from `datadog.md.service_aliases` or `inferred`).
- [ ] Repos for the service resolved (1 or more from `repos.md`).
- [ ] Window resolved to concrete `[from, to]`.
- [ ] Symptom timestamp resolved (provided / parsed / "now").
- [ ] Slack channel resolved if scraping (or marked `not requested`).

## Phase 1 — preflight

- [ ] `bin/adk-mcp-health --shipped --workspace` confirms `datadog: connected`.
- [ ] `gh --version` exit 0; `gh auth status` authenticated.
- [ ] `slack-workspace` MCP either `connected` OR Slack scrape marked `skipped: workspace MCP unreachable` in the report.
- [ ] `bin/adk-info --check info repos datadog slack` returns 0.

## Phase 3 — DD passes

- [ ] All four DD reads attempted (logs + metrics + traces + monitors). Failures logged but do not block (continue with what's available).
- [ ] Each DD query has a time window AND env tag.
- [ ] Raw responses saved to `.temp/task-<slug>/investigation/incident/raw/`.
- [ ] Baseline computed for each metric (or `n/a — baseline unavailable`).

## Phase 4 — Deploy timeline

- [ ] `/adk-investigate:investigate-deploy` called once per repo mapped to the service.
- [ ] `--symptom-time` propagated.
- [ ] Per-repo near-symptom flag computed.

## Phase 5 — Slack scrape (if applicable)

- [ ] At most 50 messages pulled.
- [ ] Filter applied (mentions service / symptom).
- [ ] Each quoted message ≤15 words.
- [ ] Each thread has a permalink.

## Phase 6 — Correlate

- [ ] At least 2 independent sources attempted (DD logs/metrics + deploys minimum).
- [ ] Multi-source protocol checks applied per `multi-source-protocol.md`.
- [ ] If only 1 source agrees, hypothesis is labeled "leading candidate" not "root cause".
- [ ] If no signals correlate, hypothesis is "no leading hypothesis" (do NOT invent one).

## Phase 7 — Hypothesis

- [ ] Hypothesis paragraph cites ≥2 source links.
- [ ] Confidence stated (`low | medium | high`).
- [ ] Confidence rationale anchored to `confidence-language.md` rules.
- [ ] No individual named as root cause.

## Phase 8 — Next actions

- [ ] At least 1 action proposed (or "escalate" if no actionable cause).
- [ ] Each action has: blast radius, reversibility, concrete command/link, estimated cost.
- [ ] Ordered by `next-action-priorities.md` (rollback > flag-off > restart > investigate-which-PR > escalate).
- [ ] No action is auto-triggered; report describes only.

## Phase 9 — Pre-handoff

- [ ] `.temp/task-<slug>/investigation/incident.md` exists.
- [ ] Sources table present and accurate.
- [ ] All sections in correct order per `output-format.md`.
- [ ] Final status banner printed.

## On any check failure

- Log to `validation/investigate-incident.md` with the failing check + remediation.
- For "single-source diagnosis" violation in Phase 6/7: re-run correlation OR label as "leading candidate" — do not allow a high-confidence single-source claim through.
- For "auto-trigger attempt": BLOCK; do not retry.
- Same check failing 3 times → surface, do not loop.
