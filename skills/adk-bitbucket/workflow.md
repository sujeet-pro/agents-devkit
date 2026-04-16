# Bitbucket Operations Workflow

## Phase 1: Detect

**Goal**: Identify the action type and target workspace/repository.

1. Parse the user request to determine operation domain: PR, review, pipeline, repo
2. Resolve target from `--target`, git remote origin, or ask the user
3. Verify the Bitbucket MCP server is configured and responsive
4. **Gate**: Confirm the action type and target workspace/repo with the user (skip if `--auto`)

## Phase 2: Gather

**Goal**: Read current state from Bitbucket to inform the plan.

1. For PR operations: fetch existing PRs, branching model, default reviewers, check status
2. For review operations: fetch PR diff, diffstat, commits, existing comments and tasks
3. For pipeline operations: fetch recent runs, step details, log output
4. For repo operations: fetch repository metadata, branching model settings
5. Surface any conflicts or blockers discovered during gathering

## Phase 3: Plan

**Goal**: Propose the action with a preview before execution.

1. Construct the operation payload:
   - PR: title, description, source/destination branches, reviewers
   - Review: staged pending comments, tasks, approval/request-changes decision
   - Pipeline: target branch, pipeline selector
   - Repo: branching model changes, reviewer updates
2. Present a preview of what will be created, modified, or deleted
3. For non-destructive operations with `--auto`: proceed directly
4. **Gate — Destructive Operations**: the following always require explicit approval regardless of `--auto`:
   - **Merge**: confirm pipeline status, reviewer approvals, and merge strategy
   - **Decline**: confirm the PR and state the reason
   - **Stop-pipeline**: confirm the running step and impact of interruption
   - **Delete branch/repo**: enumerate open PRs and downstream impact
   - **Force-push**: list commits that will be rewritten and warn about shared-branch risk
   - **Branching model changes**: confirm the change and its effect on existing branches

## Phase 4: Execute

**Goal**: Perform the Bitbucket operation via MCP.

1. Execute via the appropriate Bitbucket MCP tool
2. For batch review: stage all comments as pending, then publish in one batch
3. Capture the response: PR URL, pipeline UUID, comment ID, or error
4. If the operation fails, report the error with context and remediation suggestions

## Phase 5: Verify

**Goal**: Confirm the operation succeeded and check for side effects.

1. Read back the affected resource to confirm state matches intent
2. For PR creation: verify PR is open, correct source/destination, reviewers assigned
3. For merge: verify PR state is MERGED, target branch updated
4. For pipeline trigger: verify run started, report initial status
5. Report the final result with direct links and remaining follow-ups

## Validation Rules

- Every MCP operation must produce a verifiable result (PR URL, pipeline UUID, comment ID)
- After mutating operations, read back the resource to confirm state
- If verification fails, state so explicitly and suggest manual confirmation
- Never claim success without MCP response confirmation
