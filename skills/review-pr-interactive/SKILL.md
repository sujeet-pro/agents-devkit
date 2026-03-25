---
name: review-pr-interactive
description: Use when you need an interactive GitHub or Bitbucket PR review loop that accepts, edits, rejects, and reconciles comments before posting
user_invocable: true
arguments:
  - name: pr
    description: "PR number or URL"
    required: true
  - name: tags
    description: "Optional guideline tags such as frontend, backend, design-system, library, scripts"
    required: false
  - name: confidence
    description: "Minimum confidence threshold (0-100, default: 80)"
    required: false
---

# Interactive PR Review

Use the shared contracts in `skills/_references/agentic-teams.md`, `skills/_references/review-pipeline.md`, `skills/_references/source-routing.md`, and `skills/_references/preflight-validations.md`.

This skill is review-only. Do not edit the branch in place. Post comments only after the interactive approval loop finishes.

## Preflight

Before any work, run:

`zsh scripts/check-skill-deps.zsh review-pr-interactive pr=<pr>`

Then confirm the source-native MCP (GitHub or Bitbucket) is connected with a lightweight read.

## Phase 1: Review

Run the standard `/devkit:review-pr` pipeline:

1. Detect source (GitHub or Bitbucket) from the PR URL or repository remote.
2. Read PR metadata, diff, commits, existing review comments, and thread state via MCP.
3. Reconcile existing comments before drafting anything new:
   - confirm which comments are already fixed
   - resolve handled but unresolved comments when the source supports it
   - re-open or restate critical comments that were marked outdated but are still valid
4. Load coding guidelines based on repo type.
5. Launch child agents in parallel:
   - `code-reviewer` for correctness, security, performance
   - `repo-auditor` for architecture and boundaries
   - `doc-reviewer` for docs, naming, reviewer ergonomics
   - domain specialist for frontend, backend, or design-system
6. Consolidate findings: deduplicate, assign severity and confidence scores.
7. Filter findings below the confidence threshold.

## Phase 2: Interactive Loop

Present each finding to the user one at a time in this format:

```text
## Finding [N/total] - [severity: critical|high|medium|low]

File: path/to/file.ext:LINE
Confidence: NN%

Issue
<description of the issue>

Suggested Comment
<the review comment text that would be posted>

Action: [A]ccept | [E]dit | [R]eject | [S]kip
```

### Actions

- Accept: queue the comment for posting as-is.
- Edit: let the user revise the comment before queuing it.
- Reject: discard the finding entirely.
- Skip: defer to the end. After all other findings are processed, return to skipped items for a final decision.

### Loop Rules

1. Process findings in severity order.
2. Reuse an existing thread when the accepted finding matches a live discussion.
3. Do not repost already-resolved feedback unless the issue is still present.
4. If the user says "accept all remaining", queue all unprocessed findings.
5. If the user says "reject all remaining", discard all unprocessed findings.

## Phase 3: Posting And Summary

After the loop finishes:

- post accepted comments through the matching MCP
- resolve handled comments that were confirmed fixed
- reopen or replace critical outdated comments that still apply

Then display:

```text
## Review Summary

Accepted: N
Edited: N
Rejected: N
Skipped: N
Resolved old threads: N
Reopened critical threads: N
```

## PR Status

After the user has accepted, rejected, or edited all comments, ask the user what review status to set on the PR:

- **Request Changes** — when accepted comments include critical or high-severity findings.
- **Approve** — when only minor findings remain or all issues were rejected/resolved.
- **Comment Only** — post comments without setting a formal review status.

Suggest a default based on the severity of accepted comments (e.g., if any accepted finding is critical or high, default to Request Changes; otherwise default to Approve). Let the user override the suggestion.

Use the source-native MCP to submit the review status:

- GitHub: `mcp__github__pull_request_review_write`
- Bitbucket: `mcp__bitbucket__approvePullRequest` or equivalent
