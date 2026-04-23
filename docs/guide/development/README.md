---
title: Development
description: Build features, fix bugs, refactor, migrate frameworks, author tests, and audit dependencies — all routed through the @adk:build category router.
order: 2
---

# Development

Add features, fix bugs, restructure code without behavior changes, upgrade frameworks, author tests, and keep dependencies clean. Every "change the code" intent flows through the `@adk:build` category router.

> **Quick start:** `/adk:build` is the simplest entrypoint for this category.

## Included Skills

| Skill | Purpose | Reference |
| --- | --- | --- |
| `/adk:build` | Category router. Picks one of the task skills below based on the goal of the change. | [Details](../../reference/skill-build.md) |
| `/adk:build-feature` | Add or extend a feature end-to-end (plan -> implement -> validate -> handoff to review). | [Details](../../reference/skill-build-feature.md) |
| `/adk:build-bugfix` | Diagnose and fix a specific bug with regression-test coverage. | [Details](../../reference/skill-build-bugfix.md) |
| `/adk:build-refactor` | Restructure code without changing observable behavior; back-stopped by tests. | [Details](../../reference/skill-build-refactor.md) |
| `/adk:build-migrate` | Upgrade a framework, library, or runtime; codemod where possible. | [Details](../../reference/skill-build-migrate.md) |
| `/adk:build-test` | Author or expand tests (unit, integration, E2E) for a chosen surface. | [Details](../../reference/skill-build-test.md) |
| `/adk:build-deps` | Audit, upgrade, or prune dependencies; surface CVEs and license issues. | [Details](../../reference/skill-build-deps.md) |
| `/adk:build-api` | Design or evolve a stable interface (REST/RPC/library export/CLI) using contract-first discipline. | [Details](../../reference/skill-build-api.md) |
| `/adk:build-perf` | Diagnose and fix a performance regression with measure-first discipline; add a guardrail. | [Details](../../reference/skill-build-perf.md) |
| `/adk:build-security` | Implement a security-hardening change with a three-tier boundary system + secret scanning. | [Details](../../reference/skill-build-security.md) |

## How it works internally

`@adk:build` is a **category router**, not a worker — it never writes code itself. The router asks one question (what is the goal of the change?) and dispatches to the right task skill. Each task skill follows the same internal phase contract:

1. **Plan** — reads context, restates the change, surfaces 2-3 viable approaches with trade-offs (plan-spec / plan-design / plan-roadmap delegated when the change is non-trivial).
2. **Implement** — applies the diff incrementally; never bulk-rewrites without an approval gate.
3. **Validate** — runs the project's test/lint suite plus its own per-skill validator. Failures pause the run; under `--auto` they short-circuit to a report.
4. **Hand off** — final step always calls `/adk:review-local` so the change is self-reviewed before the user commits.

The `@adk:auto` top router will invoke `@adk:build` automatically when the prompt says "implement", "fix", "refactor", "migrate", "add tests for", or "upgrade <dep>".

<figure>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./diagrams/.diagramkit/build-routing-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="./diagrams/.diagramkit/build-routing-light.svg" />
    <img alt="Routing tree for @adk:build: branches on goal (new/extend, fix bug, restructure, upgrade, tests, deps, interface design, performance, security harden) into build-feature, build-bugfix, build-refactor, build-migrate, build-test, build-deps, build-api, build-perf, or build-security. All converge to plan -> implement -> validate, then hand off to review-local." src="./diagrams/.diagramkit/build-routing-light.svg" />
  </picture>
  <figcaption><i>How <code>@adk:build</code> routes by goal. Every task skill terminates by handing off to <code>/adk:review-local</code> for a self-review pass before commit.</i></figcaption>
</figure>

## Example invocations

```text
/adk:build                                # router — asks what you're trying to do
/adk:build-feature "add CSV export"       # feature work
/adk:build-bugfix "checkout 500 on Safari"# bugfix
/adk:build-migrate "Next.js 14 -> 15"     # framework upgrade
/adk:build-test "add E2E for /checkout"   # test authoring
/adk:build-deps --auto                    # dependency audit, unattended
```

## Outputs

- `.temp/task-<slug>/plan.md` — the approach picked + alternatives considered.
- Code edits applied directly to the working tree (diff visible via `git status` / `git diff`).
- `.temp/task-<slug>/validation/` — per-phase validator output (lint, tests, build).
- `.temp/task-<slug>/review.md` — output of the auto-handoff to `/adk:review-local`.

## How To Use This Guide

Start with the skill whose primary job matches the outcome you want. Use the linked reference page for the exact flag surface, workflow contract, and validation expectations.
