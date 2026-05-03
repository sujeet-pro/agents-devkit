# `review-pr` — anti-patterns

What to avoid, and why.

## Process

- **Delta-only review.** "I already reviewed v3 of this PR; just look at the new commit." Anti-pattern: the new commit may have introduced a Blocker that changes how an earlier section behaves. Always re-do the full review. The reconciliation phase handles the noise of re-raised findings.
- **Skipping Phase 4 (reconcile).** If you skip reconciliation, you'll re-raise findings the author already addressed (annoying) or the author already pushed back on (worse — looks like you didn't read).
- **Skipping post-confirmation.** Treating a 200 response from `gh pr review --comment` as proof the comment is on the PR. The provider's write-confirm and the read-after-write can lag; without re-fetching, you might think you posted 7 comments and only 5 made it.
- **Re-posting on a propagation miss.** Wait → re-fetch → still missing → DON'T re-post. The most likely cause is propagation lag, not loss. Re-posting creates duplicates that confuse the author.
- **Reviewing on the user's main checkout.** Two parallel PR reviews collide. Always use `git worktree add .temp/task-<slug>/review-checkout/`.
- **Skipping ownership detection.** Posting "fix this!" on your own PR (technically OK but reads as dissociated) or filing a `fix-applied` reply on a peer's PR you haven't touched.
- **Pushing without asking.** Even under `--auto --fix`, the first push of a session always asks. The user might want to push manually after eyeballing the changes.

## Severity / quality

- **Stacking 47 nitpicks before mentioning the one Blocker.** Order findings by severity, not file order. The author should see the Blocker before any Nitpick.
- **Untiered findings.** "This is weird" with no severity = noise. Either tier it or drop it.
- **Vague "could be improved" without a fix.** Every finding includes a one-sentence `Fix:` and a one-sentence `Impact if unfixed:`.
- **Re-explaining the diff.** The author wrote it; they know what it does. Lead with what's wrong, not what changed.
- **Bikeshedding style when lint is silent.** If the repo's lint config doesn't enforce a style choice, don't reopen the debate. Add the rule to the lint config (different PR) or let it go.
- **Drive-by complaints on out-of-diff lines.** The PR is for the diff. Out-of-diff observations belong in `audit-repo`. Exception: an out-of-diff line is *the* root cause of an in-diff bug — call it out as a `Question` and explain.
- **Severity inflation.** Marking "missing test" as `Critical` when the rest of the codebase has comparable coverage gaps. Use `Should-Have` and recommend a follow-up.
- **Severity deflation.** Marking a real auth bypass as `Should-Have` because "the API is internal-only". Internal != trusted. `Critical` or `Blocker`.

## Posting

- **Posting a comment on a stale line.** The diff shifted between Phase 3 and Phase 6. Always re-validate line anchors right before posting.
- **Posting many individual comments instead of one consolidated review.** Use `gh pr review --comment -F <body>` with inline annotations for one logical review. Many individual comments fragment the discussion.
- **Posting without the canonical comment template.** Every posted comment includes Type / Severity / Confidence / Dimension / Issue / Fix / Impact. Skipping the template makes findings hard to scan.
- **Posting a comment without first deduping against existing comments.** You'll annoy the author with repeats.
- **Approving + merging.** `gh pr review --approve` is the line; `gh pr merge` is over the line. Even approval is not always a default — only when the user has the merge bit and the skill saw zero Blockers.

## `--fix`-specific

- **Applying a fix that breaks tests, then pushing.** Always run repo-native validation between fix and push.
- **Bundling 5 unrelated fixes into one commit.** Prefer one commit per finding for traceability. Rebase later if the user wants a clean history.
- **Reply with "fixed" but no commit SHA.** The reply template requires the SHA so reviewers can trace the fix.
- **Resolving a comment without posting a reply.** The reviewer can't tell what you changed. Always reply first, then resolve.
- **Pushing to a wrong branch under `--auto --fix`.** Always show the `git push <remote> <branch>` command at the push gate.
- **Force-pushing because the head branch diverged.** That's a `git fetch + rebase` choice for the author, not the skill's call.

## Reconciliation

- **Re-raising a finding the author pushed back on, without engaging the pushback.** Read the reply; engage with the reasoning. If the new evidence is the same as before, drop the finding.
- **Marking "resolved-stale" without quoting the still-present code.** Make the case with evidence.
- **Confusing "thread resolved" with "issue addressed".** A thread can be resolved by either party clicking the button without code changing.

## MCP / tooling

- **Defaulting to Docker MCP when `gh` is available.** Cold start is significantly slower; `gh` is the preferred fallback when available.
- **Leaving `GITHUB_READ_ONLY=0` after Phase 6.** Always restore to `1` after the post stage so subsequent operations default to safe.
- **Quoting the actual secret if the security pass found a `secret_in_diff`.** Name the type + location, NEVER the bytes.

## Reporting

- **"Validated" without a path to evidence.** Every claim links to either a file in the worktree, a comment URL on the PR, or a commit SHA.
- **Hiding decisions made under `--auto`.** The decision table in `report.md` lists every default the skill picked, with a one-line rationale.
- **Stopping before the executive summary.** The user reads the summary first. Always end with a one-paragraph "Result + Top issue + Counts + Residual risk" block.
