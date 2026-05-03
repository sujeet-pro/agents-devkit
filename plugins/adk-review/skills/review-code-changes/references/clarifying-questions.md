# `review-code-changes` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently and are surfaced in `report.md`'s Decisions table.

## Phase 0 questions

1. **Detected baseline: `<ref>` (source: `<source>`). Use this?**
   - _How to pick:_ default is the documented order: `@{upstream}` → `origin/<branch>` → `main` → `master` → first-parent.
   - _Skip when:_ `--auto` and the source ∈ {tracking, remote, main, master, arg}. Surface but don't ask.
   - _Always ask when:_ source = `first-parent` (the fallback) — it might be wrong.

2. **Slug: `<derived-from-branch>`. OK?**
   - _How to pick:_ default = the branch name kebab-cased.
   - _Skip when:_ `--auto`.

## Phase 1 questions

3. **Run cheap lint pre-pass (`<command>`)? It will inform the style dimension.**
   - _How to pick:_ default `yes` if the command runs in <30s. Skip if larger.
   - _Skip when:_ `--auto`.

## Phase 2 questions

4. **Scope: branch=<n>, staged=<n>, unstaged=<n>, untracked=<n>. Include all four?**
   - _How to pick:_ default `yes`. The `--no-untracked` flag excludes untracked.
   - _Skip when:_ `--auto` and no flag overrides.

5. **`--scope <path>` to focus on a sub-path?**
   - _How to pick:_ default `no`. Useful when the working tree has WIP across multiple subsystems.
   - _Skip when:_ user passed `--scope` explicitly OR the scope is small (<10 files).

## Phase 3 questions

6. **Dimensions: `<list>`. Run all six, or a subset?**
   - _How to pick:_ default `all six`.
   - _Skip when:_ user passed `--dimensions` explicitly.

## Phase 4 questions

7. **Findings to include: `<count by severity>`. Show full report, or filter?**
   - _How to pick:_ default `show all validated findings`. Override under `~/.config/adk/review.md.post_only_blockers_under_auto` (although for this skill, "post" is "include in report").
   - _Skip when:_ `--auto`.

## Phase 5b questions (--fix only)

8. **Apply N fixes? `<list-by-severity>`**
   - _How to pick:_ default `apply all accepted findings`.
   - _Skip when:_ `--auto --fix`.

9. **Commit-after-fix policy: leave dirty (default), or commit per-finding?**
   - _How to pick:_ default `leave dirty` so user can `git diff` and commit manually.
   - _Skip when:_ `--auto --fix`.

10. **(after a fix's validation fails) Stop, or skip and continue?**
    - _How to pick:_ default `stop`. Surface the failure; don't try to fix the fix.
    - _Skip when:_ NEVER. This is a hard stop; user has to engage.

## Phase 6 questions

11. **Show full report, or just the executive summary?**
    - _How to pick:_ default `executive summary` + offer-depth.
    - _Skip when:_ `--auto`.

## Anti-rules for asking

- **Never ask about something the meta-info answers.** If `repos.md` has the path, don't re-ask.
- **Never stack 3 questions in one turn.** Iterate.
- **Never ask under `--auto`** — defaults apply silently, surfaced in `report.md`.
- **No question about whether to push.** The skill never pushes.
- **No question about whether to comment-post.** The skill never posts.
- **The fallback baseline (first-parent) IS asked even under `--auto`** — wrong baseline gives a wrong review; better to ask once.

## Why this skill asks fewer questions than `review-pr`

- No remote interaction → no MCP/transport question.
- No comment posting → no post-style / post-mode question.
- No reconciliation → no per-existing-comment question.
- No ownership branch → no own/peer detection question.
- No push → no push-gate question.

Under `--auto`, this skill typically asks ZERO questions and runs end-to-end.
