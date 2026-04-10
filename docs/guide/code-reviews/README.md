---
title: Code Reviews
description: Review PRs, fix comments, self-review local changes, and audit entire repositories
order: 1
---

# Code Reviews

ADK gives you two ways to start a review: use the `code-review` router when you want it to pick the right path, or jump straight to the specific review skill when you already know the target.

> **Quick start:** `/adk:code-review <prompt-text>` lets the router decide whether you need a PR review, a local review, or a repository-wide pass.

## Scenarios

- [Review A Pull Request](#review-a-pull-request)
- [Review Local Changes](#review-local-changes)
- [Fix Review Comments](#fix-review-comments)
- [Review An Entire Repository](#review-an-entire-repository)
- [Describe Or Finalize A PR](#describe-or-finalize-a-pr)

---

## Review A Pull Request

Use `code-review-pr` when you already have a GitHub or Bitbucket PR URL. Start with the plain URL, then add flags only when you want to narrow the review or change how the findings are handled.

```text
/adk:code-review-pr <pr-url>
/adk:code-review-pr https://github.com/org/repo/pull/42
/adk:code-review-pr <pr-url> --focus security
/adk:code-review-pr <pr-url> --mode interactive
/adk:code-review-pr <pr-url> --publish
/adk:code-review-pr <pr-url> --skip-repo
/adk:code-review-pr <pr-url> --context <url>
```

Use `--focus` when you want the review weighted toward one concern, `--mode interactive` when you want to triage findings before posting them, and `--publish` when the comments should go back to the PR instead of staying local.

---

## Review Local Changes

You can use the same skill before a PR exists. With no target it reviews your staged and unstaged work; with a branch name it compares that branch against its base.

```text
/adk:code-review-pr
/adk:code-review-pr <branch-name>
/adk:code-review-pr feature/auth-v2
/adk:code-review-pr --fix
/adk:code-review-pr <pr-url> --cross
```

Use `--fix` for self-review when you want the skill to apply straightforward fixes locally. Use `--cross` on high-stakes changes when you want the multi-model peer-review path before you ship.

---

## Fix Review Comments

When reviewers have already left feedback on a PR, switch to `code-review-fix`. It reads unresolved comments, categorizes them, and helps you apply fixes or push back with evidence.

```text
/adk:code-review-fix <pr-url>
/adk:code-review-fix https://github.com/org/repo/pull/42
/adk:code-review-fix <pr-url> --filter blocker
/adk:code-review-fix <pr-url> --dry-run
/adk:code-review-fix <pr-url> --auto
```

`--filter` is the quickest way to narrow the queue. `--dry-run` is useful when you want a plan before touching code, and `--auto` is for cases where you want the workflow to process everything it can without extra approvals.

---

## Review An Entire Repository

Use `code-review-repo` when the target is the codebase itself rather than a diff. This is the right entry point for architecture, consistency, testing, documentation, or technical-debt reviews.

```text
/adk:code-review-repo
/adk:code-review-repo <path>
/adk:code-review-repo src/backend/
/adk:code-review-repo --focus architecture
/adk:code-review-repo --output json
```

Point it at a directory when you only want one package or subsystem, and use `--focus` when you want the report weighted toward one review dimension.

---

## Describe Or Finalize A PR

`code-review-pr` also owns the PR-management actions that happen after the review itself: writing a description, checking merge readiness, and reporting current status.

```text
/adk:code-review-pr <pr-url> --action describe
/adk:code-review-pr <pr-url> --action finalize
/adk:code-review-pr <pr-url> --action status
```

Use `--action describe` when the diff needs a clean title and summary, `--action finalize` before merge, and `--action status` when you want a quick readiness read without changing anything.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Let ADK choose the review path | `code-review` | `<prompt-text>` |
| Review a PR | `code-review-pr` | `<pr-url>`, `--focus`, `--publish` |
| Review local changes | `code-review-pr` | no target, `<branch-name>`, `--fix` |
| Fix reviewer comments | `code-review-fix` | `<pr-url>`, `--filter`, `--dry-run` |
| Review a repository | `code-review-repo` | `<path>`, `--focus`, `--output` |
| Generate a PR description or finalize | `code-review-pr` | `<pr-url>`, `--action` |

## Related Skills

- **[`audit`](/reference/skill-audit/)** for deeper security, performance, dependency, or codebase audits.
- **[`dev-build`](/reference/skill-dev-build/)** when a review finding turns into real implementation work.
- **[`dev-commit`](/reference/skill-dev-commit/)** when you are ready to package the result into a commit or PR description.
