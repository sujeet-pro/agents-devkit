# ADK GitHub Workflow

## Default Flow
1. **Run preflight** -- execute `scripts/preflight.py` to verify MCP server availability, gh CLI presence, and authentication status. Record which execution path is available (MCP, gh CLI, or both).
2. **Detect target repository** -- resolve the `owner/repo` from (in priority order): `--target` parameter, git remote origin URL, or ask the user. Parse both HTTPS (`https://github.com/owner/repo`) and SSH (`git@github.com:owner/repo.git`) remote formats.
3. **Confirm action scope** -- identify the operation domain (PR, issue, release, search, repo) from the task description or `--action` parameter. For destructive operations, state what will happen and wait for confirmation.
4. **Execute via MCP or gh CLI** -- use MCP tools (`mcp__github__*`) when the server is configured. Fall back to `gh` CLI commands when MCP is unavailable. Never mix both in a single operation chain -- pick one path and stay on it.
5. **Validate result** -- confirm the operation produced a verifiable artifact (URL, ID, SHA, or status). If the result is ambiguous, re-read the resource to verify.
6. **Report** -- output the action performed, target resource, result URL/ID, and any suggested next steps.

## PR Flow

### Create PR
1. Verify the current branch is not main/master. If it is, stop and warn.
2. Check that the branch has been pushed to the remote (`git rev-parse --abbrev-ref --symbolic-full-name @{u}`). If not pushed, push first.
3. Detect the default branch for the base (usually `main` or `master`).
4. Generate a diff summary: count of files changed, insertions, deletions.
5. If a PR template exists in the repo (`.github/PULL_REQUEST_TEMPLATE.md` or `.github/PULL_REQUEST_TEMPLATE/`), use it to structure the body.
6. Create the PR via `mcp__github__create_pull_request` or `gh pr create`.
7. Report the PR URL.

### List/Search PRs
1. Use `mcp__github__list_pull_requests` with pagination (batch of 10) or `gh pr list --limit 10`.
2. For targeted searches, use `mcp__github__search_pull_requests` or `gh search prs`.
3. Display: number, title, author, state, head branch, URL.

### Read PR
1. Fetch PR metadata via `mcp__github__pull_request_read` or `gh pr view <number>`.
2. Include: title, body, state, author, head/base branches, mergeable status, check status.
3. Fetch the diff when the user needs to see changes.

### Update PR
1. Use `mcp__github__update_pull_request` or `gh api` PATCH to update title, body, or state.
2. Confirm the update by re-reading the PR.

### Merge PR
1. Check that all required status checks have passed.
2. Check that the PR is mergeable (no conflicts).
3. Confirm the merge strategy with the user (merge, squash, rebase) -- default to squash.
4. Execute via `mcp__github__merge_pull_request` or `gh pr merge`.
5. Optionally delete the source branch after merge.
6. Report the merge commit SHA and final PR URL.

### Review PR
1. Create a pending review via `mcp__github__pull_request_review_write` (method: create).
2. Add line-level comments via `mcp__github__add_comment_to_pending_review`.
3. Submit the review via `mcp__github__pull_request_review_write` (method: submit_pending) with event: COMMENT, APPROVE, or REQUEST_CHANGES.
4. For gh CLI fallback, construct the review JSON and submit via `gh api`.

## Issue Flow

### Create Issue
1. Search for existing issues with similar titles to avoid duplicates.
2. If issue types are available for the organization, check `mcp__github__list_issue_types` first.
3. Create via `mcp__github__issue_write` or `gh issue create`.
4. Apply labels, assignees, and milestone if specified.
5. Report the issue URL.

### Search Issues
1. Use `mcp__github__search_issues` with query filters (state, label, assignee, keyword).
2. For simple listing, use `mcp__github__list_issues` with pagination.
3. Display: number, title, state, labels, assignee, URL.

### Comment on Issue
1. Use `mcp__github__add_issue_comment` or `gh issue comment`.
2. Confirm the comment was posted by checking the response.

### Close Issue
1. Confirm with the user before closing.
2. Set state_reason (completed or not_planned) when closing.
3. Use `mcp__github__issue_write` or `gh issue close`.
4. Optionally add a closing comment explaining why.

## Release Flow

### List Releases
1. Use `mcp__github__list_releases` with pagination.
2. Display: tag name, title, published date, draft/prerelease status.

### Get Release
1. Use `mcp__github__get_latest_release` for the most recent release.
2. Use `mcp__github__get_release_by_tag` for a specific version.
3. Display: tag, title, body (release notes), assets, published date.

## Search Flow

### Code Search
1. Use `mcp__github__search_code` with the query, optionally scoped to a repository.
2. Apply language and path filters when specified.
3. Display: file path, repository, matching lines.

### Repository Search
1. Use `mcp__github__search_repositories` or `gh search repos`.
2. Display: full name, description, stars, language, URL.

### User Search
1. Use `mcp__github__search_users` or `gh search users`.
2. Display: login, name, URL.

## Repository Operations Flow

### Branch Operations
1. List branches via `mcp__github__list_branches` or `gh api`.
2. Create a branch via `mcp__github__create_branch` from a specified base ref.
3. Report the branch name and head SHA.

### File Operations
1. Read file contents via `mcp__github__get_file_contents`.
2. Create or update files via `mcp__github__create_or_update_file` (requires the file's current SHA for updates).
3. Push multiple files via `mcp__github__push_files`.
4. Report the commit SHA after file modifications.

### Repository Creation
1. Create a new repo via `mcp__github__create_repository` or `gh repo create`.
2. Fork an existing repo via `mcp__github__fork_repository` or `gh repo fork`.
3. Report the new repository URL.

## Validation Rules
- Every mutating operation must produce a verifiable artifact: URL, numeric ID, or commit SHA.
- Read operations must return data or an explicit "not found" message.
- Before reporting success on a create/update, verify by re-reading the resource when the response is ambiguous.
- For batch operations (e.g., closing multiple issues), report each result individually.
- Never claim an operation succeeded without evidence from the API response.

## MCP vs gh CLI Decision
| Condition | Path |
| --- | --- |
| GitHub MCP server configured and responding | Use MCP tools exclusively |
| MCP not configured, gh CLI installed and authenticated | Use gh CLI exclusively |
| Both available | Prefer MCP; fall back to gh CLI only if MCP tool call fails |
| Neither available | Stop and provide setup instructions from preflight output |
