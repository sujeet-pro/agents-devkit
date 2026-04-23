# `publish-ship` — four-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/publish-ship.md`.

## Phase 1 — pre-execution

- [ ] Change is named (PR link / branch / summary).
- [ ] Blast radius is explicit (internal / % / tenants / full).
- [ ] Rollback strategy is named (flag-flip / revert+redeploy / reverse-migration / forward-fix-only).
- [ ] If "no-flag" launch: explicit risk acceptance in the artifact.
- [ ] `.temp/task-<slug>/notes/` exists.

## Phase 2 — mid-flow

- [ ] Pre-launch checklist (see `references/pre-launch-checklist.md`) is fully evaluated; each item OK / WARN / BLOCKER.
- [ ] **Zero BLOCKERs remain.** (The skill cannot proceed past this gate with a BLOCKER, even under `--auto`.)
- [ ] Feature-flag wiring confirmed: name, default OFF in prod, targeting plan, cleanup ticket reference.
- [ ] Staged rollout plan written with checkpoints + SLO windows per stage.
- [ ] Rollback path verified (tested or dry-run-validated, not just assumed).

## Phase 3 — pre-handoff

- [ ] Monitoring is in place BEFORE release: dashboards exist, SLO thresholds configured, on-call paged. Verify via `@adk:observability-datadog` (a.k.a. `adk-observability-datadog`).
- [ ] First-hour check schedule written with named owners + times.
- [ ] Flag-cleanup ticket filed with a ≤ 2-week target after 100%.
- [ ] Approval gate cleared (or `--auto`).

## Phase 4 — post-execution

- [ ] Final report exists with checklist counts, rollout plan, flag info, rollback path, monitoring links, first-hour checks, cleanup ticket reference.
- [ ] User acknowledged (or `--auto`).
- [ ] Hand-off to deploy mechanism is explicit ("now run `<your-deploy-cli>` and watch with `@adk:cicd-monitor`").
