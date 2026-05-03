# `investigate-rca` — workflow detail

## Phase 1 — preflight

1. `bin/adk-mcp-health` confirms `datadog: connected`, `statsig: connected`, `slack-workspace: connected`. (Slack is technically optional but strongly recommended for an RCA — the team's chatter at incident time is invaluable.)
2. `gh --version`, `gh auth status` — for `git blame` and `gh pr view`.
3. `bin/adk-info --check info repos datadog statsig slack` returns 0.
4. Confirm the repos for the affected service(s) exist locally (for `git blame` in Phase 4).

## Phase 2 — incident triage

Run `/adk-investigate:investigate-incident` end-to-end with the same `<symptom>`, `--service`, `--window`, `--symptom-time`. The RCA is built on its output:

- `.temp/task-<slug>/investigation/incident.md` (the report)
- `.temp/task-<slug>/investigation/incident/` (the raw data per source)
- `.temp/task-<slug>/investigation/deploy/` (per-repo deploy timelines)

This phase reuses the `incident-investigator` agent inside `investigate-incident`; this skill does not duplicate the work.

## Phase 3 — Statsig audit (±2h around symptom)

Run `/adk-investigate:investigate-statsig "what changed in this window?" --use audit-log --window <symptom-2h>..<symptom+2h>`.

Output: `.temp/task-<slug>/investigation/statsig.md`.

The ±2h window is wider than the incident triage window because the cause may be a config edit that happened 90 minutes before the symptom (e.g. a metric-definition change that took an hour to propagate to dashboards, then an hour to manifest as alerts).

## Phase 4 — Code-regression deep dive

If `incident.md`'s leading hypothesis names a code regression (deploy + log signal + diff overlap), run a targeted deep dive:

1. **Identify implicated files.** From `incident.md`'s evidence, pull file paths from:
   - DD trace span names (e.g. `OrderService.computePrice` → `checkout-api/src/main/java/com/acme/checkout/OrderService.kt`).
   - DD log error class (e.g. `NullPointerException at OrderService.line47` → same file, line 47).
2. **`git blame` each implicated file.** For each suspected line / range, identify the most recent edit:
   ```bash
   git blame -L <start>,<end> -- <file>
   ```
3. **`gh pr view <pr>`** for each implicated PR:
   - Title, description, author, reviewer(s), merged-at, link.
4. Save to `.temp/task-<slug>/investigation/git-blame.md`.

If the leading hypothesis is NOT a code regression (e.g. third-party outage, gate flip, infra event), skip this phase. Note in the RCA why it was skipped.

## Phase 5 — User impact (optional)

If the incident affected a user-facing flow (most do), run a focused Mixpanel query to quantify:

1. Identify the affected funnel from `incident.md` (e.g. checkout funnel for a checkout incident).
2. `/adk-investigate:investigate-mixpanel "<funnel> during <window>" --use funnel`.
3. Compare the funnel's conversion during the incident window to a baseline (same window prior week).
4. Surface the user-impact magnitude: how many users hit the broken state, how many fewer completed.

Output: `.temp/task-<slug>/investigation/mixpanel.md`.

For internal-only systems (no user-facing flow), skip this phase.

## Phase 6 — Aggregate RCA

Build the RCA per `rca-template.md`. Sections in this exact order:

1. **Summary** — one paragraph; exec audience. What happened, when, who was affected, what we did.
2. **Timeline** — chronological. Each row has: time, event, source link.
3. **Detection** — how did we find out; how long until alert / page.
4. **Mitigation** — what stopped the bleeding; how long.
5. **Root cause** — system-level. Never a person. Anchored to ≥2 corroborating sources.
6. **Contributing factors** — what else made the impact larger / longer (slow detection, stale runbook, missing alert, etc.).
7. **Action items** — 5W frame: who, what, when, where, why. Each testable.
8. **References** — links to incident.md, statsig.md, git-blame.md, mixpanel.md (if applicable), PR / commit links, Slack threads.

Apply `blameless-language.md` throughout: scan every sentence for blame-shaped wording and rewrite to system-shaped.

## Phase 7 — Emit

Write `.temp/task-<slug>/investigation/rca.md`. Return path.

The file is *ready to paste* into the team's post-mortem template (Confluence / GDoc / docs site). The RCA is NOT auto-published — that requires a human sign-off pass via `/adk-docs:docs-publish-confluence` (or similar).

## Loop control

- Do not re-run any sub-skill in the same session — they're cached at their own slug.
- If a sub-skill (e.g. `investigate-statsig`) fails, surface the gap in the RCA's `Sources` section but continue with the rest.
- The RCA is incomplete (not failed) if a source is unreachable; it is failed only if the incident triage itself failed.

## Composition with `/adk-core:auto`

When invoked via `/adk-core:auto` (e.g. "post-mortem for yesterday's outage"), `auto` resolves the symptom + window and dispatches this skill. This skill internally chains `investigate-incident` → `investigate-statsig` → `git blame` → `investigate-mixpanel` (optional). The dispatcher inside this skill respects the max-4-parallel rule.
