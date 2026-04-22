# Output Format for `adk-review-pr`

The skill always produces two layers of output: a **default** (concise, decision-oriented) report and an **on-request detailed** report.

## Status banner (always first)

Lead the report with one of:

```
REVIEW-DRAFT (dry-run)  |  REVIEW-POSTED <n inline> + <summary>  |  AWAITING-APPROVAL-TO-POST  |  REVIEW-RECONCILED <n existing> kept / <n> stale
```

## Default report (always shown)

```
<status banner>

## PR Review: <PR title> (#<number>)
- URL: <pr-url>
- Provider: <github | bitbucket>
- Diff: <files> files, +<additions> / -<deletions>
- Focus: <focus>
- Reconciliation aggressiveness: <validate-then-keep | aggressive-cleanup | read-only>
- Post mode: <dry-run | posted | awaiting-approval>

## Verdict
<approve | request-changes | comment>

## Existing-comment reconciliation
- Threads inspected: <n>
- Kept open (still apply): <n>
- Resolved-confirmed: <n>
- Resolved-stale (reopened): <n>
- Moved (restated at new location): <n>
- No-longer-applicable (dismissed): <n>
- Pushback (reviewer was wrong): <n>
- Bitbucket tasks: <opened> / <resolved> / <reopened>

## Findings

### Blockers
<Finding cards per `pr-review-comment-format.md`>

### Critical
<Finding cards>

### Should Have
<Finding cards>

### May Have
<Finding cards>

### Nitpicks
<Finding cards>

### Questions
<Finding cards>

### Praise
<Finding cards if any>

## Out of Scope
- <items explicitly not reviewed and why>

## Validation (per `pr-review-validator.md`)
- Phase 1 (pre-execution): OK
- Phase 2 (mid-flow gates): OK
- Phase 3 (pre-post): OK
- Phase 4 (post-execution): <OK | N/A in dry-run>
- Validator log: `.temp/notes/review-pr-<provider>-<n>-validator.md`

## Postback summary (if posted)
- Inline comments posted: <n>
- Tasks created / resolved / reopened: <n> / <n> / <n>
- Reconciliation replies posted: <n>
- Summary comment: <YES | N/A>
- Failed to post: <list or none>

## Decisions auto-picked (if --auto)
- <decision> — <one-line rationale>

## Residual risk
- <bulleted, prioritized>

Need more detail on any finding? Pass `--verbose` or ask explicitly.
```

## Detailed report (on request, or under `--verbose`)

Add to the default:

- Per-dimension narrative (correctness / security / performance / style / tests).
- Drift map: which existing threads moved, which became stale, which still apply.
- Lint / test / type-check output captured during validation.
- Suggested patches as fenced code blocks (one per finding where useful).
- Full Phase 1-4 validator log inline (otherwise referenced by `.temp/` path).

## Severity ladder

`Blocker > Critical > Should Have > May Have > Nitpick > Question`. Lead with the highest. Never mix levels in one bullet.

## Decisions auto-picked under `--auto`

When running under `--auto`, the report MUST list each decision the skill auto-picked, with a one-line rationale, so the user can audit retrospectively. The list always includes:

- focus (default `all`)
- post-mode (under `--auto`, default `post`)
- reconciliation aggressiveness (default `validate-then-keep`)
- task strategy (Bitbucket only; default `task-per-blocker-and-critical`)

## Verbosity rules

- Lead with the status banner, then the verdict, then findings ordered by severity.
- Use bullets for process and counts; reserve prose for finding `Issue Explanation` sections.
- Do not dump long context unprompted; offer it instead.
- Quote primary evidence (file:line, command output) inline for findings; keep raw analyzer output and the validator log in `.temp/notes/`.
