# `investigate-rca` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/investigate-rca.md`.

## Phase 1 — preflight

- [ ] `bin/adk-mcp-health` confirms `datadog: connected`, `statsig: connected`, `slack-workspace: connected`.
- [ ] `gh --version` exit 0; `gh auth status` authenticated.
- [ ] `bin/adk-info --check info repos datadog statsig slack` returns 0.
- [ ] Repos for the affected service exist locally (for git blame).

## Phase 2 — incident triage

- [ ] `/adk-investigate:investigate-incident` ran end-to-end.
- [ ] `.temp/task-<slug>/investigation/incident.md` exists.
- [ ] Multi-source protocol satisfied (≥2 corroborating sources OR explicit "no leading hypothesis").
- [ ] Confidence stated.

## Phase 3 — Statsig audit

- [ ] `/adk-investigate:investigate-statsig --use audit-log --window <±2h around symptom>` ran.
- [ ] `.temp/task-<slug>/investigation/statsig.md` exists.
- [ ] If audit log returned matching entries within ±5min of symptom, those are flagged for inclusion in the timeline.

## Phase 4 — git blame (conditional)

- [ ] If incident hypothesis is code-cause: phase ran; `.temp/task-<slug>/investigation/git-blame.md` exists.
- [ ] If hypothesis is NOT code-cause: phase explicitly skipped; reason noted in RCA.
- [ ] If ran: implicated PR has author + reviewer + merged-at + URL.

## Phase 5 — Mixpanel user impact (conditional)

- [ ] If user-facing flow affected: phase ran; `.temp/task-<slug>/investigation/mixpanel.md` exists.
- [ ] If internal-only: phase explicitly skipped; reason noted in RCA.
- [ ] If ran: impact magnitude (users affected / conversion delta) stated.

## Phase 6 — Aggregate RCA

- [ ] All required sections present and in correct order:
  1. Summary
  2. Timeline
  3. Detection
  4. Mitigation
  5. Root cause
  6. Contributing factors
  7. Action items
  8. References
- [ ] Timeline has source link per row.
- [ ] Detection AND Mitigation include "what worked" bullets.
- [ ] Root cause sentence is system-shaped (no individual named).
- [ ] Contributing factors section is non-empty (or explicitly notes "no contributing factors beyond the root cause").
- [ ] All action items pass the 5W frame check (WHO/WHAT/WHEN/WHERE/WHY all populated).
- [ ] All action items pass the testability check (no weak phrases per `output-format.md`).
- [ ] References cite every artifact mentioned in the body.

## Phase 7 — Pre-handoff

- [ ] `.temp/task-<slug>/investigation/rca.md` exists.
- [ ] Final status banner printed.
- [ ] No auto-publish attempted (file stays in `.temp/`).

## Blameless-language pass

- [ ] Every sentence scanned against `blameless-language.md` substitution list.
- [ ] Any blame-shaped phrase rewritten; rewrites logged to `.temp/task-<slug>/investigation/rca/blameless-rewrite-log.md`.

## On any check failure

- Log to `validation/investigate-rca.md` with the failing check + remediation.
- For "individual named as root cause": HARD BLOCK; rewrite required.
- For "non-testable action item": HARD BLOCK; rewrite required.
- For "missing required section": fill or explicitly mark "n/a — reason: ...".
- Same check failing 3 times → surface, do not loop.
