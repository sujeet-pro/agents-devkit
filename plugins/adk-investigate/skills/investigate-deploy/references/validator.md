# `investigate-deploy` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/investigate-deploy.md`.

## Phase 0 — pre-execution

- [ ] User's question captured verbatim.
- [ ] Repo resolved (`<owner/repo>` form). Marked `verified` (matched `repos.md`) or `inferred` (CWD-derived).
- [ ] Workflow resolved. Marked `verified` (`repos.md.repos[].deploy_workflow`) or `inferred` (fell back to literal `deploy`).
- [ ] Window resolved to a concrete duration.
- [ ] If `--symptom-time` provided, parsed to a valid ISO timestamp.

## Phase 1 — preflight

- [ ] `gh --version` exit 0.
- [ ] `gh auth status` shows authenticated.
- [ ] (If non-local repo) `gh api repos/<owner>/<repo>` returns 200.
- [ ] `bin/adk-info --check repos github` returns 0.

## Phase 2 — execute

- [ ] `gh` command logged to `.temp/task-<slug>/investigation/deploy/command.md` before execution.
- [ ] `gh` exit 0 (or non-zero with the error captured for the report).
- [ ] Raw JSON saved to `raw/gh-run-list-<repo>.json`.
- [ ] If DD cross-reference attempted, raw JSON saved to `raw/dd-deploy-events-<service>.json` regardless of result.
- [ ] No `gh run rerun` / `gh run cancel` / write operation invoked.

## Phase 3 — summarize

- [ ] Timeline table has all 7 (or 8 with Δ-symptom) columns populated for every row.
- [ ] Failed deploys appear in their own section.
- [ ] If `--symptom-time` set, near-symptom candidates section exists (may be empty).
- [ ] If DD cross-reference ran, coherence statement included ("all matched" or specific mismatches listed).
- [ ] No claim of "deploy caused" anywhere in the report.

## Phase 4 — pre-handoff

- [ ] `.temp/task-<slug>/investigation/deploy.md` exists.
- [ ] Sections in correct order: `Summary`, `Timeline`, `Failed deploys` (if any), `Near-symptom candidates` (if applicable), `Cross-source: Datadog` (if applicable), `Follow-up`.
- [ ] Every artifact referenced in the report exists at the cited path.
- [ ] Final status banner printed.

## On any check failure

- Log to `validation/investigate-deploy.md` with the failing check + remediation.
- Block the next phase until resolved.
- If `gh` rate-limited, surface and stop.
- Same check failing 3 times → surface, do not loop.
