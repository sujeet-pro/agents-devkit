---
title: Skills Overview
description: Browse all 41 ADK skills organized by category
order: 2
---

# Skills Overview

ADK provides 41 skills organized into three categories: **guideline skills** (shared knowledge, auto-invoked), **task skills** (user-facing engineering tasks), and **routing skills** (orchestrators).

## How Skills Work

Every skill follows these principles:

- **Human-in-the-loop**: confirms intent before acting, presents options, gets plan approval
- **Plan first**: execution only starts after an approved plan exists
- **Self-sufficient**: task skills include inline fallback summaries for shared knowledge, so they work even if guideline skills are not installed
- **Auto mode**: pass `--auto` to skip confirmations

## Naming Convention

| Install Method | Invocation Pattern | Example |
| -------------- | ------------------ | ------- |
| Claude Plugin | `/adk:<skill-name>` | `/adk:code-review-pr` |
| skills.sh | `/adk-<skill-name>` | `/adk-code-review-pr` |

## Recipe Table

**If you want to do X, use these skills:**

| Goal | Primary Skill | Also Uses |
| ---- | ------------- | --------- |
| Review a PR | `code-review-pr` | `coding`, `review-standards` |
| Fix PR review comments | `code-review-fix` | `coding`, `review-standards` |
| Review entire codebase | `code-review-repo` | `architecture`, `coding`, `review-standards` |
| Implement a new feature | `dev-build` | `coding`, `architecture` |
| Fix a bug | `dev-build --mode debug` | `coding` |
| Refactor code | `dev-refactor` | `coding`, `architecture` |
| Migrate a framework | `dev-migrate` | `research`, `coding` |
| Create a commit | `dev-commit` | — |
| Write an ADR/RFC | `docs-write` | `docs-guidelines`, `docs-md` |
| Generate repo docs | `docs-repo` | `docs-md`, `docs-guidelines` |
| Review documentation | `docs-review` | `docs-guidelines`, `review-standards` |
| Create a diagram | `diagram` (routes to engine) | engine-specific skill |
| Security audit | `audit --focus security` | `coding`, `review-standards` |
| Plan an implementation | `plan` | `architecture`, `principal-engineer` |
| Research a topic | `research` | — |
| Any task (auto-route) | `use` | routes to the right skill(s) |

## Code Review Skills

| Skill | When to Use |
|-------|-------------|
| `/adk:code-review-pr` | Review a pull request (GitHub/Bitbucket), local changes, or branch diff |
| `/adk:code-review-repo` | Review an entire repository for architecture, quality, and tech debt |
| `/adk:code-review-fix` | Fix PR review comments — apply changes, reply to reviewers, mark resolved |
| `/adk:docs-review` | Review documents from Confluence, Google Docs, or local files |

> [!TIP]
> `/adk:code-review-pr` auto-detects whether you're the PR author (fix mode) or reviewer (review mode).

## Development Skills

| Skill | When to Use |
|-------|-------------|
| `/adk:dev-build` | Implement features, fix bugs, enhance code, or run TDD workflows |
| `/adk:dev-refactor` | Extract, rename, restructure, simplify, or modernize code patterns |
| `/adk:dev-migrate` | Migrate frameworks, libraries, or language versions with breaking change analysis |
| `/adk:dev-commit` | Generate meaningful commit messages and PR descriptions |
| `/adk:plan` | Brainstorm, write, execute, and track implementation plans |
| `/adk:spec` | Write specifications, analyze consistency, generate checklists |
| `/adk:design` | UI/UX design direction, visual audit, or framework porting |

## Documentation Skills

| Skill | When to Use |
|-------|-------------|
| `/adk:docs-write` | Create or update formal documents (ADR, RFC, blog, changelog, runbook) |
| `/adk:docs-repo` | Generate comprehensive documentation for an entire repository |
| `/adk:docs-review` | Review documentation for accuracy, completeness, and clarity |
| `/adk:docs-crud` | Manage doc lifecycle: create pages, update content, respond to comments |

> [!NOTE]
> `/adk:docs-repo` auto-detects pagesmith when `pagesmith.config.json5` exists and uses its frontmatter and folder/README.md conventions.

## Diagram Skills

| Skill | When to Use |
|-------|-------------|
| `/adk:diagram` | Create diagrams — auto-routes to the best engine |
| `/adk:diagram-mermaid` | Text-based diagrams: flowcharts, sequence, ER, class, state, and 15+ more types |
| `/adk:diagram-excalidraw` | Hand-drawn style: architecture overviews, system context, freeform layouts |
| `/adk:diagram-graphviz` | Strict DOT layout: dependency graphs, existing .dot assets |
| `/adk:diagram-drawio` | Precise layout: network topology, enterprise architecture, BPMN, multi-page |

> [!TIP]
> Each diagram skill contains a complete syntax reference. Use `--engine` to force an engine, or let `/adk:diagram` auto-detect.

## Quality & Research Skills

| Skill | When to Use |
|-------|-------------|
| `/adk:audit` | Codebase, security, performance, or dependency audit |
| `/adk:research` | Deep multi-agent research with citations from primary sources |
| `/adk:test` | User acceptance testing with interactive verification |

## Project & Session Skills

| Skill | When to Use |
|-------|-------------|
| `/adk:project` | Initialize projects, manage milestones, capture ideas |
| `/adk:handoff` | Pause/resume work sessions, context threads |
| `/adk:setup` | Configure CLI tools, MCP servers, and hooks |
| `/adk:deps-tracker` | Track upstream dependencies (diagramkit, pagesmith, superpowers) |

## Routing Skills

| Skill | When to Use |
|-------|-------------|
| `/adk:use` | **Start here** for any general task — expands intent, routes to the right skills |
| `/adk:team` | Multi-model review or agent team dispatch for complex tasks |

## Guideline Skills

These are auto-invoked by task skills. Each task skill includes an inline fallback summary, so guideline skills are optional but provide richer guidance when installed.

| Skill | What It Provides |
|-------|-----------------|
| `/adk:workflow` | 6-phase workflow framework with complexity-adaptive skipping |
| `/adk:communication` | Communication style: lead with conclusion, no preamble, concrete specifics |
| `/adk:principal-engineer` | PE questioning: need? simplest? alternatives? maintenance? clarity? |
| `/adk:agentic-teams` | Child-agent contract and standard team shapes (review, research, docs, security, migration) |
| `/adk:output-format` | Verbosity modes, PR comment templates, priority/principle labels |
| `/adk:interaction` | Inline protocols for intent confirm, approach select, plan approve, review findings |
| `/adk:preflight-check` | Preflight validation for dependencies, MCP, and tool readiness |
| `/adk:review-standards` | Review pipeline, comment template, source routing, postback rules |
| `/adk:coding` | Detects repo tech stack, loads relevant coding guidelines (16 files) |
| `/adk:docs-guidelines` | Detects document type, loads relevant writing guidelines (24 files) |
| `/adk:docs-md` | Detects markdown target (pagesmith/GitHub/plain), loads formatting guidelines |
| `/adk:architecture` | Architecture patterns, principles, and anti-pattern detection |
