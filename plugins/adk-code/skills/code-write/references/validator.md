# `code-write` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/code-write.md` under a `## Validator` heading.

## Phase 0 — pre-execution

- [ ] `.temp/task-<slug>/` exists and the parent `.temp/` is gitignored.
- [ ] User's prompt captured verbatim in `prompt.txt`.
- [ ] Repo resolved to a single entry in `~/.config/adk/repos.md` (or surfaced as "not in repos.md — confirm").
- [ ] Likely-files set has at least one candidate.
- [ ] Slug derived from prompt nouns/verbs.

## Phase 1 — preflight

- [ ] `git status` captured. Working tree state recorded as `clean | dirty`.
- [ ] Current branch captured. If on `main`/`master`/`develop`, branch-creation prompt fired (or auto-deferred under `--auto` if prompt named the branch).
- [ ] Validation commands resolved from `repos.md` or `package.json`/`pyproject.toml`/`Makefile`/`build.gradle`/`Cargo.toml`/`go.mod`.
- [ ] Baseline check ran: typecheck + lint + tests on HEAD. Result recorded.
- [ ] If baseline red: STOP, do not proceed to Phase 2.

## Phase 2 — read first

- [ ] Every file in the planned set has been read end-to-end (not Grep-only).
- [ ] At least 1 adjacent test file read.
- [ ] At least 1 adjacent module read for style cues.
- [ ] Recent commits in the area read (`git log -n 10 -- <file>`).
- [ ] `AGENTS.md` / `CLAUDE.md` / `.cursorrules` read if present (and noted in plan).

## Phase 3 — plan

- [ ] `plan.md` exists and contains: Goal, Scope, Files touched, Approach, Edge cases, Test changes, Validation plan, Out of scope.
- [ ] Files touched list has rationale per row.
- [ ] Validation plan has explicit commands + expected exit codes.
- [ ] Approval gate fired (unless `--auto`).

## Phase 4 — implement

- [ ] Implementer subagent ran with the plan + slug.
- [ ] Each edited file was re-read after the agent claimed done.
- [ ] No file outside the planned set was touched (or, if it was, re-confirmation event recorded).
- [ ] Test-engineer ran (if new behavior branches were added).
- [ ] Per-file edits logged with +N/-M.

## Phase 5 — validate

- [ ] Typecheck ran with exit 0.
- [ ] Lint ran with exit 0 (with the repo's `--max-warnings` policy).
- [ ] Tests ran with exit 0; counted; package scope recorded.
- [ ] If any check failed: cause identified; smallest possible follow-up edit applied; re-run; recorded.
- [ ] Same-kind failure not seen 3+ times (otherwise STOP and surface).

## Phase 6 — pre-handoff

- [ ] `report.md` covers: Result, Files changed, Validation evidence, Decisions, Residual risk, NOT done, Next steps.
- [ ] Every artifact referenced in `report.md` actually exists at the cited path.
- [ ] Decisions table includes every auto-pick (under `--auto`).
- [ ] No remote write happened (push, commit, PR open) — `code-write` never does these.
- [ ] Final status banner printed.
- [ ] Offer-depth question asked.

## On any check failure

1. Log the failure to `validation/per-skill/code-write.md` under `## Validator failures`, with: phase, check, observed, expected, next action.
2. Block the next phase until the failure is resolved.
3. If the same check fails 3 times in this session, surface to the user — do NOT loop forever.
4. If a check is conditionally skipped (e.g. lint not configured), record the skip + reason; do not silently treat as pass.
