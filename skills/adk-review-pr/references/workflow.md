# ADK Review PR Workflow

## Phase 1: Fetch & Confirm

**Gate**: User approval of scope and focus (skipped with `--auto`)

1. Resolve the PR URL, branch name, or diff target to a concrete diff.
2. Fetch the diff using `git diff`, `gh pr diff`, or platform API.
3. List changed files with line counts (additions, deletions).
4. Present scope summary to the user:
   - Files changed and line delta
   - Focus lens (default: `correctness`)
   - Any auto-detected sensitive areas (auth, payments, migrations)
5. Wait for user confirmation or scope adjustment.

**Edge cases**:
- PR URL not accessible: fall back to branch diff against default base.
- Branch not found locally: attempt `git fetch` first.
- Empty diff: report "no changes found" and stop.

## Phase 2: Triage

1. Quick-scan the full diff for severity distribution.
2. Identify hotspot files -- highest risk based on:
   - Change size (large diffs in critical paths)
   - File sensitivity (auth, payments, data migrations, public APIs)
   - Complexity indicators (deep nesting, many conditionals)
3. Flag any files touching security-sensitive areas.
4. Produce a 3-5 bullet triage summary:
   - Total files and line delta
   - Hotspot files with reason
   - Initial risk assessment (low/medium/high)
   - Recommended deep-review order

## Phase 3: Deep Review

1. Process each changed file in risk order from Phase 2.
2. For each file:
   - Read the full diff hunks.
   - Read surrounding context (function boundaries, class structure).
   - Check whether related tests exist and cover the changed paths.
   - Apply the focus lens as primary filter.
   - Never ignore Blocker/Critical issues outside the focus lens.
3. Record each finding with a stable F-ID, severity, confidence, and dimension.
4. If `--focus security` or security-sensitive files are in the diff:
   - Dispatch `adk-security-reviewer` subagent with scoped diff hunks.
   - Merge returned findings, deduplicate, and assign F-IDs.
5. For large diffs (>500 lines):
   - Consider splitting file groups across parallel subagents.
   - Merge and deduplicate results.

**Validation during review**:
- Every finding must cite a specific file:line or diff hunk.
- Speculative findings must carry an explicit confidence label.
- "I think this might be wrong" is never a valid finding without evidence.

## Phase 4: Findings

1. Collect all findings from Phase 3 (including subagent results).
2. Sort by severity: Blocker > Critical > Should Have > May Have > Nitpick > Question.
3. Within same severity, group by file when multiple findings hit the same file.
4. Present using the format defined in `references/review-comment-format.md`:
   ```
   F<n> [Type][Severity]: Title
   Confidence: High|Medium|Low | Dimension: <dim> | Scope: <file:line>
   ```
5. End with triage summary: count by severity level.

## Phase 5: User Response

1. Present the response protocol: `a-N`, `r-N`, `e-N`, `all`.
2. Wait for user input.
3. Process responses:
   - `a-N`: Mark finding as accepted. Add to follow-up list.
   - `r-N`: Mark finding as rejected. Record rejection reason if given.
   - `e-N`: Expand the finding with deeper evidence, surrounding code, reproduction steps.
   - `all`: Accept all findings.
4. If user provides no response and `--auto` is set, treat all findings as presented (no acceptance/rejection).

## Phase 6: Follow-up

1. Summarize accepted findings with their suggested fixes.
2. State residual risk from rejected findings (brief, not argumentative).
3. List recommended next actions:
   - Findings to fix immediately
   - Issues to file for later
   - Follow-up verification needed
4. Offer to hand off accepted findings to `adk-address-review-feedback`.

## Validation Rules

- Every finding cites evidence from the diff or surrounding code.
- Severity ordering is internally consistent across all findings.
- Missing validation and testing gaps are explicitly called out.
- No finding is duplicated across parallel agent results.
- Speculative findings always carry a confidence label.
- The review stays within the diff surface unless a finding demands broader context.

## Edge Case Handling

| Situation | Action |
| --- | --- |
| Empty diff | Report "no changes found" and stop |
| Binary files in diff | Note them, skip code review, flag if security-relevant |
| Merge conflicts present | Stop review, tell user to resolve conflicts first |
| PR already merged | Warn user, offer to review the merge commit diff instead |
| Very large diff (>2000 lines) | Split into file groups, dispatch parallel subagents |
| No test files changed | Always flag as a finding (severity depends on change risk) |
| Diff includes generated files | Skip generated files, note they were excluded |
