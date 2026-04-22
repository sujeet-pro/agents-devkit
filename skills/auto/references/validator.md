# `auto` — four-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/auto-validator.md`.

## Phase 1 — pre-execution

- [ ] `.temp/task-<slug>/` exists and is gitignored.
- [ ] User's prompt is captured verbatim in `prompt.md`.
- [ ] Domain classification recorded in `validation/auto-validator.md`.
- [ ] If any links in prompt, `context-gather` is queued.

## Phase 2 — mid-flow (between phases)

After Phase A:
- [ ] Slug confirmed (or `--auto` default applied).
- [ ] If links present, `context.md` exists.

After Phase B:
- [ ] `requirements.md` exists with confirmed scope statement.
- [ ] `scope.md` exists with: in/out, blast radius, success criteria, milestones.
- [ ] User approved (or `--auto`).

After Phase C:
- [ ] All dispatched subagents returned.
- [ ] Each one's per-skill validator file exists at `validation/per-skill/<skill>.md`.
- [ ] If UI touched, `preview/sample-{1..5}.html` exists OR `--skip-design` was confirmed.

After Phase D1:
- [ ] `validation/d1.md` exists. No Blockers, no Criticals.

After Phase D2 (if applicable):
- [ ] `browser-validation/<mode>/report.md` exists for every mode that ran.
- [ ] No Blocker findings.

After Phase D3:
- [ ] PR URL captured. CI status captured.

## Phase 3 — pre-handoff (before final report)

- [ ] `report.md` covers: Result, Decisions, Skills-run, Validation, Residual-risk.
- [ ] Every artifact referenced in `report.md` actually exists at the cited path.
- [ ] No remote write happened without an approval gate (or `--auto`).

## Phase 4 — post-execution

- [ ] PR is in expected state (open, ready-for-review, or merged per scope).
- [ ] CI is green (or explicit accepted-yellow recorded in `report.md`).
- [ ] User acknowledged final report.
