---
name: review-code-pr
description: Use when you need a non-mutating GitHub or Bitbucket pull request review with comment reconciliation, source-aware posting, and repo-type guidelines — handles fresh reviews, interactive review loops, and follow-up re-reviews in one skill
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
  - name: publish
    description: "Where to send the review: markdown, source, both (default: both)"
    required: false
  - name: mode
    description: "Review mode: auto, standard, interactive, followup (default: auto). Auto detects fresh vs re-review and uses interactive for fresh reviews."
    required: false
  - name: previous-review
    description: "Optional path to a previous review artifact for cross-referencing (used in followup mode)"
    required: false
  - name: focus
    description: "Review focus areas (comma-separated): security, performance, correctness, architecture, ui, all (default: all)"
    required: false
  - name: ui
    description: "Enable UI/visual review pass for frontend PRs (default: auto-detected)"
    required: false
---

# PR Review

Use the shared contracts in `skills/_references/agentic-teams.md`, `skills/_references/review-pipeline.md`, `skills/_references/source-routing.md`, `skills/_references/output-formats.md`, `skills/_references/preflight-validations.md`, and `skills/_references/review-comment-template.md`.

**All review comments posted to the PR must follow the canonical format in `skills/_references/review-comment-template.md`.** This applies to comments posted through the source MCP and to findings in the markdown review artifact.

This skill is review-only. Do not update the PR branch in place. Leave source comments or produce a markdown review artifact.

## Preflight

Before reading the PR or launching child agents, run:

`zsh scripts/check-skill-deps.zsh review-pr pr=<pr> publish=<publish>`

Then do one lightweight read through the matching source-native MCP to confirm the configured server is actually connected before deeper analysis.

## Source Handling

- Detect GitHub or Bitbucket from the PR URL or the repository remote.
- Use the source-native MCP:
  - GitHub -> `mcp__github__*`
  - Bitbucket -> `mcp__bitbucket__*`
- Read the PR metadata, diff, commits, existing review comments, thread status, and any prior resolutions before starting analysis.
- Keep the existing review interaction model: thread with or avoid duplicating current comments instead of posting a second disconnected review.

## Mode Detection

When `mode=auto` (the default):

1. After reading the PR metadata and existing review comments, check whether the current user has previously submitted a review on this PR.
2. If the current user has **no prior review comments** on this PR -> treat as a **fresh review** and use the **interactive** flow.
3. If the current user has **prior review comments** on this PR -> treat as a **follow-up review** and use the **followup** flow.

When `mode=standard`, `mode=interactive`, or `mode=followup`, skip auto-detection and use the specified flow directly.

## Large PR Handling

When the PR diff exceeds 500 changed lines:

1. Present a PR structure overview:
```text
## Large PR Detected - <N> files, <M> lines changed

Areas of change:
1. <area 1>: N files, M lines — <brief description>
2. <area 2>: N files, M lines — <brief description>
3. <area 3>: N files, M lines — <brief description>

Focus options:
[A]ll areas | [1-3] Specific areas | [C]ritical paths only | [S]ecurity focus
```

2. Use the user's selection to prioritize review depth — deeply review selected areas, surface-scan others.

## Comment Reconciliation

Before generating new findings, build a comment ledger with these buckets:

- open and still actionable
- handled in code but not resolved yet
- marked resolved or outdated
- ambiguous and needs re-verification

For each prior comment:

- re-review the latest diff or file state before assuming the issue is fixed
- if the issue is truly handled, avoid reposting it and resolve or acknowledge it when the source supports resolution
- if the issue was marked outdated or resolved but the risk is still present and critical, reopen the thread when the source supports it or post a replacement comment that references the unresolved risk
- if the issue is partially fixed, post only the remaining gap

## Guideline Loading

Always load:

- `skills/_references/guidelines/coding/general.md`
- `skills/_references/guidelines/coding/architecture.md`

Then add repo-type guidance:

- frontend -> `skills/_references/guidelines/coding/frontend-nextjs.md`
- design system -> `skills/_references/guidelines/coding/design-system.md`
- backend -> `skills/_references/guidelines/coding/backend-general.md` plus language-specific guidance when matched:
  - Java -> `skills/_references/guidelines/coding/backend-java.md`
  - Kotlin -> `skills/_references/guidelines/coding/backend-kotlin.md`
  - Node.js -> `skills/_references/guidelines/coding/backend-nodejs.md`
  - Python -> `skills/_references/guidelines/coding/backend-python.md`
- JS/TS library -> `skills/_references/guidelines/coding/js-ts-library.md`
- scripts or tooling -> `skills/_references/guidelines/coding/scripts.md`

Also load when the codebase or PR touches these areas:

- security-sensitive changes -> `skills/_references/guidelines/coding/security.md`
- test files or test configuration -> `skills/_references/guidelines/coding/testing.md`
- observability, logging, or monitoring -> `skills/_references/guidelines/coding/observability.md`
- API endpoints or contracts -> `skills/_references/guidelines/coding/api-design.md`

Also load repo-local coding guidance when present.

## Required Child Agents

Run at least these child agents in parallel:

- `code-reviewer` for correctness, security, performance, tests, and code patterns
- `repo-auditor` for architecture, dependency direction, and change isolation
- `doc-reviewer` for docs, migration notes, naming, and reviewer ergonomics
- one domain specialist pass for frontend, backend, or design-system concerns
- `source-publisher` after consolidation if `publish` includes source posting

## UI Review Pass

When `ui=true` or when the PR is auto-detected as frontend (touches `.tsx`, `.jsx`, `.vue`, `.svelte`, `.css`, `.scss` files):

Add a UI review child agent that checks:
- Visual consistency with existing patterns
- Accessibility (ARIA, keyboard nav, focus management)
- Responsive design (breakpoint coverage)
- Interaction states (empty, loading, error, disabled)
- Component API ergonomics

UI findings follow the same interactive loop and comment template as code review findings.

For full visual audit, suggest `/devkit:review-ui` as a dedicated adjacent skill.

## Review Requirements

Every review must cover:

- correctness and regressions
- security and performance
- architecture and boundary fit
- tests, docs, and migration impact
- code patterns and maintainability
- reconciliation of prior comments and thread state

When `focus` is specified, weight child agent priorities accordingly:
- `security` -> security reviewer gets extra depth, others surface-scan
- `performance` -> performance analysis prioritized
- `ui` -> UI review pass activated, visual patterns prioritized
- `correctness` -> correctness and regression analysis prioritized
- `architecture` -> boundary, coupling, and migration impact prioritized

---

## Standard Flow

Used when `mode=standard` or when auto-detection selects a fresh review without interactive.

1. Run the review pipeline: preflight, source handling, comment reconciliation, guideline loading, child agents.
2. Consolidate findings: deduplicate, assign severity and confidence scores.
3. Filter findings below the confidence threshold.
4. Post findings directly through the matching MCP (if `publish` includes source posting).
5. Produce the markdown review output.
6. Set PR status based on severity.

---

## Interactive Flow

Used when `mode=interactive` or when auto-detection selects a fresh review (the default for fresh reviews).

### Phase 1: Review

1. Run the full review pipeline: preflight, source handling, comment reconciliation, guideline loading, child agents.
2. Consolidate findings: deduplicate, assign severity and confidence scores.
3. Filter findings below the confidence threshold.

### Phase 2: Interactive Loop

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

#### Actions

- Accept: queue the comment for posting as-is.
- Edit: let the user revise the comment before queuing it.
- Reject: discard the finding entirely.
- Skip: defer to the end. After all other findings are processed, return to skipped items for a final decision.

#### Loop Rules

1. Process findings in severity order.
2. Reuse an existing thread when the accepted finding matches a live discussion.
3. Do not repost already-resolved feedback unless the issue is still present.
4. If the user says "accept all remaining", queue all unprocessed findings.
5. If the user says "reject all remaining", discard all unprocessed findings.

### Phase 3: Posting And Summary

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

### PR Status (Interactive)

After the user has accepted, rejected, or edited all comments, ask the user what review status to set on the PR:

- **Request Changes** — when accepted comments include critical or high-severity findings.
- **Approve** — when only minor findings remain or all issues were rejected/resolved.
- **Comment Only** — post comments without setting a formal review status.

Suggest a default based on the severity of accepted comments (e.g., if any accepted finding is critical or high, default to Request Changes; otherwise default to Approve). Let the user override the suggestion.

---

## Follow-Up Flow

Used when `mode=followup` or when auto-detection finds the current user has prior review comments on this PR.

### Phase 1: Build Previous Review Ledger

1. Read all existing review comments and their resolution state from the source MCP.
2. If `previous-review` is provided, also load that artifact and cross-reference its findings with the comment threads.
3. Build a ledger of every previous review comment with these fields:
   - comment ID and thread ID
   - original issue description
   - file and line reference
   - current resolution state (open, resolved, outdated)
   - author of the comment

### Phase 2: Re-Evaluate Each Comment

For each previous review comment in the ledger:

1. Read the current state of the referenced file and surrounding context.
2. Check the commits since the last review for changes to the referenced area.
3. Classify the comment into one of these buckets:
   - **Addressed**: the code change fixes the issue. Queue for resolution.
   - **Partially addressed**: the fix is incomplete or introduces a related gap. Draft a follow-up comment describing the remaining issue.
   - **Not addressed**: the code is unchanged or the issue persists. Keep the comment open.
   - **Resolved but not fixed**: the comment was marked resolved on the platform but the underlying issue is still present. Queue for reopening with explanation.
   - **Obsolete**: the surrounding code was refactored in a way that makes the comment no longer applicable. Queue for resolution.

### Phase 3: Scan for New Issues

Run the standard review pipeline on the new commits and changed files:

1. Load coding guidelines based on repo type.
2. Launch child agents in parallel:
   - `code-reviewer` for correctness, security, performance
   - `repo-auditor` for architecture and boundaries
   - `doc-reviewer` for docs, naming, reviewer ergonomics
   - domain specialist for frontend, backend, or design-system concerns
3. Consolidate findings: deduplicate against previous comments, assign severity and confidence scores.
4. Filter out issues that duplicate already-open threads.

### Phase 4: Interactive Summary

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

### Phase 5: Post and Resolve

After user confirmation:

1. **Addressed comments**: resolve the thread on the platform when supported. Post a brief acknowledgment reply (e.g., "Confirmed fixed in [commit-sha].").
2. **Partially addressed comments**: post a follow-up reply in the existing thread describing the remaining gap.
3. **Not addressed comments**: leave the thread open. Optionally post a gentle nudge if the user approves.
4. **Resolved but not fixed**: reopen the thread when the platform supports it, or post a new comment referencing the original thread and explaining why the issue persists.
5. **Obsolete comments**: resolve the thread with a note that the surrounding code was refactored.
6. **New issues**: post as new review comments through the matching MCP.

### Phase 6: Set PR Status (Follow-Up)

Based on the final state:

- If any comments remain in "not addressed" or "partially addressed" with severity >= high, set the review status to **Request Changes**.
- If all previous comments are addressed and no new critical or high-severity issues exist, set the review status to **Approved**.
- Otherwise, set to **Comment** and let the author decide.

---

## PR Status (General)

Use the source-native MCP to submit the review status:

- GitHub: `mcp__github__pull_request_review_write`
- Bitbucket: `mcp__bitbucket__approvePullRequest` or equivalent

If the review is comment-only (no source posting), skip status setting and note it in the output.

Before setting the status, show the user the intended status and the reasoning.

## Output

Always produce a markdown review with:

- severity-ordered findings
- confidence scores
- open questions and assumptions
- summary of what was posted back to the PR
- comment reconciliation summary covering carried-forward, resolved, reopened, and skipped threads

Display a final summary:

```text
## Review Complete

PR Status: [Approved | Request Changes | Comment]
Mode: [standard | interactive | followup (auto-detected)]

Resolved threads: N
Reopened threads: N
New comments posted: N
Threads left open: N
```

## Adjacent Skills

- `/devkit:review-ui` for standalone 6-pillar visual audit
- `/devkit:cross-review` for multi-model peer review
