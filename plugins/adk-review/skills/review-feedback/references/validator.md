# `review-feedback` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/review-feedback.md`.

## Phase 0 — pre-execution

- [ ] PR URL / number parsed; resolved to `<owner>/<repo>#<num>`.
- [ ] Local checkout located (main checkout preferred; worktree only if main is unavailable).
- [ ] Slug derived (with `feedback-` prefix).
- [ ] `.temp/task-<slug>/` exists; gitignored.
- [ ] `prompt.txt` written (verbatim user prompt + ISO ts + resolved PR URL).
- [ ] Mode parsed (`auto` | `interactive` | + `fix`); incompatible combos refused.

## Phase 1 — preflight

- [ ] `bin/adk-mcp-health --shipped --json` shows `github.connected: true` OR `gh auth status` succeeds.
- [ ] MCP client choice recorded (gh-cli preferred when both available).
- [ ] `gh api /user` returns 200.
- [ ] For `--fix`: `gh api /repos/<repo>` shows `permissions.push: true`.
- [ ] For `--fix`: working tree clean; warned otherwise.
- [ ] `gh api /repos/<repo>/branches/<base>/protection` fetched; for `--fix`, head branch is not protected.
- [ ] `bin/adk-info github --check` returns 0.
- [ ] `bin/adk-info repos --check` returns 0.
- [ ] `forbid_force_push_branches` loaded from `github.md`.

## Phase 2 — fetch context

- [ ] `feedback/pr-context/pr.json` exists; head SHA recorded.
- [ ] `feedback/pr-context/comments.json` exists with full pagination.
- [ ] `feedback/pr-context/issue-comments.json` exists.
- [ ] `feedback/pr-context/reviews.json` exists.
- [ ] `feedback/pr-context/threads.json` exists (GraphQL, for resolved state).
- [ ] `--scope <id-list>` filter applied if provided.
- [ ] At least 1 open / unresolved comment present (else: stop with "no open comments to address").

## Phase 3 — classify

- [ ] Every open comment has a classification ∈ {apply-as-stated, apply-with-modification, discuss-not-fix, wont-fix, already-resolved}.
- [ ] Every classification has a one-line `Reasoning` field.
- [ ] `apply-with-modification` includes the modification rationale.
- [ ] `wont-fix` includes concrete reasoning (>1 sentence).
- [ ] `discuss-not-fix` includes a follow-up link or scheduled sync.
- [ ] `already-resolved` includes the verifying line/SHA showing the issue is no longer present.
- [ ] Comment grouping applied per `references/comment-grouping.md`.
- [ ] `classification.md` written.

## Phase 4 — propose

- [ ] Counts surfaced: A/M/D/W/R.
- [ ] Under `-i`: each classification walked; user re-classifications captured.
- [ ] Under `--auto`: classifications kept as-is.
- [ ] Approval gate (unless `--auto`): user confirmed classifications.

## Phase 5a — draft replies (always)

- [ ] Every classification has a drafted reply per `references/reply-templates.md`.
- [ ] `apply-*` drafts have a `<commit-sha>` placeholder (filled in 5b).
- [ ] No reply quotes >15 words from the original comment verbatim.
- [ ] No reply contains an emoji (per the universal interaction contract).
- [ ] No reply omits the attribution line.
- [ ] `replies-draft.md` written.

## Phase 5b — apply (`--fix` only)

- [ ] Fix queue built from groupings (per `comment-grouping.md`).
- [ ] For each grouped fix: applied (inline or via `/adk-code:code-bugfix`).
- [ ] Repo-native validation ran after each fix (or once at end if scope is small).
- [ ] If validation failed mid-queue: stopped applying further fixes; surfaced.
- [ ] Commits captured (one per logical fix, or one squashable if `--squash-fixes`).
- [ ] `fix-log.md` written.
- [ ] `<commit-sha>` placeholders in `replies-draft.md` filled.

## Phase 5c — push (`--fix` only)

- [ ] PUSH-GATE asked at first push of session (even under `--auto --fix`).
- [ ] `git push` did not include `--force` (assert).
- [ ] Push target is NOT in `forbid_force_push_branches`.
- [ ] Push succeeded; SHA recorded in `fix-log.md`.

## Phase 5d — post replies + resolve

- [ ] Replies posted with receipt IDs captured.
- [ ] **POST-CONFIRMATION** completed (per `/adk-review:review-pr` `references/post-confirmation.md`):
  - [ ] t=5s re-fetch ran.
  - [ ] If gaps: t=10s re-fetch ran.
  - [ ] If gaps: t=20s re-fetch ran.
  - [ ] Final: every receipt classified `confirmed` or `unconfirmed`.
  - [ ] **NO RE-POSTS** on misses.
- [ ] For `apply-*` classifications with confirmed replies: thread resolved via `gh api graphql resolveReviewThread`.
- [ ] For `discuss-not-fix` / `wont-fix` / `already-resolved`: thread NOT resolved (assert: no `resolveReviewThread` call for these IDs).
- [ ] `replies-postback.md` written.
- [ ] `GITHUB_READ_ONLY=1` restored (if MCP was used).

## Phase 6 — pre-handoff

- [ ] `report.md` covers: Result, PR snapshot, Classification summary, Per-comment table, Fix log (if --fix), Validation, Decisions, Threads left open, Residual risk, Artifact index.
- [ ] Every artifact referenced in `report.md` exists at the cited path.
- [ ] No remote write happened without an approval gate (or `--auto`).
- [ ] No `--force` in any git command in the session log.
- [ ] No `gh pr merge` in any command in the session log.
- [ ] No new findings posted (assert: this skill never posts new inline review comments — only replies + resolutions).
- [ ] Final status banner printed.

## On any check failure

- Log the failure to `validation/per-skill/review-feedback.md` with the failing check + remediation.
- Block the next phase until the failure is resolved.
- If the same check fails 3 times in this session, stop and surface to the user.
- If the post-confirmation final miss occurs, **never re-post** — surface to the user.
- If `--fix` validation fails, stop applying further fixes — do NOT try to "fix the fix".
