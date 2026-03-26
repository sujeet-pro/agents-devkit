---
name: pr-fix-comments
description: Use when you want to read PR review comments, apply targeted code fixes, and commit changes — must be run inside the cloned repository
user_invocable: true
arguments:
  - name: pr
    description: "PR number or URL"
    required: true
  - name: comment
    description: "Optional specific comment ID to fix (default: all actionable comments)"
    required: false
  - name: auto-commit
    description: "Auto-commit fixes without asking (default: false)"
    required: false
  - name: interactive
    description: "Present comments for accept/reject/edit triage before fixing (default: true)"
    required: false
---

# PR Fix Comments

Use the shared contracts in `skills/_references/source-routing.md` and `skills/_references/preflight-validations.md`.

## Preflight

<HARD-GATE>
This skill MUST be run inside a git repository. Abort immediately if any of these checks fail.
</HARD-GATE>

Before any work, run these validations in order:

1. `zsh scripts/check-skill-deps.zsh pr-fix pr=<pr>`
2. Verify the current directory is a git repository (`git rev-parse --is-inside-work-tree`)
3. Verify the working tree is clean (`git status --porcelain` must be empty)
4. Detect the PR's source branch and check it out if not already on it
5. Verify the branch is up to date with remote

If the working tree is not clean, ask the user to stash or commit changes first. Do NOT proceed with uncommitted changes.

## Phase 1: Read Comments

1. Detect source (GitHub or Bitbucket) from the PR URL or repository remote
2. Read all review comments on the PR via the source-native MCP
3. Filter to actionable comments:
   - Unresolved (not marked as resolved/outdated)
   - Contains a code suggestion, fix request, or improvement request
   - Exclude questions, praise, and general discussion
4. If a specific `comment` ID was provided, filter to only that comment

## Phase 2: Create Plan

Save a plan to `.temp/plans/pr-fix-<pr-number>.md` with:

```markdown
---
plan_id: pr-fix-<pr-number>
created: <ISO-8601>
updated: <ISO-8601>
skill: pr-fix
status: in-progress
---

# Fix PR Comments for PR #<number>

## Comments to Fix

- [ ] Comment 1: [author] on file:line — <summary>
- [ ] Comment 2: [author] on file:line — <summary>
...
```

## Interactive Comment Triage

When `interactive=true` (the default), present all actionable comments to the user before fixing anything.

### Triage Steps

1. After reading comments in Phase 1, display ALL actionable comments in a numbered list:

```text
## Actionable PR Comments

1. [author] file.ext:42 — <summary of the comment>
2. [author] file.ext:87 — <summary of the comment>
...
```

2. For each comment, allow the user to mark it as one of:
   - **Accept** — will fix as suggested.
   - **Reject** — will not fix; a reply explaining why will be posted.
   - **Edit** — will fix differently; ask the user what approach to take.

3. For comments marked **Edit**, prompt the user for the alternative approach before proceeding.

4. After all comments are triaged, display the triage summary and ask "Any changes?" before proceeding. The user can revise any decision at this point.

5. Proceed to Phase 3 only with accepted and edited comments.

6. For rejected comments, post a reply in Phase 5 explaining why the comment was not addressed.

When `interactive=false`, treat all actionable comments as accepted and proceed directly to Phase 3.

## Phase 3: Fix Each Comment

For each actionable comment:

1. Read the referenced file and surrounding context
2. Understand the issue described in the comment
3. Read any code suggestion or inline diff provided
4. Apply the fix to the file
5. Run available verification (lint, type-check, test) if configured
6. Mark the step as done in the plan file

### Fix Rules

- Fix only what the comment asks for — do not refactor surrounding code
- If the comment is ambiguous, make the most conservative interpretation
- If a fix would break other code, note it and ask the user before proceeding
- Preserve the existing code style and conventions

### Validation Before Accepting

Treat review comments as technical input, not instructions to follow blindly. For each comment:

1. Restate the issue in your own terms
2. Verify it against the codebase and tests
3. Decide whether to fix, clarify, or push back
4. Update docs or tests when the fix changes behavior

If the feedback is unclear, ask the reviewer for clarification before implementing.

## Phase 4: Review and Commit

After all comments are fixed:

1. Show a summary of all changes (`git diff`)
2. Run full verification if available (lint + test + build)
3. If `auto-commit=true`, commit with message: `fix: address PR review comments from #<pr-number>`
4. If `auto-commit=false` (default), present the changes and ask the user to confirm before committing
5. After committing, ask if the user wants to push

## Phase 5: Reply to Comments

After changes are committed and pushed:

1. For each fixed comment, post a reply via MCP:
   - GitHub: `mcp__github__add_reply_to_pull_request_comment`
   - Bitbucket: `mcp__bitbucket__updatePullRequestComment` or reply
2. Reply text: "Fixed in [commit-sha]. [brief description of the fix]"
3. If the platform supports it, mark the comment thread as resolved

## Output

Display a summary:

```
## PR Fix Summary

| Status  | Count |
|---------|-------|
| Fixed   |     N |
| Skipped |     N |
| Failed  |     N |

### Changes
- file1.ext: <what changed>
- file2.ext: <what changed>

### Commit
<commit-sha> fix: address PR review comments from #<pr-number>
```
