# ADK Bitbucket Workflow

## Default Flow
1. run preflight to verify MCP server and CLI dependencies
2. detect the target workspace and repository from `--target` or git remote
3. confirm the requested action and any destructive consequences with the user
4. execute the operation via the appropriate Bitbucket MCP tool
5. validate the result by reading back the affected resource
6. report the outcome with links, status, and next steps

## PR Flow

### Create
1. detect the repository branching model to determine destination branch
2. fetch default reviewers
3. create the PR with `createPullRequest` or `createDraftPullRequest`
4. read back the created PR to confirm and report the URL

### Update
1. fetch the current PR state with `getPullRequest`
2. apply the requested changes with `updatePullRequest`
3. read back the updated PR to confirm

### Approve
1. fetch the PR state and pipeline statuses
2. confirm all pipeline checks pass
3. approve with `approvePullRequest`
4. read back the PR to confirm approval is recorded

### Merge
1. fetch the PR state, approvals, and pipeline statuses
2. confirm with the user that merge is intended
3. merge with `mergePullRequest`
4. read back the PR state to confirm it is merged

### Decline
1. fetch the PR state
2. confirm with the user that decline is intended
3. decline with `declinePullRequest`
4. read back the PR state to confirm it is declined

## Review Flow
1. read the diff with `getPullRequestDiff`
2. read the diff stat with `getPullRequestDiffStat` for a file-level summary
3. read commit history with `getPullRequestCommits` for context
4. stage comments with `addPendingPullRequestComment` for each finding
5. create tasks with `createPullRequestTask` for actionable items
6. publish all pending comments with `publishPendingComments`
7. approve or request changes depending on findings

## Pipeline Flow

### Trigger
1. confirm branch or tag target with the user
2. trigger with `runPipeline`
3. read back the pipeline run to confirm it started

### Monitor
1. list recent runs with `listPipelineRuns`
2. get details of the target run with `getPipelineRun`
3. list steps with `getPipelineSteps`
4. read logs from failing or relevant steps with `getPipelineStepLogs`
5. report status and any failures

### Stop
1. confirm with the user that stopping is intended
2. stop with `stopPipeline`
3. read back the pipeline run to confirm it is stopped

## Repository Flow
1. list or get repository details as requested
2. fetch default reviewers or branching model as needed
3. for branching model updates, confirm changes with the user before applying
4. read back the updated settings to confirm

## Validation Rules
- every state-changing MCP operation must be followed by a read-back of the affected resource
- if the read-back does not confirm the expected state, report the discrepancy
- if validation cannot be performed, say so explicitly
- do not claim an operation succeeded without confirming via API response
