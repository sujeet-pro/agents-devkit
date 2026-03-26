---
name: write-changelog
description: Use when you need to draft or directly revise a professional changelog from git history with categorization, release formatting, and clear breaking-change summaries
user_invocable: true
arguments:
  - name: since
    description: "Starting point: a git tag, commit SHA, or date (e.g., 'v1.2.0', 'abc1234', '2024-01-01')"
    required: true
  - name: format
    description: "Output format: markdown, github-release, confluence (default: markdown)"
    required: false
---

# Changelog

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should draft or improve the changelog directly. If you only want a comment-only review, use `/devkit:review-doc`.

## Preflight

Before reading git history or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-changelog`

Verify that the repository is a git repository and that the `since` reference resolves to a valid git object.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/changelog.md`

## Required Child Agents

Run at least these child agents in parallel:

- **Commit analyzer**: reads `git log` from `since` to HEAD. For each commit, extracts the type (feat, fix, refactor, docs, test, chore, perf, build, ci), scope, subject, body, breaking change markers, referenced issues or PRs, and author. Produces a structured list of parsed commits.
- **Categorizer**: groups the parsed commits into user-facing categories: Features, Bug Fixes, Breaking Changes, Performance Improvements, Documentation, Refactoring, and Other. Merges related commits. Identifies which changes are user-facing vs internal-only. Produces a categorized change list.
- **Writer**: takes the categorized list and produces a polished changelog. Writes concise, user-facing summaries for each entry. Formats breaking changes with migration instructions. Links to PRs and issues where available. Applies the requested output format.

## Workflow

1. **Read git history.** Extract commits from `since` to HEAD with full metadata.
2. **Launch child agents.** Run commit analyzer, categorizer, and writer in parallel.
3. **Merge outputs.** Combine the categorized and formatted results.
4. **Format for output.** Apply the requested format:
   - **markdown**: standard Keep a Changelog format with `## [version] - date` sections
   - **github-release**: GitHub release body format with categories and links
   - **confluence**: Confluence-friendly markdown with tables for breaking changes
5. **Review.** Check that all breaking changes are flagged, entries are user-readable, and links resolve.

## Output

A professional changelog containing:

- **Version header** with date
- **Breaking Changes** section (always first when present, with migration steps)
- **Features** section with concise descriptions
- **Bug Fixes** section with issue/PR references
- **Performance Improvements** section when applicable
- **Other Changes** section for internal improvements
- PR and issue links for traceability

## Final Step

Before delivering, review the changelog for missing breaking changes and ensure all entries are written as user-facing descriptions, not raw commit messages.

## Adjacent Skills

- `/devkit:write-blog` for release announcement blog posts
- `/devkit:pr-describe` for PR-level descriptions
- `/devkit:review-doc` for comment-only review of existing changelogs
