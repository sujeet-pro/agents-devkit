# `audit-pr` — four-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/audit-pr.md`.

## Phase 1 — pre-execution
- [ ] Inputs valid.
- [ ] `.temp/task-<slug>/` exists.
- [ ] Required MCP servers reachable (or fallback documented).

## Phase 2 — mid-flow
- [ ] Each step's preconditions met before the next runs.
- [ ] No write outside `.temp/task-<slug>/`.

## Phase 3 — pre-handoff (before publishing the artifact)
- [ ] Artifact matches `references/artifact-format.md` shape.
- [ ] Every claim has cited evidence.
- [ ] No remote write happened without an approval gate.

## Phase 4 — post-execution
- [ ] Final report exists.
- [ ] All side effects accounted for.
- [ ] User acknowledged (or `--auto`).
- [ ] **Post-confirmation (if any inline summary comment was posted to the PR):** wait 5s, re-fetch the PR's comment graph, confirm every receipt ID re-appears. On miss, retry at 10s and 20s (3 attempts total, 35s budget). All confirmed → OK. Any unconfirmed after the budget → record as `WARN` with the receipt ID + html_url in the report. NEVER re-post on a miss — propagation lag would create real duplicates.
