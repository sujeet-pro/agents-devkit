# DevKit Review Pipeline

All review-oriented skills follow this pipeline.

## 1. Intake

- Run the skill preflight first so tool dependencies and source-native MCP configuration are verified from the actual input.
- Detect the source type: GitHub PR, Bitbucket PR, local repository, local markdown, Confluence page, Google Doc, or mixed input.
- Detect whether the requested output is markdown only, source comments, source updates, or both.
- Detect whether the active skill is `review-*` or `write-*`. `review-*` skills do not mutate the source; `write-*` skills do.
- Load repo and source-specific guidelines before analysis.

## 2. Source Ingestion

- Pull the primary material first:
  - PR metadata, diff, commits, and existing comments
  - document body, attachments, images, diagrams, and comments
  - relevant source files from the local checkout
- Build a comment ledger when the source already has comments or threads:
  - still-open issues
  - handled but unresolved issues
  - resolved or outdated issues that need verification
  - critical issues that may need to be reopened
- Build a compact context packet for the review team: summary, scope, guidelines, changed files, and existing discussion.

## 3. Parallel Review

Launch a review team from `skills/_references/agentic-teams.md`.

Every review must cover:

- correctness and behavioral risk
- architecture and boundary fit
- security and performance
- tests, docs, and migration impact
- source-specific concerns such as frontend, backend, design system, or document quality

## 4. Consolidation

- Deduplicate overlapping findings.
- Attach file paths, line numbers, or quoted text when available.
- Assign a confidence score and a concrete next step.
- Separate must-fix issues from suggestions.
- Reconcile new findings against the comment ledger before preparing postback actions.

## 5. Output

Always produce a markdown review artifact with:

- summary
- findings grouped by severity
- open questions and assumptions
- follow-up checklist

Optional source-side output:

- PR comments on GitHub or Bitbucket
- Confluence comments or page updates
- Google Docs comments or document updates

## 6. Postback Rules

- Reuse or align with existing review interaction when the source already has a live review thread.
- Avoid posting duplicate comments that already exist.
- Resolve comments that are truly handled but still left open when the source supports it.
- Reopen or restate critical comments that were marked outdated or resolved incorrectly and are still valid.
- Prefer line comments when the source supports them and the line mapping is stable.
- Fall back to a grouped summary comment when exact line mapping is not possible.
