---
title: Skills Overview
description: Browse all 51 ADK skills organized by category
order: 3
---

# Skills Overview

ADK provides 51 skills organized into four categories: **guideline skills** (shared knowledge, auto-invoked), **connector skills** (platform API wrappers), **task skills** (user-facing engineering tasks), and **routing skills** (orchestrators). Only the relevant skill files load per task (see [lazy loading](/guide/philosophy/#token-efficient-lazy-loading)).

## How Skills Work

- **Human-in-the-loop**: confirms intent before acting, presents options, gets plan approval
- **Plan first**: execution only starts after an approved plan exists
- **Self-sufficient**: task skills include inline fallback summaries for shared knowledge, so they work even if guideline skills are not installed
- **Auto mode**: pass `--auto` to skip confirmations

## Naming Convention

| Install Method | Invocation Pattern | Example |
| -------------- | ------------------ | ------- |
| Claude Plugin | `/adk:<skill-name>` | `/adk:code-review-pr` |
| skills.sh | `/<skill-name>` | `/code-review-pr` |
| Local plugin-dir | `/adk:<skill-name>` | `/adk:code-review-pr` |

The `name` field in each skill's frontmatter is set to `<skill-name>`. When installed as a Claude plugin, the plugin namespace `adk:` is used and the folder name determines the command. When installed via skills.sh, the `name` field is used directly.

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
| Create a PR description | `dev-commit --action pr-describe` | — |
| Write an ADR/RFC | `docs-write` | `docs-guidelines`, `docs-md` |
| Write a blog post | `docs-write --type blog` | `docs-guidelines`, `docs-md` |
| Generate repo docs | `docs-repo` | `docs-md`, `docs-guidelines` |
| Review documentation | `docs-review` | `docs-guidelines`, `review-standards` |
| Update docs from comments | `docs-crud` | `docs-guidelines`, `docs-md` |
| Create a diagram | `diagram` (routes to engine) | engine-specific skill |
| Mermaid sequence diagram | `diagram-mermaid` | — |
| Architecture overview | `diagram-excalidraw` | — |
| Dependency graph | `diagram-graphviz` | — |
| Network topology | `diagram-drawio` | — |
| Data visualization | `chart` | — |
| Design a UI | `design` | `architecture` |
| Security audit | `audit --focus security` | `coding`, `review-standards` |
| Performance audit | `audit --focus performance` | `coding` |
| Plan an implementation | `plan` | `architecture`, `principal-engineer` |
| Write a spec | `spec` | `docs-guidelines` |
| Research a topic | `research` | — |
| Run acceptance tests | `test` | — |
| Set up new project | `project` | `setup` |
| Hand off session | `handoff` | — |
| Configure tools/MCP | `setup` | — |
| Multi-model review | `team` | any review skill |
| Any task (auto-route) | `use` | routes to the right skill(s) |

## Guideline Skills (16 shared helpers)

Provide reusable knowledge and standards. Auto-invoked by task skills when available. Each task skill includes one-line inline fallback summaries, so it works even if the guideline skill is not installed.

| Skill | Invocation | What It Provides |
| ----- | ---------- | ---------------- |
| `workflow` | `/adk:workflow` | 6-phase workflow framework with complexity-adaptive phase skipping |
| `communication` | `/adk:communication` | Communication style: lead with conclusion, no preamble, concise by default |
| `principal-engineer` | `/adk:principal-engineer` | PE questioning: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | `/adk:agentic-teams` | Child-agent contract: team shapes for review, research, docs, security, migration |
| `output-format` | `/adk:output-format` | Verbosity modes, PR comment templates, priority/principle labels |
| `interaction` | `/adk:interaction` | Inline protocols: intent confirm, approach select, plan approve, review findings |
| `interactivity` | `/adk:interactivity` | Structured interaction orchestration (inline-first, optional TUI for large forms) |
| `preflight-check` | `/adk:preflight-check` | Preflight validations for dependencies, MCP, and tool readiness |
| `review-standards` | `/adk:review-standards` | Review pipeline, comment template, source routing, postback rules |
| `coding` | `/adk:coding` | Detects repo stack, lazy-loads matching coding guidelines (16 guideline files) |
| `docs-guidelines` | `/adk:docs-guidelines` | Detects document type, lazy-loads matching writing guidelines (24 guideline files) |
| `docs-md` | `/adk:docs-md` | Detects markdown target (pagesmith/GitHub/plain), loads formatting guidelines |
| `architecture` | `/adk:architecture` | Architecture patterns, principles, and anti-pattern detection |

Connector skills (auto-invoked by task skills for platform APIs):

| Skill | Invocation | What It Provides |
| ----- | ---------- | ---------------- |
| `github` | `/adk:github` | GitHub PR, issue, review, and repo operations via `gh` CLI |
| `bitbucket` | `/adk:bitbucket` | Bitbucket PR, comment, and repo operations via API |
| `confluence` | `/adk:confluence` | Confluence page, comment, and space operations |
| `jira` | `/adk:jira` | Jira issue, board, project, and search operations |

## Task Skills (28 user-facing)

### Code Review

| Skill | Invocation | Description |
| ----- | ---------- | ----------- |
| `code-review-pr` | `/adk:code-review-pr` | Code review: PR, local, branch + fix/comment/interactive |
| `code-review-repo` | `/adk:code-review-repo` | Whole-repo review with prioritized improvement plan |
| `code-review-fix` | `/adk:code-review-fix` | Fix PR comments, reply to reviewers, mark resolved |
| `docs-review` | `/adk:docs-review` | Review documents (local, Confluence, Google Docs) |

> [!TIP]
> `/adk:code-review-pr` auto-detects whether you're the PR author (fix mode) or reviewer (review mode).

### Development

| Skill | Invocation | Description |
| ----- | ---------- | ----------- |
| `dev-build` | `/adk:dev-build` | Implement features, fix bugs, enhance code, TDD |
| `dev-refactor` | `/adk:dev-refactor` | Extract, rename, restructure, simplify, modernize code |
| `dev-migrate` | `/adk:dev-migrate` | Framework/library migration with breaking change analysis |
| `dev-commit` | `/adk:dev-commit` | Smart commit messages and PR descriptions |
| `plan` | `/adk:plan` | Brainstorm, write, execute, and track implementation plans |
| `spec` | `/adk:spec` | Write specs, analyze consistency, generate checklists |
| `design` | `/adk:design` | UI/UX design direction + visual audit |

### Documentation

| Skill | Invocation | Description |
| ----- | ---------- | ----------- |
| `docs-write` | `/adk:docs-write` | Create/update formal documents (ADR, RFC, blog, changelog) |
| `docs-repo` | `/adk:docs-repo` | Generate comprehensive repo documentation (pagesmith) |
| `docs-crud` | `/adk:docs-crud` | Manage doc lifecycle: create, update, improve, comment-reply |
| `docs-confluence` | `/adk:docs-confluence` | Confluence-specific read/write with format mapping |

> [!NOTE]
> `/adk:docs-repo` auto-detects pagesmith when `pagesmith.config.json5` exists and uses its frontmatter and folder/README.md conventions.

### Diagrams

| Skill | Invocation | Description |
| ----- | ---------- | ----------- |
| `diagram-mermaid` | `/adk:diagram-mermaid` | Mermaid diagrams with full syntax reference (21 types) |
| `diagram-excalidraw` | `/adk:diagram-excalidraw` | Excalidraw hand-drawn style architecture diagrams |
| `diagram-graphviz` | `/adk:diagram-graphviz` | Graphviz DOT diagrams for dependency graphs |
| `diagram-drawio` | `/adk:diagram-drawio` | Draw.io precise layout for network/enterprise architecture |
| `chart` | `/adk:chart` | Data charts (bar, line, pie, scatter, area, 30+ types) from CSV/JSON |

> [!TIP]
> Each diagram skill contains a complete syntax reference. Use `--engine` to force an engine, or let `/adk:diagram` auto-detect.

### Quality & Research

| Skill | Invocation | Description |
| ----- | ---------- | ----------- |
| `audit` | `/adk:audit` | Audit: codebase, security, performance, dependencies |
| `research` | `/adk:research` | Multi-agent research with citations |
| `test` | `/adk:test` | User acceptance testing with interactive verification |

### Project & Session

| Skill | Invocation | Description |
| ----- | ---------- | ----------- |
| `project` | `/adk:project` | Initialize projects, manage milestones and ideas |
| `handoff` | `/adk:handoff` | Pause/resume work sessions, context threads |
| `setup` | `/adk:setup` | Configure CLI tools, MCP servers, hooks, and system prompt |
| `deps-tracker` | `/adk:deps-tracker` | Track upstream dependencies and sync updates |
| `interactivity` | `/adk:interactivity` | Structured interaction: options, data capture, approvals |

## Routing Skills (5 orchestrators)

Coordinate and route work across other skills. Category routers auto-detect the right sub-skill.

| Skill | Invocation | Description |
| ----- | ---------- | ----------- |
| `use` | `/adk:use` | Default orchestrator: expand intent, identify skills, confirm, execute |
| `team` | `/adk:team` | Multi-model review, agent team dispatch |
| `code-review` | `/adk:code-review` | Code review router: detects type, routes to code-review-pr/repo/fix |
| `docs` | `/adk:docs` | Documentation router: routes to docs-write/crud/repo/review/confluence |
| `dev` | `/adk:dev` | Development router: routes to dev-build/refactor/migrate/commit |
| `diagram` | `/adk:diagram` | Diagram router: detects engine, routes to mermaid/excalidraw/drawio/graphviz |
