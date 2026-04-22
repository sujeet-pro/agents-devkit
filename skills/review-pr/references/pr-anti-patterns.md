# Anti-patterns for `adk-review-pr`

Things that look reasonable but break this skill's contract. Reject them on sight.

## Review-shape anti-patterns

- Mixing severities in one bullet ("nit / blocker?"). Pick one Type + Severity.
- Findings without evidence. If you cannot quote it, do not file it.
- Reviewing the PR description instead of the code.
- Stating "looks good" without enumerating what was inspected.
- Letting Nitpicks dominate the summary; reorder by severity.
- Inventing file paths or line numbers; always cite from the actual diff.
- Filing the same finding against multiple files when it is one root cause; consolidate per `pr-review-comment-format.md`.
- Severity inflation (every finding is `Blocker`); the team stops trusting the verdict.
- Severity deflation (a real bug filed as `Suggestion`); the team merges with a known issue.

## Reconciliation anti-patterns

- Skipping `pr-comment-reconciliation.md` and producing a "fresh" review that re-files what's already raised.
- Resolving a Bitbucket task because the author replied "fixed" without re-validating against the current code.
- Closing an existing thread because the file moved, without restating the concern at the new location.
- Posting a "new" finding that duplicates an existing thread; the author cannot tell what is new vs already-handled.
- Pushback replies without concrete code citations; "I don't agree" is not a pushback.

## Posting anti-patterns

- Posting before the user approves (unless `--auto`).
- Stapling multiple findings into one inline comment.
- Posting an Approve verdict automatically — never. The Approve button is always a human action, even with `--auto`.
- Posting a Request-Changes verdict for Nitpicks alone.
- Posting comments that do not match the canonical shape from `pr-review-comment-format.md`.
- Re-posting a comment that already succeeded in a previous run; idempotency per `pr-artifact-format.md` is mandatory.

## Validator anti-patterns

- Skipping any of the four validator phases in `pr-review-validator.md`.
- Treating WARN as OK silently; WARNs must surface in the report.
- Claiming `validated` without writing the validator log to `.temp/notes/`.

## Workflow anti-patterns

- Acting outside this skill's scope; route to:
  - `adk-review-local` for un-pushed work.
  - `adk-review-feedback` for addressing existing reviewer comments on someone else's review of YOUR PR.
  - `adk-audit-repo` for whole-repo, multi-dimensional audits.
  - `adk-docs-review` for doc-only review (with or without `--mode confluence`).
- Editing the working tree during a PR review (read-only mode).
- Routing to two skills at once instead of chaining.

## Engineering anti-patterns the reviewer should flag (not commit themselves)

These are the things the reviewer should look FOR in the PR being reviewed (and convert into findings):

- Adding new abstractions, dependencies, or infrastructure for a small change without a documented justification.
- Mixing unrelated concerns in one PR (feature + refactor + bumps).
- Tests that assert implementation details instead of behavior.
- Catch-all `try/catch` that swallows errors silently.
- New code without tests when the changed area has them.
- Disabled / skipped tests without a tracking link.
- Hard-coded secrets, env-specific values, or PII.
