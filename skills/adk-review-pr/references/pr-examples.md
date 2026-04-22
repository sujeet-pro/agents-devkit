# Examples for `adk-review-pr`

Concrete inputs the skill expects and the shape of what comes back.

## Trigger phrases

- "Review this PR: <url>"
- "Run `adk-review-pr` on <url>"
- "Take a look at <url> before I merge"
- "Re-review my PR; the author pushed new commits"
- A user request that matches the skill's "When to use" section in `SKILL.md`.

## Sample invocations

```
adk-review-pr https://github.com/org/repo/pull/842 --focus correctness,security
```

Default-ask flow: confirms focus and post-mode, runs reconciliation, presents findings, asks for accept-or-edit per finding (`a-1,3,5`, `r-2`, `e-4`), then posts on approval.

```
adk-review-pr https://bitbucket.org/org/repo/pull-requests/17 --post-mode post --auto
```

`--auto` flow: skips approval gates, picks documented defaults (focus=all, reconciliation=validate-then-keep, task strategy=task-per-blocker-and-critical), validates, posts.

```
adk-review-pr https://bitbucket.org/org/repo/pull-requests/17 --reconciliation aggressive-cleanup
```

Aggressive cleanup: also dismisses no-longer-applicable threads from earlier rounds.

```
adk-review-pr https://github.com/org/repo/pull/842 --focus security --post-mode dry-run
```

Narrow re-review: only security findings, dry-run only (no post).

## Sample output (dry-run, condensed)

````text
REVIEW-DRAFT (dry-run)

## PR Review: Add retry logic to HTTP client (#842)
- URL: https://github.com/org/repo/pull/842
- Provider: github
- Diff: 4 files, +118 / -23
- Focus: correctness, security
- Reconciliation: validate-then-keep
- Post mode: dry-run

## Verdict
request-changes (1 Blocker, 2 Critical)

## Existing-comment reconciliation
- Threads inspected: 3
- Kept open (still apply): 1
- Resolved-confirmed: 2
- (other counts: 0)

## Findings

### Blockers
F1 - see card below.

### Critical
F2, F3 - see cards below.

### Should Have
(2 findings; expand with --verbose)

***

### F1 [Blocker][Issue][correctness] Retry loop ignores 4xx and re-hits the server forever

Location: `src/http/retry.ts:47-58`
Action: post new inline comment
Task: create

Why post this comment:
- The retry policy treats every error as transient.
- 4xx responses (e.g., 401/403/404) will be re-tried until the deadline.

Exact comment to post (rendered as Markdown on the PR):

    **[Blocker][correctness] Retry loop ignores 4xx and re-hits the server forever**

    **Confidence:** 95/100 | **Dimension:** correctness | **Guideline:** HTTP retry semantics - only retry transient (5xx, network) errors

    **Issue Explanation:**
    `shouldRetry()` returns `true` whenever an error is thrown (`src/http/retry.ts:47-58`). 4xx responses (401/403/404) are non-transient and will be retried until the configured deadline, hammering the server and surfacing as request timeouts to the caller.

    **Suggested Fix:**
    Restrict retry to 5xx and network errors. For example:

        function shouldRetry(error: unknown): boolean {
          if (error instanceof NetworkError) return true;
          if (error instanceof HttpError && error.status >= 500) return true;
          return false;
        }

    **Impact:**
    4xx responses become latency cliffs and produce false-positive timeouts in logs. Authentication failures retry until the deadline, masking the real error from callers.

Reviewer explanation:
The fix is one function. There is one existing test in `retry.test.ts` that asserts the bad behavior (line 88) - it should be updated alongside the fix.

***

(F2, F3 omitted in this excerpt)

## Validation
- Phase 1 (pre-execution): OK
- Phase 2 (mid-flow): OK
- Phase 3 (pre-post): OK (8 findings, 0 duplicates)
- Phase 4 (post-execution): N/A (dry-run)
- Validator log: .temp/notes/review-pr-github-842-validator.md

Need more detail on any finding? Reply with `F<n>` to expand, or `--verbose` for everything.
````

## Sample output (after `--post-mode post` approval)

```
REVIEW-POSTED 8 inline + summary

## Postback summary
- Inline comments posted: 8 (IDs: gh:rc_2148931, ...)
- Reconciliation replies posted: 2
- Summary comment: YES (gh:c_2148950)
- Verdict posted: request-changes
- Failed to post: none
- Validator log: .temp/notes/review-pr-github-842-validator.md
```
