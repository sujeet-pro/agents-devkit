# PR Finalize Stage

Guide completion of the development branch after the PR is approved and ready. Also handles draft status management.

---

## Draft Status Management

When `--action status` is used, or as part of finalization assessment.

### Check Current Status

Read the PR metadata to determine:
- Is the PR currently a draft (GitHub draft PR)?
- Does the title have a "Draft:" or "WIP:" prefix?
- Are there unresolved review comments?
- Is CI passing?

### Draft Assessment

| Condition | Recommendation |
|-----------|---------------|
| All critical/high comments addressed, CI passing | Remove draft status, mark ready for review |
| Unresolved critical/high comments remain | Keep or set draft status |
| CI failing | Keep or set draft status |
| New significant changes pushed, no re-review yet | Keep draft until review requested |
| User explicitly wants to park the PR | Set draft |

### Operations

- **Set draft**: Add "Draft:" prefix to title. On GitHub, convert to draft PR via `convertPullRequestToDraft` mutation if available, otherwise just prefix the title.
- **Remove draft**: Remove "Draft:" or "WIP:" prefix from title. On GitHub, mark ready for review via `markPullRequestReadyForReview` mutation if available.

### Always Confirm

```text
## Draft Status

Current: <draft|ready>
Title: <current title>
Unresolved comments: N
CI: <passing|failing|pending>

Recommendation: <set draft | remove draft | keep current>
Reason: <explanation>

Proceed? [Y]es | [N]o | [C]ustom title
```

---

## Finalize Flow

### Step 1: Verify Tests

Run the project's test suite. If tests fail, stop and report. Do not proceed.

### Step 2: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main -- is that correct?"

### Step 3: Present Options

```text
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and update the Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

### Step 4: Execute Choice

**Option 1: Merge Locally**
- Switch to base branch, pull latest, merge feature branch, verify tests, delete feature branch.

**Option 2: Push and Update PR**
- Push branch, update PR description if stale (invoke the pr-describe stage), request re-review if needed.

**Option 3: Keep As-Is**
- Report branch and worktree location. Don't clean up.

**Option 4: Discard**
- Require typed "discard" confirmation. Delete branch. Clean up worktree if applicable.

### Step 5: Worktree Cleanup

For Options 1, 2, and 4: check if in a worktree and clean up.
For Option 3: keep worktree.

### Post-Merge Checklist

After successful merge or PR update:
- Delete remote branch (if merged)
- Update linked issues
- Note any follow-up items from the PR description

---

## Summary

```text
## PR Finalize Complete

PR: <owner>/<repo>#<number>
Action: <merge locally | push and update | keep | discard | draft status change>
Tests: <pass/fail>
Branch: <deleted | kept>
```
