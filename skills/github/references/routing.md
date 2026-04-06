# GitHub Operation Routing

## PR Review Workflow

A full PR review follows this sequence:

1. **Get PR metadata** → `pr-operations.md` → `get-pr-details`
2. **Get the diff** → `pr-operations.md` → `get-pr-diff`
3. **Get changed files list** → `pr-operations.md` → `get-pr-files`
4. **Get file contents at branch HEAD** → `repo-operations.md` → `get-file-contents`
5. **Check for existing review comments** → `review-operations.md` → `list-review-comments` (idempotency)
6. **Post review with inline comments** → `review-operations.md` → `create-review`
7. **Check CI status** → `pr-operations.md` → `get-pr-checks`

## PR Management

| Task | Reference | Operations |
|------|-----------|------------|
| Describe a PR | `pr-operations.md` | `get-pr-details`, `get-pr-diff`, `update-pr` |
| Fix PR issues | `pr-operations.md` + `review-operations.md` | `get-pr-details`, `list-review-comments`, `get-pr-diff` |
| Finalize / merge | `pr-operations.md` | `get-pr-checks`, `merge-pr` |
| Create a PR | `pr-operations.md` | `create-pr` |

## Comment Operations

| Task | Reference | Operations |
|------|-----------|------------|
| List all comments | `review-operations.md` | `list-review-comments` |
| Post inline comment | `review-operations.md` | `create-review` or `create-standalone-comment` |
| Reply to a comment | `review-operations.md` | `reply-to-comment` |
| Resolve a thread | `review-operations.md` | `resolve-thread` |
| Check for duplicates | `review-operations.md` | See Idempotency section |

## Repository Access

| Task | Reference | Operations |
|------|-----------|------------|
| Read a file | `repo-operations.md` | `get-file-contents` |
| Read a file at a branch | `repo-operations.md` | `get-file-contents` (with `ref` param) |
| Search code | `repo-operations.md` | `search-code` |
| List branches | `repo-operations.md` | `list-branches` |
| Compare two branches | `repo-operations.md` | `compare-branches` |
| Get commit history | `repo-operations.md` | `list-commits` |
| Get single commit | `repo-operations.md` | `get-commit` |

## Issue Management

| Task | Reference | Operations |
|------|-----------|------------|
| View an issue | `issue-operations.md` | `get-issue` |
| Create an issue | `issue-operations.md` | `create-issue` |
| Update an issue | `issue-operations.md` | `update-issue` |
| Close an issue | `issue-operations.md` | `close-issue` |
| Comment on an issue | `issue-operations.md` | `add-comment` |
| Manage labels | `issue-operations.md` | `add-labels`, `remove-label` |
| Assign users | `issue-operations.md` | `assign` |
| List milestones | `issue-operations.md` | `list-milestones` |
