# `review-feedback` — anti-patterns

## Replies

- **Bulk-resolving comments without per-comment replies.** The reviewer can't tell what changed. Always: reply per-comment, then resolve.
- **Missing the commit SHA in `apply-as-stated`.** The SHA is the proof. Without it, the reply is unverifiable.
- **`wont-fix` with no reasoning.** "Won't fix" alone is rude and unhelpful. Concrete reasoning + offer to discuss is the minimum.
- **`discuss-not-fix` with no follow-up link.** A void. Always link a Jira ticket / sync invite / DM.
- **Resolving a `wont-fix` or `discuss-not-fix` thread.** Those stay open by design. The reviewer accepts or counters.
- **Resolving a thread before the reply post-confirms.** If the reply doesn't land (propagation lag), the resolution is for nothing.
- **Using a non-template reply shape.** Reviewers learn to scan the templates; deviating reduces signal.
- **Re-litigating the design in the thread.** If the reply needs >7 sentences, escalate to a sync conversation.

## Process

- **Re-performing a full review pass.** That's `review-pr`'s job. This skill TRUSTS the reviewer's findings; it doesn't second-guess them.
- **Skipping the classification phase.** The whole skill hinges on classifying first. Don't jump straight to "apply everything".
- **Per-comment fixes when grouping is obvious.** 3 comments flagging the same root issue → one fix, three replies. Skipping the grouping creates three separate commits where one would do.
- **Reading the comments without reading the code.** Without re-reading the code at the comment's target line, you can't tell whether the issue is `already-resolved` (an intervening commit fixed it).
- **Pushing without asking.** Even under `--auto --fix`, the first push always asks.
- **`gh pr merge` after a successful apply round.** Never. Even when it's tempting because "everything's green and the reviewer approved". The merge is the author's call.

## Classification

- **Defaulting everything to `apply-as-stated` without checking the suggestion.** The suggestion may not actually solve the issue (or may break something else). Always sanity-check.
- **Defaulting to `wont-fix` because the suggested fix is bad.** Often the issue IS valid; just write `apply-with-modification` with the better fix.
- **Marking `discuss-not-fix` to defer hard things.** Real `discuss-not-fix` is "this needs a sync conversation". If you can fix it in 10 minutes, fix it.
- **Marking `already-resolved` without verifying against the current code.** The comment may be on a line that LOOKS resolved (whitespace change) but the issue is still in adjacent code.

## `--fix`-specific

- **Validating once at the start of the queue, not after each fix.** If fix #2 breaks tests that fix #5 depends on, you'll only find out at the end. Validate after each fix (or at minimum, in clusters).
- **Force-pushing because the head branch diverged.** That's a `git fetch + rebase` choice, not the skill's call. Surface the divergence; let the user decide.
- **Bundling 7 unrelated fixes into one commit.** Even though `--squash-fixes` is an option, the default of one-per-logical-fix is preferred for traceability — the reviewer can see exactly which commit addressed which comment.
- **Continuing after a fix's validation fails.** Stop the queue; surface; let user decide whether to skip or abort.
- **Reply with "fixed" but no SHA quote.** The reply template requires the SHA in a code-fence block.

## Posting

- **Re-posting on a propagation miss.** Same rule as `review-pr`: never. The cost is duplicate replies that fragment the thread.
- **Posting all replies in one batch then trying to resolve.** Resolve only after each reply individually post-confirms. (The protocol allows batch posting, but resolution is per-thread, after that thread's reply confirms.)
- **Posting to a thread that the reviewer just commented on (newer than the classification).** The reviewer may have changed their mind; consider re-classifying that comment.

## Reporting

- **No classification breakdown in `report.md`.** The user wants `A4/M2/D1/W1/R0` at the top.
- **Hiding the `wont-fix` and `discuss-not-fix` reasons.** Surface in the report — those are where the conversation continues.
- **Saying "validated" without a path to evidence.** Every claim links to a file, a commit SHA, or a comment URL.

## MCP / tooling

- **Defaulting to Docker MCP when `gh` is available.** Cold start is significantly slower; `gh` is the preferred fallback when available.
- **Leaving `GITHUB_READ_ONLY=0` after Phase 5d.** Always restore to `1`.
- **Resolving a thread via the wrong API.** The REST endpoint for "resolve" is via GraphQL only (`mutation { resolveReviewThread(...) }`). Don't try `PATCH /repos/.../comments/<id>/resolve` — doesn't exist.
