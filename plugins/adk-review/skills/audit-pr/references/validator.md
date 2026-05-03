# `audit-pr` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/audit-pr.md`.

## Phase 0 — pre-execution

- [ ] PR URL / number parsed; resolved to `<owner>/<repo>#<num>`.
- [ ] Slug derived (with `audit-` prefix).
- [ ] `.temp/task-<slug>/` exists; gitignored.
- [ ] `prompt.txt` written.
- [ ] Mode parsed; `--checks` subset parsed if present.
- [ ] If `--auto -i`: refused.

## Phase 1 — preflight

- [ ] `bin/adk-mcp-health --shipped --json` shows `github.connected: true` OR `gh auth status` succeeds.
- [ ] MCP client choice recorded.
- [ ] `gh api /user` returns 200.
- [ ] For `--fix`: working tree clean.
- [ ] `bin/adk-info github --check` returns 0.
- [ ] `bin/adk-info repos --check` returns 0.
- [ ] Tool detection per `references/check-catalog.md`: each check marked `executable` or `N/A (missing tool)`.
- [ ] `forbid_force_push_branches` loaded (only if --fix).

## Phase 2 — fetch context

- [ ] `audit/pr-context/pr.json` exists; head SHA recorded.
- [ ] `audit/pr-context/diff.patch` exists.
- [ ] `audit/pr-context/ci-status.json` exists.

## Phase 3 — fixed-set checks

- [ ] All requested checks (or all 10 by default) ran (parallel where independent; max 4 at once).
- [ ] Each check has a `per-check/<name>.md` with: command, exit code, output (truncated), verdict, reason.
- [ ] Each check's verdict ∈ {PASS, WARN, FAIL, N/A, INCONCLUSIVE}. **NEVER use the 6-tier severity system from review-pr.**
- [ ] Conditional checks ran only when their trigger matched (a11y if UI files; perf if hot-path; bundle if frontend with budget).
- [ ] Missing tools mapped to `N/A`, NOT `FAIL`.
- [ ] `~/.config/adk/review.md.ignore_in_repos[<repo>]` filter applied (skip checks the operator deemed irrelevant for this repo).
- [ ] `audit/results.md` written with per-check table + overall verdict.

## Phase 4 — propose

- [ ] Verdict computed per `references/pass-warn-fail.md`.
- [ ] Under `-i`: each WARN / FAIL walked with action options.
- [ ] Under `--auto`: results kept as-is.
- [ ] Approval gate (unless `--auto`): user confirmed before --fix or --post-comment.

## Phase 5a — report (no `--fix`, no `--post-comment`)

- [ ] `results.md` final.
- [ ] Surfaced verdict + per-check counts.

## Phase 5b — fix (`--fix` mode)

- [ ] Auto-fix scope is the SAFELY-FIXABLE SUBSET ONLY: lint-clean, license-headers, docs-toc.
- [ ] Other failed checks are NOT auto-fixed (assert: no edits to test files / dep manifests / env files / etc.).
- [ ] After each fix: re-run the affected check; expect new verdict (typically Pass).
- [ ] `results.pre-fix.md` snapshot taken before fix.
- [ ] `audit/results.md` rewritten with post-fix verdicts.
- [ ] `fix-log.md` written (per-fix evidence).
- [ ] If pushing: PUSH-GATE asked (always — even under `--auto --fix`); push did NOT include `--force`; target NOT in `forbid_force_push_branches`.

## Phase 5c — postback (only if `--post-comment`)

- [ ] Confirmation gate ASKED (always — even under `--auto`).
- [ ] If user declined: NO post happened (assert).
- [ ] If user approved:
  - [ ] Posted via `gh pr comment <num> --body-file <summary>`.
  - [ ] Receipt captured.
  - [ ] **POST-CONFIRMATION** per `/adk-review:review-pr` `references/post-confirmation.md`:
    - [ ] t=5s re-fetch ran.
    - [ ] If gaps: t=10s, t=20s.
    - [ ] **NO RE-POSTS** on misses.
- [ ] `postback.md` written.

## Phase 6 — pre-handoff

- [ ] `report.md` covers: Result, PR snapshot, Verdict, Per-check table, Decisions, Fix log (if --fix), Validation, Residual risk, Artifact index.
- [ ] Every artifact referenced in `report.md` exists at the cited path.
- [ ] No remote write happened without an approval gate (--post-comment confirmed; --fix push gated).
- [ ] No `--force` in any git command in the session log.
- [ ] No `gh pr merge` in any command in the session log.
- [ ] No comment posted to the PR UNLESS `--post-comment` was set AND user confirmed.
- [ ] No 6-tier severity terminology leaked into the report (assert: no "Blocker" / "Critical" / "Should-Have" / "May-Have" / "Nitpick" wording in `results.md` or `report.md`).
- [ ] Final status banner printed.

## On any check failure

- Log the failure to `validation/per-skill/audit-pr.md` with the failing check + remediation.
- Block the next phase until the failure is resolved.
- If the same check fails 3 times in this session, stop and surface to the user.
- If post-confirmation final-misses, **never re-post** — surface to the user.
- If `--fix` re-validation doesn't yield expected verdict (e.g. lint --fix didn't actually clear all warnings), surface honestly; don't overstate the fix.

## Invariants

- This skill is informational by default. Never posts unless `--post-comment` AND user confirms.
- This skill never auto-fixes outside the safely-fixable subset.
- This skill never produces severity-tiered findings (Pass/Warn/Fail/N/A only).
- This skill never blocks on style nits (those are Warn).
- This skill never auto-merges (no `gh pr merge`).
- This skill never force-pushes.
