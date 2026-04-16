# GitHub Operations Workflow

## Phase 1: Detect

**Goal**: Identify the action type and target repository.

1. Parse the user request to determine operation domain: PR, issue, release, search, repo
2. Resolve target repository from `--target`, git remote origin, or ask the user
3. Detect whether the GitHub MCP server is available; fall back to gh CLI if not
4. **Gate**: Confirm the action type and target repository with the user (skip if `--auto`)

## Phase 2: Gather

**Goal**: Read current state from GitHub to inform the plan.

1. For PR operations: fetch existing PRs, branch state, check status, reviewers
2. For issue operations: fetch existing issues, labels, milestones
3. For release operations: fetch existing releases and tags
4. For repo operations: fetch repository metadata, branches, collaborators
5. Surface any conflicts or blockers discovered during gathering

## Phase 3: Plan

**Goal**: Propose the action with a preview before execution.

1. Construct the operation payload (title, body, labels, reviewers, merge strategy)
2. Present a preview of what will be created, modified, or deleted
3. For non-destructive operations with `--auto`: proceed directly
4. **Gate — Destructive Operations**: the following always require explicit approval regardless of `--auto`:
   - **Merge**: confirm CI status, reviewer approvals, and merge strategy
   - **Close/Decline**: confirm the resource and reason
   - **Delete**: enumerate downstream impact (branch protections, open PRs, release assets)
   - **Force-push**: confirm target branch, list commits that will be rewritten, and warn about shared-branch risk

## Phase 4: Execute

**Goal**: Perform the GitHub operation.

1. Execute via MCP tools when available, gh CLI otherwise
2. Capture the response: URL, ID, SHA, or error
3. If the operation fails, report the error with context and remediation suggestions
4. For batch operations, execute sequentially and report progress

## Phase 5: Verify

**Goal**: Confirm the operation succeeded and check for side effects.

1. Read back the affected resource to confirm state matches intent
2. For PR creation: verify PR is open, correct base/head, reviewers assigned
3. For merge: verify target branch updated, no pipeline failures
4. For issue operations: verify state change, labels applied
5. Report the final result with direct links and any remaining follow-ups

## Validation Rules

- Every mutating operation must produce a confirmable artifact (URL, ID, SHA)
- Read operations must return non-empty data or explicit "not found"
- If verification fails, state so explicitly and suggest manual confirmation
- Never claim success without API confirmation
