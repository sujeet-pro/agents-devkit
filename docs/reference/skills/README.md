---
title: Skill Reference
description: Complete reference for all 49 ADK skills
order: 1
---

# Skill Reference

Each skill's `SKILL.md` is the definitive reference. Use `--help` on any skill to see its parameters.

## Strategy and Governance

- [Skill Landscape and Gap Analysis](./LANDSCAPE.md)
- [Skill Inspiration Map](./INSPIRATION-MAP.md)
- [Category Routing Map](./CATEGORY-ROUTING.md)

## Common Parameters

All user-invocable skills support:

| Parameter | Values | Description |
|-----------|--------|-------------|
| `--help` | flag | Show skill parameters and examples |
| `--verbosity` | `short`, `standard`, `detailed` | Output detail level |
| `--auto` | flag | Skip human confirmations, execute full workflow |

## Review Skills (Task)

| Skill | Tier | Description |
|-------|------|-------------|
| `code-review-pr` | full | Code review for PRs (GitHub/Bitbucket), local changes, or branch diffs. Supports fix, describe, finalize actions. |
| `code-review-repo` | full | Whole-repository review. Produces a prioritized improvement plan covering architecture, quality, patterns, and debt. |
| `code-review-fix` | full | Reads PR review comments, applies code fixes, replies to reviewers, marks threads resolved. |
| `docs-review` | full | Reviews documents from local files, Confluence, or Google Docs. |

## Development Skills (Task)

| Skill | Tier | Description |
|-------|------|-------------|
| `dev-build` | full | Implement features, fix bugs, enhance code, or run TDD. Modes: implement, enhance, debug, tdd, verify, worktree, quick. |
| `dev-refactor` | full | Extract, rename, restructure, simplify, or modernize code. Safe, tested transformations. |
| `dev-migrate` | full | Framework/library/version migration. Reads changelogs, maps breaking changes, generates and executes plan. |
| `dev-commit` | full | Smart commit messages and PR descriptions. Auto-detects convention (conventional, gitmoji, plain). |
| `plan` | full | Brainstorm, write, execute, and track implementation plans. Modes: brainstorm, write, execute, track. |
| `spec` | full | Write specifications, analyze consistency, generate checklists, write constitutions. |
| `design` | full | UI/UX design direction with 5 HTML preview variations, or visual audit. |

## Documentation Skills (Task)

| Skill | Tier | Description |
|-------|------|-------------|
| `docs-write` | full | Create or update formal documents: ADR, RFC, blog, changelog, runbook, API reference, and more. |
| `docs-repo` | full | Generate comprehensive repo documentation using pagesmith conventions. |
| `docs-review` | full | Review documentation for accuracy, completeness, clarity, and style. |
| `docs-crud` | full | Manage doc lifecycle: create, update, improve, respond to comments. |
| `docs-confluence` | full | Confluence-specific read/write with format mapping. |

## Diagram Skills (Task)

| Skill | Tier | Description |
|-------|------|-------------|
| `diagram` | full | Diagram routing — auto-detects the best engine from context and routes to the engine-specific skill. |
| `diagram-mermaid` | full | Mermaid diagrams: full syntax reference for all 21 diagram types. Light/dark mode via diagramkit. |
| `diagram-excalidraw` | full | Excalidraw diagrams: hand-drawn style with complete JSON format reference. |
| `diagram-graphviz` | full | Graphviz DOT diagrams: WASM-based rendering, no browser needed. |
| `diagram-drawio` | full | Draw.io diagrams: precise layout with rich icon library (AWS, Azure, GCP shapes). |

## Quality & Research Skills (Task)

| Skill | Tier | Description |
|-------|------|-------------|
| `audit` | full | Codebase, security, performance, or dependency audit with focus modes. |
| `research` | full | Multi-agent research with citations. Standard (2 agents) or deep (4 agents). |
| `test` | abbreviated | User acceptance testing with interactive verification and failure diagnosis. |

## Project & Session Skills (Task)

| Skill | Tier | Description |
|-------|------|-------------|
| `project` | full | Initialize projects, manage milestones, capture ideas. |
| `handoff` | full | Pause/resume work sessions, context threads. |
| `setup` | abbreviated | Configure CLI tools, MCP servers, and hooks. |
| `deps-tracker` | full | Track upstream dependencies (diagramkit, pagesmith, superpowers) and sync updates. |
| `interactivity` | full | Structured user interaction orchestration: options, data collection, edit/review loops, inline-first with optional external TUI sessions. |

## Routing Skills

| Skill | Tier | Description |
|-------|------|-------------|
| `use` | orchestrator | Default entry point. Expands intent, identifies skills, confirms plan, executes. |
| `team` | full | Multi-model review or agent team dispatch. |
| `code-review` | orchestrator | Code review router: detects type, routes to code-review-pr/repo/fix. |
| `docs` | orchestrator | Documentation router: routes to docs-write/crud/repo/review/confluence. |
| `dev` | orchestrator | Development router: routes to dev-build/refactor/migrate/commit. |
| `diagram` | orchestrator | Diagram router: detects engine, routes to mermaid/excalidraw/drawio/graphviz. |

## Guideline Skills (auto-invoked)

| Skill | Tier | Description |
|-------|------|-------------|
| `workflow` | helper | 6-phase workflow framework with complexity-adaptive skipping. |
| `communication` | helper | Communication style: lead with conclusion, no preamble, concrete specifics. |
| `principal-engineer` | helper | PE questioning framework: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | helper | Child-agent contract and standard team shapes for review, research, docs, security, migration. |
| `output-format` | helper | Verbosity modes (short/standard/detailed), PR comment templates, priority labels. |
| `interaction` | helper | Inline interaction protocols: intent confirm, approach select, plan approve, review findings. |
| `interactivity` | helper | Structured interaction orchestration (inline-first, optional TUI for large forms). |
| `preflight-check` | helper | Preflight validation for dependencies, MCP servers, and tool readiness. |
| `review-standards` | helper | Review pipeline, canonical comment template, source routing, postback rules. |
| `coding` | helper | Detects repo tech stack, loads matching coding guidelines (16 files). |
| `docs-guidelines` | helper | Detects document type, loads matching writing guidelines (24 files). |
| `docs-md` | helper | Detects markdown rendering target and loads formatting guidelines. |
| `architecture` | helper | Architecture patterns, principles, and anti-pattern detection. |

## Connector Skills (auto-invoked)

| Skill | Tier | Description |
|-------|------|-------------|
| `github` | helper | GitHub PR, issue, review, and repo operations via `gh` CLI. |
| `bitbucket` | helper | Bitbucket PR, comment, and repo operations via API. |
| `confluence` | helper | Confluence page, comment, and space operations. |
| `jira` | helper | Jira issue, board, project, and search operations. |

## Self-Sufficient Pattern

Every task skill includes a "Shared Skills" section with a table listing the guideline skills it uses and inline fallback summaries. This means:

- **Full install** (Claude plugin): Task skills invoke guideline skills for rich guidance
- **Partial install** (skills.sh, individual skills): Task skills fall back to the inline summaries
- **No knowledge loss**: The inline summaries contain the essential rules from each guideline skill
