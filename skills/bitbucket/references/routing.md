# Bitbucket Routing

Route map from use cases to the correct reference file, script, and action.

## PR Review Workflow

Typical review flow — execute steps in order:

| Step | Action | Script | Command |
|------|--------|--------|---------|
| 1. Get PR metadata | Fetch PR details (title, author, branches, status) | `scripts/pr.sh` | `pr.sh get <ws> <repo> <pr-id>` |
| 2. Get diff | Fetch the full text diff | `scripts/pr.sh` | `pr.sh diff <ws> <repo> <pr-id>` |
| 3. Get diffstat | Fetch file-level change summary | `scripts/pr.sh` | `pr.sh diffstat <ws> <repo> <pr-id>` |
| 4. Get commits | List commits in the PR | `scripts/pr.sh` | `pr.sh commits <ws> <repo> <pr-id>` |
| 5. Check statuses | Pipeline/build status | `scripts/pr.sh` | `pr.sh statuses <ws> <repo> <pr-id>` |
| 6. Read existing comments | Avoid duplicate comments | `scripts/comments.sh` | `comments.sh list <ws> <repo> <pr-id>` |
| 7. Post review comments | Inline or general comments | `scripts/comments.sh` | `comments.sh create <ws> <repo> <pr-id> --body "..." [--file path --line N]` |
| 8. Approve / request changes | Approve the PR | `scripts/pr.sh` | `pr.sh approve <ws> <repo> <pr-id>` |

**Reference**: `references/pr-operations.md`, `references/comment-operations.md`

## PR Management

| Use Case | Script | Action | Key Args |
|----------|--------|--------|----------|
| List open PRs | `scripts/pr.sh` | `list` | `--state OPEN` (default) |
| List merged PRs | `scripts/pr.sh` | `list` | `--state MERGED` |
| Create a PR | `scripts/pr.sh` | `create` | `--title "..." --source-branch feature --dest-branch main` |
| Update PR title/description | `scripts/pr.sh` | `update` | `--title "..." --description "..."` |
| Merge a PR | `scripts/pr.sh` | `merge` | `--strategy squash --close-source true` |
| Decline a PR | `scripts/pr.sh` | `decline` | — |
| Approve a PR | `scripts/pr.sh` | `approve` | — |
| Remove approval | `scripts/pr.sh` | `unapprove` | — |
| View activity feed | `scripts/pr.sh` | `activity` | — |

**Reference**: `references/pr-operations.md`

## Comment Operations

| Use Case | Script | Action | Key Args |
|----------|--------|--------|----------|
| List all comments | `scripts/comments.sh` | `list` | — |
| Get single comment | `scripts/comments.sh` | `get` | `--comment-id N` |
| Post general comment | `scripts/comments.sh` | `create` | `--body "..."` |
| Post inline comment | `scripts/comments.sh` | `create` | `--body "..." --file path --line N` |
| Reply to a comment | `scripts/comments.sh` | `reply` | `--parent-id N --body "..."` |
| Update a comment | `scripts/comments.sh` | `update` | `--comment-id N --body "..."` |
| Delete a comment | `scripts/comments.sh` | `delete` | `--comment-id N` |
| List tasks | `scripts/comments.sh` | `list-tasks` | — |
| Create a task | `scripts/comments.sh` | `create-task` | `--body "..." --comment-id N` |
| Resolve/reopen a task | `scripts/comments.sh` | `resolve-task` | `--task-id N --state RESOLVED` |

**Reference**: `references/comment-operations.md`

## Repository Access

| Use Case | Script | Action | Key Args |
|----------|--------|--------|----------|
| Get repo info | `scripts/repo.sh` | `get` | — |
| Read file contents | `scripts/repo.sh` | `file` | `--path src/main.py --ref main` |
| List branches | `scripts/repo.sh` | `branches` | — |
| List commits | `scripts/repo.sh` | `commits` | `--branch main` |
| Compare branches | `scripts/repo.sh` | `diff` | `--spec main..feature` |

**Reference**: `references/repo-operations.md`
