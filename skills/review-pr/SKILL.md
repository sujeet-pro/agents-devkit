---
name: review-pr
description: Use when you need a non-mutating GitHub or Bitbucket pull request review with comment reconciliation, source-aware posting, and repo-type guidelines
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
---

# PR Review

Use the shared contracts in `skills/_references/agentic-teams.md`, `skills/_references/review-pipeline.md`, `skills/_references/source-routing.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

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

## Review Requirements

Every review must cover:

- correctness and regressions
- security and performance
- architecture and boundary fit
- tests, docs, and migration impact
- code patterns and maintainability
- reconciliation of prior comments and thread state

## Output

Always produce a markdown review with:

- severity-ordered findings
- confidence scores
- open questions and assumptions
- summary of what was posted back to the PR
- comment reconciliation summary covering carried-forward, resolved, reopened, and skipped threads

If `publish` includes source posting, convert the consolidated findings into GitHub or Bitbucket review comments through the matching MCP.

## PR Status

After posting review comments, set the PR review status based on the severity of findings:

- If any **Critical** or **Important** (high-severity) issues were found -> **Request Changes**
- If only **Minor** issues or no issues were found -> **Approve**

Before setting the status, show the user the intended status and the reasoning (e.g., "Setting status to Request Changes because 2 critical findings remain"). Use the source-native MCP to submit the review:

- GitHub: `mcp__github__pull_request_review_write`
- Bitbucket: `mcp__bitbucket__approvePullRequest` or equivalent

If the review is comment-only (no source posting), skip status setting and note it in the output.
