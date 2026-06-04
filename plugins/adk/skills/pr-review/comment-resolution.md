# pr-review — classifying pre-existing review threads

Every pre-existing review thread on the PR gets exactly one decision. Re-check the **worktree at the comment's anchor** before deciding — that's the real re-validation.

| Thread state | Condition | Decision |
|---|---|---|
| Open | the diff resolves the concern (verify at `file:line` in the worktree) | **resolve** — cite the `file:line` evidence |
| Open or Resolved | an acceptable reply explains the disposition — offline-aligned, "done in the next PR", "tracked in PROJ-1234", "synced with @alice" | **leave-as-is** |
| Resolved | the diff did **not** resolve it AND no acceptable reply | **reopen** |
| anything else | ambiguous, missing context, bot comment | **leave-as-is** — reason: "ambiguous — needs human" |

## How to act on each decision (gh CLI)

GitHub exposes thread resolve/reopen only via GraphQL:

- **resolve**: `gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"<id>"}) { thread { isResolved } } }'`
- **reopen**: `gh api graphql -f query='mutation { unresolveReviewThread(input:{threadId:"<id>"}) { thread { isResolved } } }'`
- Get thread IDs: `gh api graphql` querying `repository.pullRequest.reviewThreads`.

If the authenticated token can't mutate thread state (insufficient scope / org restriction), fall back to a **status reply** on the thread (`gh api .../comments/<id>/replies` or `gh pr comment`) saying what you concluded ("Resolving — addressed at `path:line`") so a human can flip the actual state.

## Hard rule

Don't re-raise a concern a prior thread already resolved unless the diff **regressed** it. If you would have raised something that a thread already covers, classify the thread instead of adding a duplicate finding.
