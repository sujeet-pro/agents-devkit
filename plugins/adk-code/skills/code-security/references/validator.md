# `code-security` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/code-security.md`.

## Phase 0 — pre-execution

- [ ] `.temp/task-<slug>/` exists; `.temp/` is gitignored.
- [ ] User's prompt captured in `prompt.txt` (sanitized — no working exploit payloads in this file).
- [ ] Repo resolved.
- [ ] CVE id (if applicable) noted; advisory fetched.
- [ ] Slug derived.

## Phase 1 — preflight

- [ ] `git status` clean.
- [ ] Branch captured. Protected → branch-creation prompt.
- [ ] Validation commands resolved.
- [ ] Tests pass on HEAD (baseline = green).

## Phase 2 — threat model

- [ ] `threat-model.md` exists.
- [ ] EXACTLY 5 lines (one per slot: untrusted input, privileged action, asset, actor, residual risk).
- [ ] Each slot has a specific answer (not vague).
- [ ] Approval gate fired (unless `--auto`).

## Phase 3 — boundary

- [ ] `boundary.md` exists.
- [ ] Input boundary: `<path>:<line>` — described.
- [ ] Output / privileged action: `<path>:<line>` — described.
- [ ] The mitigation will live AT or NEAR the input boundary (recorded).

## Phase 4 — REPRODUCE the exploit

- [ ] `exploit-test.md` exists.
- [ ] Test file path in the repo recorded.
- [ ] Test name uses behavior-named convention (e.g. "rejects forged token via algorithm confusion").
- [ ] Test ran on HEAD: FAILED. Failing output captured verbatim.
- [ ] If test passed unexpectedly: STOP. Either bug already fixed, env-specific, or test is wrong.
- [ ] Confidence stated (high / medium / low).

## Phase 5 — APPLY mitigation

- [ ] `plan.md` exists with: Mitigation (one sentence), Files touched, Why this is at the right boundary, Validation plan.
- [ ] Implementer subagent ran with `threat-model.md` + `boundary.md` + `exploit-test.md` + `plan.md`.
- [ ] Each edited file re-read after the agent claimed done.
- [ ] No file outside the planned set was touched (or scope creep was re-confirmed).
- [ ] Re-run exploit test: GREEN. Captured.
- [ ] If still failing: STOP. Mitigation is wrong; loop back to Phase 3 / Phase 5 plan.
- [ ] No drive-by hardening / scope creep in the diff.

## Phase 6 — VALIDATE

- [ ] Exploit test alone: green.
- [ ] Full affected-package suite: green.
- [ ] Typecheck + lint: green.
- [ ] No pre-existing test went red (no regression).

## Phase 7 — security-reviewer

- [ ] Security-reviewer agent ran with the diff + `threat-model.md` + `boundary.md`.
- [ ] `security-review.md` exists with findings tiered (Blocker / Critical / Should-have / Question).
- [ ] No Blocker findings remain unfixed (loop back to Phase 5 if any).
- [ ] Critical findings either fixed in this diff or explicitly deferred with operator approval.

## Phase 8 — pre-handoff

- [ ] `report.md` covers: Threat (verbatim), Boundary, Exploit test red→green, Mitigation, Security-review findings, Validation evidence, Decisions, Residual risk, NOT done, Disclosure status, Next steps.
- [ ] Every artifact referenced in `report.md` exists.
- [ ] Decisions table includes every auto-pick.
- [ ] No remote write.
- [ ] Final status banner printed.
- [ ] Offer-depth question asked.
- [ ] Disclosure handling: `report.md` may include details (internal); commit message + PR description language is generic until disclosure permits.

## Hard checks (the skill cannot pass without these)

1. `threat-model.md` exists with EXACTLY 5 lines.
2. `boundary.md` exists with input + output pointers.
3. `exploit-test.md` exists with failing-on-HEAD output captured.
4. The exploit test's red→green transition is recorded in `validation/per-skill/code-security.md`.
5. `security-review.md` exists with no unaddressed Blockers.
6. Full affected-package suite is green after the mitigation.
7. The mitigation lives at the boundary (per `boundary.md`), not scattered.

If any hard check fails:

- The skill is BLOCKED.
- The status banner shows `exploit-test=red` or `security-review=blocker-pending`.
- The report is not generated.

## On any check failure

1. Log under `## Validator failures`.
2. Block the next phase.
3. Wrong mitigation (test still red after fix) → loop back to Phase 5 once. After 2 wrong mitigations, STOP regardless of mode.
4. Blocker finding from security-reviewer → loop back to Phase 5; fix in this diff; never ship a Blocker.
5. Vulnerability disclosure leak detected (e.g. exploit details in commit message) → STOP; sanitize before continuing.
