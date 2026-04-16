# ADK Review Local Changes Workflow

## Phase 1: Scan

**Gate**: User confirms scope (skipped with `--auto`)

1. Run `git status` to identify:
   - Staged files (`git diff --cached --name-status`)
   - Unstaged modified files (`git diff --name-status`)
   - Untracked files
2. Run `git diff` (unstaged) and `git diff --cached` (staged) to get the full diff content.
3. If on a branch, identify the base branch:
   - Check `git log --oneline <base>..HEAD` for committed-but-not-pushed changes.
   - Compute `git diff <base>...HEAD` for the full branch diff.
4. If `--scope` is set, filter all diffs to the specified path.
5. Present scope summary:
   - Staged: N files, +A/-D lines
   - Unstaged: M files, +A/-D lines
   - Branch: K commits ahead of base (if applicable)
   - Total review surface
6. Wait for user confirmation or scope adjustment.

**Edge cases**:
- Not in a git repo: stop and tell the user.
- No changes found: report "working tree clean, nothing to review" and stop.
- Merge conflicts present: stop, tell user to resolve conflicts first.
- `--scope` path does not exist: warn and stop.

## Phase 2: Classify

1. Categorize each changed file by risk level:
   - **High risk**: auth, payments, data migrations, public APIs, security-sensitive code, database schema changes
   - **Medium risk**: business logic, state management, API handlers, configuration with runtime impact
   - **Low risk**: documentation, test-only changes, style/formatting, comments, dev tooling
2. Flag files with no corresponding test changes.
3. Produce a risk-ordered file list for Phase 3.
4. Note any generated or vendored files to skip.

## Phase 3: Review

1. Process each file in risk order from Phase 2.
2. For each file:
   - Read the diff hunks (staged and/or unstaged as relevant).
   - Read surrounding context: function boundaries, class structure, imports.
   - Check whether related test files exist and cover the changed paths.
   - Apply the focus lens as primary filter.
   - Never ignore Blocker/Critical issues regardless of focus lens.
3. Record each finding with:
   - Stable F-ID (sequential: F1, F2, ...)
   - Type and severity
   - Confidence level
   - Dimension
   - Scope (file:line)
4. For security-sensitive files, consider dispatching `adk-security-reviewer` subagent.

**Validation during review**:
- Every finding must cite a specific file:line from the local diff.
- Speculative findings must carry an explicit confidence label.
- If surrounding context is needed to verify, read it before recording the finding.

## Phase 4: Findings

1. Collect all findings from Phase 3.
2. Sort by severity: Blocker > Critical > Should Have > May Have > Nitpick > Question.
3. Group by file when multiple findings hit the same file.
4. Present using the format defined in `references/review-comment-format.md`.
5. End with triage summary: count by severity level.

## Phase 5: Recommendations

1. Classify findings into action categories:
   - **Fix before commit**: Blockers and Criticals. These should not be committed as-is.
   - **Acceptable to commit**: Should-Have and below. Can be addressed in follow-up.
   - **Defer**: Nitpicks and Questions. Do not block the current work.
2. Present the classification with clear reasoning.
3. Wait for user response: `a-N`, `r-N`, `e-N`, `all`.
4. Process responses:
   - `a-N`: Mark accepted for fix.
   - `r-N`: Mark rejected, record reason if given.
   - `e-N`: Expand with deeper evidence or context.
   - `all`: Accept all.

## Phase 6: Summary

1. Final summary:
   - Total findings by severity
   - Coverage gaps identified
   - Files reviewed vs. skipped (with reasons for skips)
2. Residual risk statement.
3. Recommended next action:
   - "Safe to commit" if no blockers/criticals remain
   - "Fix these N issues first" if blockers exist
   - "Consider splitting into smaller commits" if mixed-risk changes
4. Offer hand-off to `adk-address-review-feedback` for accepted findings.

## Validation Rules

- Review is grounded in the actual local diff (re-read if needed, never assume).
- Staged vs. unstaged distinction is maintained throughout.
- Findings are prioritized by severity.
- Testing gaps are explicitly flagged.
- Speculative findings carry confidence labels.
- Generated and vendored files are excluded from review.

## Edge Case Handling

| Situation | Action |
| --- | --- |
| No changes (clean working tree) | Report "nothing to review" and stop |
| Only untracked files | Note them, ask if they should be included |
| Merge conflicts | Stop, tell user to resolve first |
| Very large diff (>2000 lines) | Split by file risk groups, consider parallel subagents |
| Mixed staged/unstaged in same file | Review both, note the distinction in findings |
| Stash or WIP commits present | Note their existence, review only the requested scope |
| Binary files changed | Note them, skip code review, flag if security-relevant |
