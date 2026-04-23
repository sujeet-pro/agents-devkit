# `review-pr` — modes

This skill supports the following `--mode` values:

| Mode | Behavior |
| --- | --- |
| `auto` (default) | Ownership-aware delivery. If the PR is NOT yours → run Path A (review-and-post). If the PR IS yours → run Path B (validate existing reviewer comments, draft replies via `adk-review-feedback`, no code edits). Approval gates active unless `--auto`. |
| `review` | Force findings-only / replies-only. Never edits code. Bypasses `--fix` even if also passed. |
| `fix` | Run `--mode auto` then, on Path B (`mine`), locally apply the `Apply`'d reviewer comments via `adk-build-bugfix` / `adk-build-refactor` / `adk-build-feature`, then re-run `adk-review-local` against the changed files. Local commits stay staged — push is a separate, user-gated action. On Path A (`not-mine`), `--fix` is silently ignored — you can't push commits to someone else's branch. |

`--auto` is orthogonal and skips approval gates regardless of `--mode`.
The `--fix` flag is a shorthand for `--mode fix`.
See `@adk:mode-contract` (a.k.a. `adk-mode-contract`) for the universal contract.

## Ownership detection

Compare the PR's `author.login` (GitHub) or `user.account_id` (Bitbucket) against:

1. `gh auth status` (GitHub) — preferred when authenticated.
2. `git config user.email` — falls back when no provider auth.
3. Bitbucket username from the configured MCP / app password — Bitbucket fallback.

Result: `mine` | `not-mine`. Surface the comparison in the status banner. The `<ownership>` input (`mine` / `not-mine` / `auto`) overrides the detection. When the auto-detection has low confidence (no remote auth, ambiguous identity, fork PR), STOP and clarify with the user.

## Path matrix

| Source ownership | Default Path | Default delivery | What `--fix` does |
| --- | --- | --- | --- |
| `not-mine` | Path A — review-and-post | `post` (inline + summary; Bitbucket tasks for Blockers + Critical) | Silently ignored |
| `mine` | Path B — feedback-and-fix | `dry-run-replies` (drafted, awaiting approval), then `post` after approval | Locally apply `Apply`'d comments via adk-build-* skills; commit; never auto-push |

`--mode review` always falls back to a non-posting variant: Path A → Markdown report only. Path B → drafted replies in `.temp/` only.
