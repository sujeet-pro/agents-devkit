# Local Review Stage

Review local changes (staged, unstaged, or all commits since the branch diverged from the base) and produce a review document. This stage does not mutate the source.

**Core principle:** Review early, review often.

---

## Source Detection

Detect the scope of local changes:

1. **Staged changes**: `git diff --cached`
2. **Unstaged changes**: `git diff`
3. **All branch changes**: `git diff <base>...HEAD`
4. **Recent commits**: `git log --oneline <base>..HEAD`

If both staged and unstaged changes exist, review both. If the user specifies a scope, use that.

### Get git SHAs

```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

### Get Changed Files

```bash
# Staged
git diff --cached --name-only

# Unstaged
git diff --name-only

# All branch changes
git diff --name-only <base>...HEAD
```

---

## Guideline Loading

Invoke the `coding` skill to detect repo frameworks and load matching coding guidelines. Pass the list of changed files (from `git diff` or `git diff <base>...HEAD`) for scoped detection.

---

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

---

## Review Execution

### Step 1: Dispatch Review Dimension Agents

Run these review dimensions in parallel:

**Always run:**
1. **`syntax`** — linting gaps, formatting, naming, import organization, dead code
2. **`correctness`** — logic bugs, edge cases, null handling, boundary conditions, race conditions
3. **`security`** — OWASP Top 10, auth/authz, input validation, secret exposure, injection
4. **`performance`** — N+1 queries, memory leaks, bundle size, caching, complexity
5. **`design`** — coupling, dependency direction, data flow, API surface, change isolation
6. **`reliability`** — error handling, retries, timeouts, observability, logging
7. **`testing`** — coverage gaps, test quality, missing edge case tests, flaky patterns
8. **`documentation`** — doc drift, migration notes, API docs, changelog

**Conditional:**
9. **`ui-ux`** — when changes touch frontend files (`.tsx`, `.jsx`, `.vue`, `.svelte`, `.css`, `.scss`)
10. **`spec-compliance`** — when context documents are available

**Placeholders for code-reviewer:**
- `{WHAT_WAS_IMPLEMENTED}` - What was built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{BASE_SHA}` - Starting commit
- `{HEAD_SHA}` - Ending commit
- `{DESCRIPTION}` - Brief summary

### Step 2: Dual Review

**Approach 1: Diff Review**

Review the raw diff for exact line changes, files added/removed/renamed, and diff-visible issues.

**Approach 2: Full File Review**

For each changed file, read the full file to catch issues in surrounding code, missing imports, broken invariants, and existing patterns.

### Step 3: Consolidate

- Deduplicate overlapping findings
- Assign severity (Must Fix, Suggestion, Note) and confidence scores
- Attribute each finding to its review dimension(s)
- Tag with Concern domain and Review Depth
- Separate must-fix issues from suggestions

---

## Auto-Validation

Verify each finding against the actual code before presenting:

1. File existence check
2. Line accuracy check
3. Code state verification
4. Suggested fix applicability
5. Duplicate/stale check

Discard findings where the issue does not actually exist in the current code.

---

## Acting on Feedback

- Fix Must Fix issues immediately
- Fix Suggestion issues before proceeding
- Note issues for later
- Push back if reviewer is wrong (with reasoning)

---

## Integration with Workflows

**Subagent-Driven Development:**
- Review after EACH task
- Catch issues before they compound
- Fix before moving to next task

**Executing Plans:**
- Review after each batch (3 tasks)
- Get feedback, apply, continue

**Ad-Hoc Development:**
- Review before merge
- Review when stuck

---

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Must Fix issues
- Proceed with unfixed Suggestion issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

---

## Output

Produce a markdown review document:

```text
## Local Review: <branch-name>

### Scope
- Staged changes: N files
- Unstaged changes: N files
- Branch commits: N since <base>

### Findings (severity order)

[findings using canonical comment template format]

### Open Questions
[items needing clarification]

### Action Items
- [ ] Must Fix: ...
- [ ] Suggestion: ...
- [ ] Note: ...
```

Display a final summary:

```text
## Local Review Complete

- **Scope:** [staged | unstaged | branch changes]
- **Files reviewed:** N
- **Findings:** N (must fix: N, suggestion: N, note: N)
- **Dimensions:** N active
- **Auto-validation:** N kept / M discarded
- **Output:** Markdown review presented
```
