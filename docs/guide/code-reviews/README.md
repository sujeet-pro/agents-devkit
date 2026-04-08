---
title: Code Reviews
description: Review PRs, fix comments, self-review local changes, and audit entire repositories
order: 1
---

# Code Reviews

ADK provides a complete code review workflow — from reviewing someone else's PR to fixing review comments on your own. The `code-review` router auto-detects the right sub-skill, or you can invoke each one directly.

> **Quick start:** `/adk:code-review <PR URL or description>` — the router picks the right skill automatically.

## Scenarios

- [Review someone else's PR](#review-someone-elses-pr)
- [Self-review your own changes](#self-review-your-own-changes)
- [Generate a PR description](#generate-a-pr-description)
- [Fix PR review comments](#fix-pr-review-comments)
- [Review an entire repository](#review-an-entire-repository)
- [Multi-model cross-review](#multi-model-cross-review)
- [Finalize and merge a PR](#finalize-and-merge-a-pr)

---

## Review Someone Else's PR

Use `code-review-pr` with a PR URL. ADK fetches the diff, loads coding guidelines for the detected stack, and produces a structured review.

```text
/adk:code-review-pr https://github.com/org/repo/pull/42
```

### Focusing the review

By default, the review covers all dimensions (correctness, security, performance, maintainability). Use `--focus` to narrow:

```text
/adk:code-review-pr https://github.com/org/repo/pull/42 --focus security
/adk:code-review-pr https://github.com/org/repo/pull/42 --focus performance
```

### Publishing comments to the PR

Add `--publish` to post review comments directly on the PR (requires GitHub or Bitbucket MCP):

```text
/adk:code-review-pr https://github.com/org/repo/pull/42 --publish
```

### Interactive review mode

Use `--mode interactive` for a guided review where you can accept, reject, or edit each finding:

```text
/adk:code-review-pr https://github.com/org/repo/pull/42 --mode interactive
```

### Diff-only remote review

When you don't have the repo cloned locally, use `--skip-repo` to review only the PR diff:

```text
/adk:code-review-pr https://github.com/org/repo/pull/42 --skip-repo
```

### Bitbucket PRs

Works identically with Bitbucket URLs (requires Bitbucket MCP):

```text
/adk:code-review-pr https://bitbucket.org/workspace/repo/pull-requests/42
```

---

## Self-Review Your Own Changes

Review local uncommitted changes or a branch diff before creating a PR.

### Review unstaged/staged changes

```text
/adk:code-review-pr
```

When invoked without a URL, `code-review-pr` reviews your local changes (staged + unstaged).

### Review a branch

```text
/adk:code-review-pr --branch feature/auth
```

Reviews the diff between the current branch and the base branch.

### Auto-fix issues found

Combine review with automatic fixes for any issues found:

```text
/adk:code-review-pr --fix
```

---

## Generate a PR Description

Auto-generate a PR title and description from your changes:

```text
/adk:code-review-pr --action describe
```

This analyzes the diff, summarizes the changes, and generates a structured PR description. Pair with `--publish` to push the description directly to the PR.

```text
/adk:code-review-pr https://github.com/org/repo/pull/42 --action describe --publish
```

---

## Fix PR Review Comments

When reviewers leave comments on your PR, use `code-review-fix` to read, categorize, and fix them:

```text
/adk:code-review-fix https://github.com/org/repo/pull/42
```

This will:

1. Fetch all unresolved review comments
2. Categorize by severity (blocker, critical, suggestion)
3. Present a fix plan for approval
4. Apply code changes, reply to reviewers, and resolve threads

### Filter by severity

Only address blockers and critical issues:

```text
/adk:code-review-fix https://github.com/org/repo/pull/42 --filter blocker
/adk:code-review-fix https://github.com/org/repo/pull/42 --filter critical
```

### Dry run

See what would be fixed without making changes:

```text
/adk:code-review-fix https://github.com/org/repo/pull/42 --dry-run
```

### Automatic mode

Skip confirmations and fix everything:

```text
/adk:code-review-fix https://github.com/org/repo/pull/42 --auto
```

---

## Review an Entire Repository

Use `code-review-repo` for a full codebase audit. This is read-only — it produces a prioritized improvement plan without modifying files.

```text
/adk:code-review-repo
```

### Focus on specific dimensions

```text
/adk:code-review-repo --focus architecture
/adk:code-review-repo --focus security
/adk:code-review-repo --focus all
```

Available focus areas: architecture, code quality, patterns, testing, security, performance, dependencies, documentation.

### Review a specific path

```text
/adk:code-review-repo ./src/api
```

### Output format

```text
/adk:code-review-repo --output json
```

---

## Multi-Model Cross-Review

For high-stakes PRs, use `--cross` to run a multi-model review where multiple AI models review independently and findings are merged:

```text
/adk:code-review-pr https://github.com/org/repo/pull/42 --cross
```

This produces a consensus review with higher confidence ratings.

---

## Finalize and Merge a PR

Check that all review comments are addressed and the PR is merge-ready:

```text
/adk:code-review-pr https://github.com/org/repo/pull/42 --action finalize
```

Check PR status (CI, approvals, conflicts):

```text
/adk:code-review-pr https://github.com/org/repo/pull/42 --action status
```

---

## Which Skill to Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Review a PR (GitHub/Bitbucket) | `code-review-pr` | `<url>`, `--focus`, `--publish` |
| Review local changes | `code-review-pr` | (no args), `--branch` |
| Self-review before PR | `code-review-pr` | `--fix` |
| Generate PR description | `code-review-pr` | `--action describe` |
| Fix reviewer comments | `code-review-fix` | `<url>`, `--filter`, `--dry-run` |
| Review entire repo | `code-review-repo` | `--focus`, `--output` |
| Multi-model review | `code-review-pr` | `--cross` |
| Check merge readiness | `code-review-pr` | `--action finalize` |

## Related Skills

- **[`audit`](/reference/skills/audit/)** — deeper codebase audits with security/performance/dependency focus
- **[`dev-build`](/reference/skills/dev-build/)** — implement fixes after review
- **[`dev-commit`](/reference/skills/dev-commit/)** — commit changes and generate PR descriptions
