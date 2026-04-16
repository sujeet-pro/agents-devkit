# ADK Address Review Feedback Workflow

## Phase 1: Gather

**Gate**: None (gathering is always safe)

1. Read the feedback source:
  - **PR thread**: Fetch comments via platform API or `gh pr view --comments`.
  - **Local review notes**: Read the specified markdown file.
  - **F-ID list**: Parse structured findings from a previous review session (e.g., "a-1, a-2, a-5").
  - **Free text**: Parse pasted feedback into discrete findings.
2. Extract each distinct finding:
  - Original F-ID (preserve if present; assign sequential IDs if not).
  - Severity from the original review.
  - File:line reference.
  - Description of the concern.
  - Suggested fix (if the reviewer provided one).
  - Code suggestion (if the reviewer provided inline code).
3. List all extracted findings for the triage phase.

**Edge cases**:

- PR URL not accessible: try local branch comments or ask user to paste feedback.
- Empty feedback source: report "no findings to address" and stop.
- Duplicate findings: deduplicate, keep the most specific version.

## Phase 2: Triage

1. Classify each finding:
  - **Accepted**: Clear, actionable, the author agrees. Will be fixed.
  - **Rejected**: Author disagrees. Will not be fixed. Record the reason.
  - **Needs Discussion**: Ambiguous, has trade-offs, or requires clarification before fixing.
2. For each accepted finding, assess complexity:
  - **Simple**: Single file, <10 lines, obvious fix. Handle directly.
  - **Moderate**: Single file, 10-30 lines, or non-obvious logic. Handle directly with care.
  - **Complex**: Multiple files, >30 lines, or architectural impact. Consider subagent dispatch.
3. For findings with reviewer-suggested code:
  - Check if the suggestion can be applied as-is.
  - Note if it needs adaptation (syntax, style, context).
  - Flag if the suggestion would break other code.
4. Present triage summary.

## Phase 3: Plan Fixes

**Gate**: User approval (skipped with `--auto`)

1. For each accepted finding, create a fix plan entry:
  - F-ID
  - Target file(s) and line(s)
  - Fix summary (one sentence)
  - Source: reviewer suggestion / own fix / needs investigation
  - Complexity: simple / moderate / complex
  - Risk: none / may affect tests / may affect other code
2. Group related findings that share a file or logical unit.
  - Group only when fixing one naturally addresses the other.
  - Never bundle unrelated fixes.
3. Order by dependency: fix upstream issues before downstream ones.
4. Flag any fix that:
  - Might break existing tests.
  - Requires changes beyond `--scope`.
  - Needs new test coverage.
5. Present the fix plan table.
6. Wait for user approval or adjustment.

## Phase 4: Implement

1. Apply fixes in the planned order.
2. For each fix:
  - Read the target file and surrounding context (function boundaries, callers, related tests).
  - Apply the smallest change that resolves the finding.
  - Preserve existing code style: indentation, naming conventions, patterns.
  - If the reviewer included a code suggestion, use it directly unless:
    - It has a syntax error (fix the syntax, keep the intent).
    - It would break other code (report the conflict, skip the fix).
    - It contradicts project conventions (note the deviation, suggest an alternative).
3. For complex fixes (multiple files, >30 lines, architectural):
  - Dispatch `adk-implementer` subagent with:
    - The specific finding and fix plan.
    - Relevant file context.
    - Clear success criteria.
    - Instruction to preserve code style.
  - Review the subagent's output before accepting.
4. After each fix, record:
  - What changed (before/after summary).
  - Files modified.
  - Whether the fix followed the reviewer's suggestion or deviated (with reason).

**Rules during implementation**:

- Do not refactor surrounding code.
- Do not add unrelated improvements.
- Do not change code style.
- Do not introduce new dependencies.
- If a fix reveals a new issue, note it for a separate pass.

## Phase 5: Verify

1. For each applied fix:
  - Confirm the change addresses the original finding (re-read the reviewer's comment, compare against the fix).
  - Run available validation:
    - Linter: does the changed file pass?
    - Type check: do types still resolve?
    - Tests: do related tests pass?
  - Check that surrounding code is not broken.
2. If validation fails:
  - Record the failure with detail (which check failed, error message).
  - Assess whether the fix is wrong or the test/linter needs updating.
  - If the fix is wrong: revert and mark as **Failed**.
  - If the test needs updating: note it as a **Follow-up** action.
3. Verification status per finding:
  - **Verified**: Fix applied, validation passed.
  - **Unverified**: Fix applied, no validation available (note what to check manually).
  - **Failed**: Fix attempted, validation failed (include error details).

## Phase 6: Report

1. Present the final status table:
  ```
   | F-ID | Status   | File             | Summary                              |
   | ---- | -------- | ---------------- | ------------------------------------ |
   | F-1  | Fixed    | src/config.ts:42 | Null check added                     |
   | F-2  | Fixed    | src/auth.ts:18   | Auth middleware applied              |
   | F-3  | Deferred | src/utils.ts     | Refactor out of scope                |
   | F-4  | Follow   | --               | Benchmark needs manual run           |
   | F-5  | Failed   | src/api.ts:55    | Fix breaks downstream test           |
  ```
2. Status levels:
  - **Fixed**: Applied and verified (or applied and unverifiable, noted).
  - **Deferred**: Acknowledged, not applied. Reason stated.
  - **Follow-up**: Needs reviewer action or manual verification.
  - **Failed**: Fix attempted but validation failed. Details provided.
3. Summary counts: N fixed, N deferred, N follow-up, N failed.
4. Validation summary: linter/tests/type-check pass/fail.
5. Ready-to-merge assessment:
  - **Yes**: All blockers and criticals fixed, validation passes.
  - **No**: Blockers or criticals remain unfixed or failed.
  - **Partial**: Some fixed, some deferred with acceptable risk.
6. Remaining actions for developer or reviewer.

## Validation Rules

- Every fixed finding has a before/after diff or clear description of the change.
- Validation (linter, tests, type check) is run after all fixes when tools are available.
- No unrelated changes are introduced (diff should only touch finding-relevant code).
- Deferred and follow-up items are explicitly listed with reasons.
- Failed fixes include the failure reason and any error output.
- The fix commit is reviewable: isolated changes, clear intent, no bundled cleanup.

## Edge Case Handling


| Situation                                                | Action                                                            |
| -------------------------------------------------------- | ----------------------------------------------------------------- |
| Feedback source is empty                                 | Report "no findings to address" and stop                          |
| Finding references a file that no longer exists          | Note as stale, classify as Deferred                               |
| Finding is already addressed (code changed since review) | Verify the fix, note "already addressed"                          |
| Reviewer's suggestion has a syntax error                 | Fix the syntax, keep the intent, note the correction              |
| Fix would break existing tests                           | Report the conflict, mark as Failed, suggest resolution           |
| Fix requires changes outside `--scope`                   | Report, ask user to expand scope or defer                         |
| Multiple findings conflict with each other               | Report the conflict, fix the higher-severity one, defer the other |
| Fix is trivial but finding was marked Blocker            | Apply the fix; severity does not affect fix complexity            |
| Finding has no clear suggested fix                       | Investigate the concern, propose a fix, present for approval      |


