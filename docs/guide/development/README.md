---
title: Development
description: Build features, debug issues, run TDD, refactor code, and migrate frameworks
order: 2
---

# Development

ADK's development skills cover the full implementation lifecycle — from building features and debugging to refactoring and migrating frameworks. The `dev` router auto-detects the right sub-skill, or invoke each directly.

> **Quick start:** `/adk:dev <describe what you want to build or fix>` — the router picks the right skill.

## Scenarios

- [Build a new feature](#build-a-new-feature)
- [Debug an issue](#debug-an-issue)
- [Test-driven development](#test-driven-development)
- [Enhance existing code](#enhance-existing-code)
- [Refactor code](#refactor-code)
- [Migrate frameworks or libraries](#migrate-frameworks-or-libraries)
- [Create commits and PR descriptions](#create-commits-and-pr-descriptions)
- [Quick one-off changes](#quick-one-off-changes)
- [Isolated experiments with worktrees](#isolated-experiments-with-worktrees)

---

## Build a New Feature

Use `dev-build` to implement a feature from a description, spec, or plan.

```text
/adk:dev-build implement user authentication with OAuth2
```

### From a spec or plan

Reference an existing spec or plan file:

```text
/adk:dev-build --spec ./docs/specs/auth-spec.md implement the authentication module
/adk:dev-build --plan ./.temp/auth-plan/plan.md execute the auth implementation plan
```

### Full implementation with tests

Use `--full` to include test generation alongside the implementation:

```text
/adk:dev-build --full implement the payment processing module
```

### Scoped implementation

Limit changes to specific files or directories:

```text
/adk:dev-build --scope src/api/ add rate limiting to all API endpoints
```

---

## Debug an Issue

ADK auto-detects debug mode from keywords like "fix", "bug", "error", "broken":

```text
/adk:dev-build fix the memory leak in the WebSocket connection handler
/adk:dev-build debug why the login page shows a blank screen after redirect
```

Or set the mode explicitly:

```text
/adk:dev-build --mode debug the API returns 500 on POST /users when email contains unicode
```

The debug workflow: reproduce → diagnose → hypothesize → fix → verify.

---

## Test-Driven Development

Use TDD mode to write tests first, then implement until they pass:

```text
/adk:dev-build --mode tdd implement a rate limiter with sliding window
/adk:dev-build --tdd add input validation for the user registration form
```

The TDD cycle: write failing tests → implement → green → refactor.

---

## Enhance Existing Code

Improve or extend existing functionality:

```text
/adk:dev-build --mode enhance add pagination to the users list API
/adk:dev-build enhance the search to support fuzzy matching
```

ADK detects "enhance" mode from signals like "add ... to", "improve", "extend", "optimize".

---

## Refactor Code

Use `dev-refactor` for safe, tested code transformations.

### Extract

Pull logic into a separate function, class, or module:

```text
/adk:dev-refactor extract the validation logic from UserController into a ValidationService
/adk:dev-refactor --pattern extract split the monolithic API handler into route-specific modules
```

### Rename

Rename symbols across the codebase:

```text
/adk:dev-refactor --pattern rename rename getUserData to fetchUserProfile across the codebase
```

### Restructure

Reorganize file and directory structure:

```text
/adk:dev-refactor --pattern restructure move from flat file structure to feature-based folders
```

### Simplify

Reduce complexity and remove dead code:

```text
/adk:dev-refactor --pattern simplify reduce cyclomatic complexity in the payment module
```

### Modernize

Update patterns to use current language features:

```text
/adk:dev-refactor --pattern modernize convert callbacks to async/await in the data layer
```

### Scoped refactoring

```text
/adk:dev-refactor --scope src/services/ simplify error handling patterns
```

---

## Migrate Frameworks or Libraries

Use `dev-migrate` to upgrade or swap dependencies with breaking-change analysis.

### Version upgrade

```text
/adk:dev-migrate React 17 to React 18
/adk:dev-migrate Node 18 to Node 22
/adk:dev-migrate Python 3.9 to Python 3.12
```

### Library swap

```text
/adk:dev-migrate moment.js to dayjs
/adk:dev-migrate Express to Fastify
```

### Dry run

Analyze breaking changes without making modifications:

```text
/adk:dev-migrate React 17 to React 18 --dry-run
```

### Scoped migration

```text
/adk:dev-migrate --scope src/frontend/ Vue 2 to Vue 3
```

---

## Create Commits and PR Descriptions

Use `dev-commit` for smart commits that auto-detect your convention.

```text
/adk:dev-commit
```

This stages changes, generates a commit message (detecting conventional commits, gitmoji, or plain format), and creates the commit. Also generates PR descriptions from branch diffs.

---

## Quick One-Off Changes

For simple changes that don't need the full workflow:

```text
/adk:dev-build --mode quick add a loading spinner to the dashboard
```

Quick mode skips planning phases and goes straight to implementation.

---

## Isolated Experiments with Worktrees

For experimental changes you might discard:

```text
/adk:dev-build --mode worktree try implementing auth with Passport.js
```

Worktree mode creates a git worktree, implements there, and lets you merge or discard.

### Named branch

```text
/adk:dev-build --mode worktree --branch experiment/new-auth try the new auth approach
```

---

## Which Skill to Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Build a feature | `dev-build` | `--mode implement`, `--spec`, `--plan`, `--full` |
| Fix a bug | `dev-build` | `--mode debug`, `--scope` |
| Write tests first | `dev-build` | `--mode tdd`, `--tdd` |
| Improve existing code | `dev-build` | `--mode enhance` |
| Quick change | `dev-build` | `--mode quick` |
| Experiment safely | `dev-build` | `--mode worktree`, `--branch` |
| Extract / rename / restructure | `dev-refactor` | `--pattern`, `--scope` |
| Upgrade or swap frameworks | `dev-migrate` | `<source> to <target>`, `--dry-run` |
| Commit with smart message | `dev-commit` | (auto-detects convention) |

## Related Skills

- **[`code-review-pr`](/reference/skill-code-review-pr/)** — self-review before creating a PR
- **[`plan`](/reference/skill-plan/)** — create an implementation plan before building
- **[`spec`](/reference/skill-spec/)** — write or analyze specifications
- **[`test`](/reference/skill-test/)** — user acceptance testing after implementation
