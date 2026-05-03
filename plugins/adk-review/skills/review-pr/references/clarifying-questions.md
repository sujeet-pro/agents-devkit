# `review-pr` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently and are surfaced in the final `report.md` Decisions table.

## Phase 0 questions

1. **PR reference: `<resolved owner/repo#num>`. Correct?**
   - _How to pick:_ derived from input (URL or `#N` against current repo). Default = `(approve)`.
   - _Skip when:_ unambiguous URL.

2. **Local checkout for this repo: `<path-from-repos.md>`. Use this?**
   - _How to pick:_ from `~/.config/adk/repos.md`. If repo not listed, default `gh repo clone` into `.temp/task-<slug>/review-checkout/`.
   - _Skip when:_ `--auto` and repo is in `repos.md`.

3. **Detected ownership: `<own|peer>`. Confirm?**
   - _How to pick:_ `author.login` vs `git config user.email` vs `gh api graphql viewer.login`.
   - _Skip when:_ unambiguous (e.g. PR author is the local user, no other identity in play).

## Phase 3 questions

4. **Dimensions to run: `<list>`. Run all six, or a subset?**
   - _How to pick:_ default `all six` (correctness, security, performance, tests, docs, style). Use `--dimensions security,perf` to subset.
   - _Skip when:_ user passed `--dimensions` explicitly.

5. **Restrict scope to a sub-path?**
   - _How to pick:_ default `no` (full diff). Use `--scope src/auth/` if the diff is huge and only one subsystem matters.
   - _Skip when:_ diff is small (<10 files).

## Phase 4 questions

6. **Existing comments to walk: `<count>`. Reconcile all, or skip resolved?**
   - _How to pick:_ default `all` (including resolved — to catch resolved-stale).
   - _Skip when:_ no existing comments.

## Phase 5 questions

7. **Findings to post: `<count by severity>`. Post all, or filter?**
   - _How to pick:_ default `post all validated non-duplicate findings`. Override under `~/.config/adk/review.md.post_only_blockers_under_auto` to post only Blocker/Critical.
   - _Skip when:_ `--auto` and review.md doesn't override.

8. **Post style: one consolidated review (recommended) or N individual comments?**
   - _How to pick:_ default `one consolidated review` (preserves the "single review" UX). Override only on user request.
   - _Skip when:_ `--auto`.

## Phase 6 questions

9. **(--fix only) Apply N fixes? `<list-by-severity>`**
   - _How to pick:_ default `apply all accepted findings`.
   - _Skip when:_ `--auto --fix`.

10. **(--fix only) PUSH-GATE: push `<n>` commits to branch `<head-branch>`? [y/N]**
    - _How to pick:_ NO DEFAULT. Always asks at the first push of the session. Subsequent pushes don't re-ask UNLESS the target branch changed.
    - _Skip when:_ NEVER. This question is mandatory, even under `--auto --fix`.

11. **(--fix only) Commit style: one commit per finding (default) or one squashable commit?**
    - _How to pick:_ default `one per finding` (for traceability). Override at session start with `--squash-fixes`.
    - _Skip when:_ `--auto`.

12. **(own-PR) For drafted reply `<id>`: post as-is, edit, or skip?**
    - _How to pick:_ under `-i`, walks each draft. Default `post as-is` per draft.
    - _Skip when:_ `--auto` and the draft uses a standard template.

## Anti-rules for asking

- **Never ask about something the meta-info already answers.** If `repos.md` has the path, don't ask. If `review.md` has the severity bar, don't ask whether to use it.
- **Never stack multiple questions in one turn.** Iterate.
- **Never ask under `--auto`** — defaults apply silently, surfaced in `report.md`.
- **The PUSH-GATE is the exception.** It always asks (per the universal mode contract; even under `--auto --fix`).
- **Once-per-session.** If the user already answered the same question earlier in this session (e.g. "yes, use one consolidated review"), don't re-ask within the same task slug.
- **No question about whether to post-confirm.** Post-confirmation always runs; it's not negotiable.
- **No question about whether to merge.** The skill never merges, period.
