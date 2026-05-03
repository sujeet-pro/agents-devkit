# `review-pr` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/review-pr.md`.

## Phase 0 — pre-execution

- [ ] PR URL / number parsed; resolved to `<owner>/<repo>#<num>`.
- [ ] `.temp/task-<slug>/` exists and is gitignored.
- [ ] `prompt.txt` written (verbatim user prompt + ISO ts + resolved PR URL + ownership).
- [ ] Local checkout located via `repos.md`, OR `gh repo clone` queued.
- [ ] `git worktree add .temp/task-<slug>/review-checkout/ <head-sha>` succeeded.
- [ ] Ownership detected (`own` or `peer`) and recorded.
- [ ] Mode parsed (`auto` | `interactive` | + `fix`); incompatible combos refused.

## Phase 1 — preflight

- [ ] `bin/adk-mcp-health --shipped --json` shows `github.connected: true` OR `gh auth status` returns success.
- [ ] MCP client choice recorded (gh-cli preferred when both available).
- [ ] `gh api /user` returns 200.
- [ ] For `--fix`: `gh api /repos/<repo>` shows `permissions.push: true`.
- [ ] In worktree: `git status --porcelain` is clean for `--fix`; warned otherwise.
- [ ] `gh api /repos/<repo>/branches/<base>/protection` fetched; for `--fix`, head branch is not protected.
- [ ] `bin/adk-info github --check` returns 0.
- [ ] `bin/adk-info review --check` returns 0.
- [ ] `forbid_force_push_branches` loaded from `github.md`.

## Phase 2 — fetch context

- [ ] `pr-context/pr.json` exists; `head.sha` recorded for later anchor checks.
- [ ] `pr-context/diff.patch` exists; size sanity (warn if >10MB).
- [ ] `pr-context/comments.json` exists with full pagination (no `Link: next` left unfollowed).
- [ ] `pr-context/issue-comments.json` exists.
- [ ] `pr-context/reviews.json` exists.
- [ ] `pr-context/threads.json` exists (GraphQL for resolved state).
- [ ] `pr-context/template.md` and `codeowners.txt` written if found.
- [ ] `pr-context/author-history.md` lists last 5 PRs.
- [ ] Repo conventions synthesized from `AGENTS.md` / `CLAUDE.md` / `.cursorrules` if present.

## Phase 3 — full-scope review

- [ ] All requested dimension passes ran (or are explicitly skipped with reason in `raw-findings.md`).
- [ ] Each finding has: severity, file:line, dimension, confidence, evidence (≤15 words), issue, fix, impact.
- [ ] No finding without an `Evidence:` block.
- [ ] No finding tier-less.
- [ ] `~/.config/adk/review.md.severity_bar` overrides applied (re-tier where matched).
- [ ] `~/.config/adk/review.md.ignore_in_repos[<repo>]` filter applied (drop where matched).
- [ ] Same-root-cause de-noise applied (3+ same root → 1 + references).
- [ ] `raw-findings.md` written.

## Phase 4 — reconcile existing comments

- [ ] Every existing comment / reply / resolved task has a classification in `reconciliation.md`.
- [ ] Pushback comments: every one has a "we re-evaluated" note.
- [ ] Resolved-stale: every one has the still-present-code quote.
- [ ] New findings deduped against `still-open` and `pushback`. Duplicates dropped.

## Phase 5 — propose

- [ ] `findings.md` exists, severity-sorted (Blocker first).
- [ ] Under `-i`: walked every finding; recorded each user decision.
- [ ] Under `--auto`: all validated non-duplicate findings kept.
- [ ] Approval gate (unless `--auto`): user said "post these".

## Phase 6a — post (peer's PR)

- [ ] Re-validated line anchors against current head SHA. Dropped findings with shifted lines.
- [ ] `GITHUB_READ_ONLY=0` set (or using `gh`).
- [ ] Post call returned with receipt IDs for every posted finding.
- [ ] `post-receipts.json` written.
- [ ] **POST-CONFIRMATION** completed:
  - [ ] t=5s re-fetch ran.
  - [ ] If gaps: t=10s re-fetch ran.
  - [ ] If gaps: t=20s re-fetch ran.
  - [ ] Final: every receipt classified `confirmed` or `unconfirmed`.
  - [ ] **NO RE-POSTS** on misses (regardless of cause).
- [ ] `GITHUB_READ_ONLY=1` restored.
- [ ] `postback.md` written.

## Phase 6b — validate + reply (own PR)

- [ ] Replies drafted using `references/pr-reply-templates.md` templates.
- [ ] `replies-draft.md` exists.
- [ ] Under `-i`: each draft walked.
- [ ] Replies posted with same post-confirmation protocol as 6a.
- [ ] `replies-postback.md` written.

## Phase 6c — fix (`--fix` mode)

- [ ] Fix queue built (accepted findings, severity-prioritized).
- [ ] For each fix: applied (inline or via `/adk-code:code-bugfix`).
- [ ] Repo-native validation ran after each fix (or once at end if diff is small): tests + typecheck + lint.
- [ ] **PUSH-GATE** asked at first push of the session (even under `--auto --fix`).
- [ ] `git push` did not include `--force` (assert at the gate).
- [ ] Push target is NOT in `forbid_force_push_branches` (or push gate refused).
- [ ] Per addressed comment: reply posted via `pr-reply-templates.md` → `fix-applied`.
- [ ] Comments resolved only after reply post-confirmation.
- [ ] **NO `gh pr merge` calls** (assert in command log).
- [ ] `fix-log.md` written.

## Phase 7 — pre-handoff

- [ ] `report.md` covers: Result, PR snapshot, Findings posted, Findings NOT posted, Decisions, Reconciliation summary, Fix log (if --fix), Validation, Residual risk, Artifact index.
- [ ] Every artifact referenced in `report.md` actually exists at the cited path.
- [ ] No remote write happened without an approval gate (or `--auto`).
- [ ] No `--force` in any git command in the session log.
- [ ] No `gh pr merge` in any command in the session log.
- [ ] Final status banner printed.

## On any check failure

- Log the failure to `validation/per-skill/review-pr.md` with the failing check + remediation.
- Block the next phase until the failure is resolved.
- If the same check fails 3 times in this session, stop and surface to the user — do NOT loop forever.
- If the failed check is the post-confirmation final miss, **never re-post** — that's the rule, not a workaround.
