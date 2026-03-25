---
name: review-pr-followup
description: Use when you need to re-review a PR after the author has updated it based on previous review comments, checking which issues are addressed and which remain
user_invocable: true
arguments:
  - name: pr
    description: "PR number or URL"
    required: true
  - name: previous-review
    description: "Optional path to a previous review artifact for cross-referencing"
    required: false
---

# PR Follow-Up Review

Use the shared contracts in `skills/_references/agentic-teams.md`, `skills/_references/review-pipeline.md`, `skills/_references/source-routing.md`, and `skills/_references/preflight-validations.md`.

This skill is review-only. Do not edit the branch in place. Post comments only after the interactive approval loop finishes.

## Preflight

Before any work, run:

`zsh scripts/check-skill-deps.zsh review-pr-followup pr=<pr>`

Then confirm the source-native MCP (GitHub or Bitbucket) is connected with a lightweight read.

## Source Handling

- Detect GitHub or Bitbucket from the PR URL or the repository remote.
- Use the source-native MCP:
  - GitHub -> `mcp__github__*`
  - Bitbucket -> `mcp__bitbucket__*`
- Read the PR metadata, current diff, commits since the last review, existing review comments, thread status, and any prior resolutions.

## Phase 1: Build Previous Review Ledger

1. Read all existing review comments and their resolution state from the source MCP.
2. If `previous-review` is provided, also load that artifact and cross-reference its findings with the comment threads.
3. Build a ledger of every previous review comment with these fields:
   - comment ID and thread ID
   - original issue description
   - file and line reference
   - current resolution state (open, resolved, outdated)
   - author of the comment

## Phase 2: Re-Evaluate Each Comment

For each previous review comment in the ledger:

1. Read the current state of the referenced file and surrounding context.
2. Check the commits since the last review for changes to the referenced area.
3. Classify the comment into one of these buckets:
   - **Addressed**: the code change fixes the issue. Queue for resolution.
   - **Partially addressed**: the fix is incomplete or introduces a related gap. Draft a follow-up comment describing the remaining issue.
   - **Not addressed**: the code is unchanged or the issue persists. Keep the comment open.
   - **Resolved but not fixed**: the comment was marked resolved on the platform but the underlying issue is still present. Queue for reopening with explanation.
   - **Obsolete**: the surrounding code was refactored in a way that makes the comment no longer applicable. Queue for resolution.

## Phase 3: Scan for New Issues

Run the standard review pipeline on the new commits and changed files:

1. Load coding guidelines based on repo type (same as `/devkit:review-pr`).
2. Launch child agents in parallel:
   - `code-reviewer` for correctness, security, performance
   - `repo-auditor` for architecture and boundaries
   - `doc-reviewer` for docs, naming, reviewer ergonomics
   - domain specialist for frontend, backend, or design-system concerns
3. Consolidate findings: deduplicate against previous comments, assign severity and confidence scores.
4. Filter out issues that duplicate already-open threads.

## Phase 4: Interactive Summary

Present the full follow-up summary to the user before posting anything:

```text
## Follow-Up Review Summary

### Previous Comments
| Status              | Count |
|---------------------|-------|
| Addressed           |     N |
| Partially addressed |     N |
| Not addressed       |     N |
| Resolved but unfixed|     N |
| Obsolete            |     N |

### New Issues Found: N

[List each new issue with severity, file, and description]
```

Ask the user to confirm before proceeding to post. Allow the user to:

- Override any classification (e.g., mark something as addressed that was classified as not addressed).
- Edit any follow-up comment text before posting.
- Skip posting for specific items.

## Phase 5: Post and Resolve

After user confirmation:

1. **Addressed comments**: resolve the thread on the platform when supported. Post a brief acknowledgment reply (e.g., "Confirmed fixed in [commit-sha].").
2. **Partially addressed comments**: post a follow-up reply in the existing thread describing the remaining gap.
3. **Not addressed comments**: leave the thread open. Optionally post a gentle nudge if the user approves.
4. **Resolved but not fixed**: reopen the thread when the platform supports it, or post a new comment referencing the original thread and explaining why the issue persists.
5. **Obsolete comments**: resolve the thread with a note that the surrounding code was refactored.
6. **New issues**: post as new review comments through the matching MCP.

## Phase 6: Set PR Status

Based on the final state:

- If any comments remain in "not addressed" or "partially addressed" with severity >= high, set the review status to **Request Changes**.
- If all previous comments are addressed and no new critical or high-severity issues exist, set the review status to **Approved**.
- Otherwise, set to **Comment** and let the author decide.

## Output

Display a final summary:

```text
## Follow-Up Review Complete

PR Status: [Approved | Request Changes | Comment]

Resolved threads: N
Reopened threads: N
New comments posted: N
Threads left open: N
```
