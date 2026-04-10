---
title: Development
description: Build features, debug issues, run TDD, refactor code, and migrate frameworks
order: 2
---

# Development

Use the `dev` router when you want ADK to decide which development workflow fits the request, or jump directly to the specialized skill when you already know whether the job is implementation, debugging, refactoring, migration, or wrap-up.

> **Quick start:** `/adk:dev <prompt-text>` routes the request to the right development skill and keeps the workflow small when the task is small.

## Scenarios

- [Build Or Extend Something](#build-or-extend-something)
- [Debug Or Verify](#debug-or-verify)
- [Refactor Safely](#refactor-safely)
- [Migrate Dependencies Or Frameworks](#migrate-dependencies-or-frameworks)
- [Wrap Up Your Changes](#wrap-up-your-changes)

---

## Build Or Extend Something

Start with `dev-build` for new features, extensions to existing behavior, quick fixes, or isolated experiments. The skill can read a spec or plan file when you already have one.

```text
/adk:dev-build <prompt-text>
/adk:dev-build implement user authentication with OAuth2
/adk:dev-build --mode enhance <prompt-text>
/adk:dev-build --spec <path> <prompt-text>
/adk:dev-build --plan <path> <prompt-text>
/adk:dev-build --scope <path> <prompt-text>
/adk:dev-build --branch <name> <prompt-text>
/adk:dev-build --mode quick <prompt-text>
/adk:dev-build --mode worktree <prompt-text>
```

Use `--mode enhance` when you are extending something that already exists, `--scope` when you want to keep the blast radius tight, and `--mode worktree` when you want the experiment isolated in a separate git worktree.

---

## Debug Or Verify

Use debug mode when the main job is diagnosis, and verify mode when the implementation is already done and you only want confidence checks.

```text
/adk:dev-build --mode debug <prompt-text>
/adk:dev-build --mode debug the login form crashes on empty email
/adk:dev-build --fix <prompt-text>
/adk:dev-build --mode tdd <prompt-text>
/adk:dev-build --tdd <prompt-text>
/adk:dev-build --mode verify <prompt-text>
```

`--fix` keeps you in the debugging workflow but lets the skill implement the fix once the root cause is understood. `--tdd` is just the convenient alias for the TDD mode when you want tests first.

---

## Refactor Safely

Reach for `dev-refactor` when the job is a behavior-preserving transformation rather than new product behavior.

```text
/adk:dev-refactor <prompt-text>
/adk:dev-refactor --pattern extract <prompt-text>
/adk:dev-refactor --pattern rename <prompt-text>
/adk:dev-refactor --pattern restructure <prompt-text>
/adk:dev-refactor --scope <path> <prompt-text>
```

The pattern flag is the main selector here: use it when you want the skill to skip inference and go directly to extraction, rename, restructure, simplify, or modernization work.

---

## Migrate Dependencies Or Frameworks

Use `dev-migrate` when the core question is “how do we move from one version, package, or framework to another without breaking the system?”

```text
/adk:dev-migrate <source> to <target>
/adk:dev-migrate react@17 to react@19
/adk:dev-migrate --scope <path> <source> to <target>
/adk:dev-migrate --dry-run <source> to <target>
```

Start with `--dry-run` when you want the breakage analysis and migration path before any code changes happen.

---

## Wrap Up Your Changes

After implementation, refactoring, or migration work is done, use `dev-commit` to package the result cleanly.

```text
/adk:dev-commit
```

This is the wrap-up skill for staging, commit-message generation, and PR-description generation when you have finished the development work itself.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Let ADK pick the development path | `dev` | `<prompt-text>` |
| Build or extend behavior | `dev-build` | `<prompt-text>`, `--mode`, `--spec`, `--plan`, `--scope` |
| Debug or verify | `dev-build` | `--mode debug`, `--fix`, `--mode verify` |
| Refactor | `dev-refactor` | `<prompt-text>`, `--pattern`, `--scope` |
| Migrate packages or frameworks | `dev-migrate` | `<source> to <target>`, `--scope`, `--dry-run` |
| Commit and summarize | `dev-commit` | no required flags |

## Related Skills

- **[`plan`](/reference/skill-plan/)** when you want the plan first and the code second.
- **[`spec`](/reference/skill-spec/)** when the missing artifact is a requirements document rather than code.
- **[`code-review-pr`](/reference/skill-code-review-pr/)** when you want to self-review the result before or after a PR is opened.
