# `review-feedback` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently and are surfaced in `report.md`.

## Phase 0 questions

1. **PR reference: `<resolved owner/repo#num>`. Correct?**
   - _How to pick:_ derived from input (URL or `#N`). Default = `(approve)`.
   - _Skip when:_ unambiguous URL.

2. **Use the user's main checkout at `<path>`?**
   - _How to pick:_ default `yes` if main checkout exists + clean + on PR head branch. Else: `git worktree add` to `.temp/.../feedback-checkout/`.
   - _Skip when:_ `--auto` and main checkout is suitable.

## Phase 3 questions

3. **Comment classification table — confirm or re-classify?**
   - _How to pick:_ default `confirm`.
   - _Skip when:_ `--auto`.
   - Under `-i`: walks each comment, allows re-classify per-comment.

4. **Comment grouping: `<n>` groups across `<m>` comments. OK?**
   - _How to pick:_ default `yes` (groupings derived from same-root-cause heuristic).
   - _Skip when:_ `--auto`.

## Phase 5 questions

5. **(--fix only) Apply N grouped fixes?**
   - _How to pick:_ default `apply all apply-* classifications`.
   - _Skip when:_ `--auto --fix`.

6. **(--fix only) Commit style: one per logical fix (default) or `--squash-fixes`?**
   - _How to pick:_ default `one per logical fix`.
   - _Skip when:_ `--auto`.

7. **(--fix only) PUSH-GATE: push `<n>` commits to branch `<head-branch>`?**
   - _How to pick:_ NO DEFAULT. Always asks at first push of session. Subsequent pushes don't re-ask UNLESS target branch changed.
   - _Skip when:_ NEVER.

8. **(--fix only) Resolve `apply-*` threads after replies confirm?**
   - _How to pick:_ default `yes`. Override with `--no-resolve` (useful when reviewer should verify before resolution).
   - _Skip when:_ `--auto --fix` (default applies).

9. **(after a fix's validation fails) Stop, skip, or delegate?**
   - _How to pick:_ default `stop`. Surface the failure.
   - _Skip when:_ NEVER.

## Anti-rules for asking

- **Never ask about something the meta-info answers.**
- **Never stack 3 questions in one turn.**
- **Never ask under `--auto`** — defaults apply silently.
- **PUSH-GATE always asks.** Even under `--auto --fix`.
- **No question about whether to post-confirm.** Always runs.
- **No question about whether to merge.** The skill never merges.
- **No question about whether to resolve `discuss-not-fix` / `wont-fix` / `already-resolved` threads.** They stay OPEN by design.

## Why this skill asks fewer questions than `review-pr`

- No new findings → no severity tier / dimension question.
- No reconciliation against own findings → fewer dedupe questions.
- No own/peer ownership branch → no ownership question.
- The classification phase is structured (5 fixed states), not open-ended.

Under `--auto --fix`, the typical interaction is:

1. Skill: "PUSH-GATE: push 5 commits to branch `pr-2841-feedback-fixes`? [y/N]"
2. User: `y`
3. Skill: runs end-to-end; surfaces report.

That's it.
