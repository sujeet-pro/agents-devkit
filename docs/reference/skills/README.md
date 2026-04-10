---
title: "Skill Reference"
description: "Complete reference for ADK skills — parameters, workflow contracts, and examples sourced from current SKILL.md files"
order: 1
---

# Skill Reference

Every page in this section is derived from the live `SKILL.md` file for that skill. Use the individual reference pages when you want the exact flag surface, workflow contract, helper-skill composition, and output expectations for the current repository state.

## Strategy and Governance

- [Skill Landscape and Gap Analysis](../skill-LANDSCAPE.md)
- [Skill Inspiration Map](../skill-INSPIRATION-MAP.md)
- [Category Routing Map](../skill-CATEGORY-ROUTING.md)

## Common Parameters

Many user-invocable skills expose some combination of the following controls:

| Parameter | What it usually does |
|-----------|----------------------|
| `--help` | Print the embedded skill reference and stop |
| `--verbosity` | Change how much detail the result includes without changing the core task |
| `--auto` | Skip approval pauses while keeping the skill's validation behavior |

## Orchestrator

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`use`](../skill-use.md) | router | Use when starting any task to expand intent, identify the right DevKit skills, confirm the plan early with the user, and then execute the approved workflow | [Details ->](../skill-use.md) |

## Review Skills

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`code-review`](../skill-code-review.md) | router | Code review router — detects review type and routes to the right sub-skill | [Details ->](../skill-code-review.md) |
| [`code-review-pr`](../skill-code-review-pr.md) | full | PR, local, or branch code review — review, fix, describe, finalize with conditional stages | [Details ->](../skill-code-review-pr.md) |
| [`code-review-repo`](../skill-code-review-repo.md) | full | Review an entire repository — architecture, code quality, patterns, tech debt. Prioritized improvement plan | [Details ->](../skill-code-review-repo.md) |
| [`code-review-fix`](../skill-code-review-fix.md) | full | Fix PR review comments — reads comments, applies code fixes, replies to reviewers, marks threads resolved | [Details ->](../skill-code-review-fix.md) |

## Development Skills

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`dev`](../skill-dev.md) | router | Development router — detects dev task type and routes to the right sub-skill | [Details ->](../skill-dev.md) |
| [`dev-build`](../skill-dev-build.md) | full | Implement features, debug, enhance code, or run TDD — auto-detects mode from context | [Details ->](../skill-dev-build.md) |
| [`dev-refactor`](../skill-dev-refactor.md) | full | Refactor code — extract, rename, restructure, simplify, or modernize patterns across files with safe, tested transformations | [Details ->](../skill-dev-refactor.md) |
| [`dev-migrate`](../skill-dev-migrate.md) | full | Migrate frameworks, libraries, or language versions — analyze breaking changes, map to codebase, execute migration plan | [Details ->](../skill-dev-migrate.md) |
| [`dev-commit`](../skill-dev-commit.md) | full | Create commits or PR descriptions — analyzes changes, generates conventional commit messages | [Details ->](../skill-dev-commit.md) |

## Documentation Skills

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`docs`](../skill-docs.md) | router | Documentation router — detects doc task type and routes to the right sub-skill | [Details ->](../skill-docs.md) |
| [`docs-write`](../skill-docs-write.md) | full | Create or update formal engineering documents — auto-detects type, loads the right stage, optional Confluence/Google Docs publishing | [Details ->](../skill-docs-write.md) |
| [`docs-crud`](../skill-docs-crud.md) | full | Manage documentation lifecycle — create, update, improve, respond to comments | [Details ->](../skill-docs-crud.md) |
| [`docs-review`](../skill-docs-review.md) | full | Review documentation — local files, Confluence, or Google Docs. Standard, interactive, and follow-up modes with multi-dimensional analysis | [Details ->](../skill-docs-review.md) |
| [`docs-repo`](../skill-docs-repo.md) | full | Generate comprehensive repository documentation using pagesmith | [Details ->](../skill-docs-repo.md) |
| [`docs-confluence`](../skill-docs-confluence.md) | full | Confluence-specific documentation — read/write Confluence pages with format mapping between Confluence storage format and markdown | [Details ->](../skill-docs-confluence.md) |

## Diagram Skills

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`diagram`](../skill-diagram.md) | router | Diagram router — auto-detects the best engine and routes to the right diagram skill | [Details ->](../skill-diagram.md) |
| [`diagram-mermaid`](../skill-diagram-mermaid.md) | full | Create Mermaid diagrams with full syntax reference for all 21 diagram types. Supports light/dark mode via diagramkit | [Details ->](../skill-diagram-mermaid.md) |
| [`diagram-excalidraw`](../skill-diagram-excalidraw.md) | full | Create Excalidraw diagrams — hand-drawn style architecture overviews and freeform diagrams. Full JSON format reference with light/dark mode | [Details ->](../skill-diagram-excalidraw.md) |
| [`diagram-drawio`](../skill-diagram-drawio.md) | full | Create draw.io diagrams — precise layout with rich icon library for network topology, enterprise architecture, and BPMN | [Details ->](../skill-diagram-drawio.md) |
| [`diagram-graphviz`](../skill-diagram-graphviz.md) | full | Create Graphviz DOT diagrams — strict layout for dependency graphs and existing .dot assets. WASM-based rendering, no browser needed | [Details ->](../skill-diagram-graphviz.md) |

## Planning & Research Skills

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`plan`](../skill-plan.md) | full | Use when brainstorming, approving, executing, or tracking implementation plans with explicit human checkpoints before execution | [Details ->](../skill-plan.md) |
| [`research`](../skill-research.md) | full | Use when you need to research a software engineering topic — searches official sources, implementations, and community patterns, then produces structured markdown with citations | [Details ->](../skill-research.md) |
| [`spec`](../skill-spec.md) | full | Use when analyzing specs, writing specifications, generating checklists, or writing constitutions | [Details ->](../skill-spec.md) |

## Quality & Design Skills

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`audit`](../skill-audit.md) | full | Use when performing a codebase, security, performance, or dependency audit -- auto-detects focus or use --focus to specify | [Details ->](../skill-audit.md) |
| [`design`](../skill-design.md) | full | Use when designing frontend UI/UX, auditing visual design, or creating design direction | [Details ->](../skill-design.md) |
| [`test`](../skill-test.md) | abbreviated | Use when you need interactive user acceptance testing that extracts testable deliverables and walks the user through manual verification with automatic failure diagnosis | [Details ->](../skill-test.md) |
| [`chart`](../skill-chart.md) | full | Create data charts — bar, line, pie, scatter, area, and 30+ chart types from CSV/JSON data. CLI-based SVG/PNG rendering | [Details ->](../skill-chart.md) |

## Project & Session Skills

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`project`](../skill-project.md) | full | Use when initializing projects, managing milestones, or capturing ideas | [Details ->](../skill-project.md) |
| [`handoff`](../skill-handoff.md) | full | Use when handing off sessions or managing persistent context threads | [Details ->](../skill-handoff.md) |
| [`team`](../skill-team.md) | full | Use when dispatching multi-model tasks or coordinating agent teams | [Details ->](../skill-team.md) |
| [`setup`](../skill-setup.md) | abbreviated | Use when setting up, validating, or updating CLI tools and MCP server configurations for DevKit skills | [Details ->](../skill-setup.md) |
| [`deps-tracker`](../skill-deps-tracker.md) | full | Track upstream dependencies and inspirations for ADK skills. Detect changes in referenced tools/libraries and update skills accordingly | [Details ->](../skill-deps-tracker.md) |
| [`interactivity`](../skill-interactivity.md) | full | Agent-first interaction orchestration for option selection, data capture, edits, and human approval | [Details ->](../skill-interactivity.md) |
| [`create-skill`](../skill-create-skill.md) | abbreviated | Scaffold a new ADK skill — generates directory structure, SKILL.md with proper frontmatter, preflight script, and runs propagation | [Details ->](../skill-create-skill.md) |

## Guideline Skills

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`workflow`](../skill-workflow.md) | helper | Helper skill providing 4 workflow families — Quick Action, Standard Task, Complex Build, Investigative Loop. Invoked by all task skills with --family flag | [Details ->](../skill-workflow.md) |
| [`communication`](../skill-communication.md) | helper | Communication style rules for all DevKit output. Lead with conclusions, use concrete specifics, avoid preamble | [Details ->](../skill-communication.md) |
| [`principal-engineer`](../skill-principal-engineer.md) | helper | Principal Engineer questioning framework applied before committing to significant work. Five questions: need, simplest, alternatives, maintenance, clarity | [Details ->](../skill-principal-engineer.md) |
| [`agentic-teams`](../skill-agentic-teams.md) | helper | Child-agent contract for parallel agentic teams. Standard team shapes for review, research, docs, diagrams, security, migration, planning | [Details ->](../skill-agentic-teams.md) |
| [`output-format`](../skill-output-format.md) | helper | Output format standards: verbosity modes (short/standard/detailed), PR comment templates, document templates, priority labels, and cross-platform markdown rules | [Details ->](../skill-output-format.md) |
| [`interaction`](../skill-interaction.md) | helper | Inline interaction protocols for intent confirmation, approach selection, plan approval, review findings, and progress dashboards | [Details ->](../skill-interaction.md) |
| [`preflight-check`](../skill-preflight-check.md) | helper | Preflight validation for dependencies, MCP servers, and tool readiness. Run before launching child agents, reviews, or publishing | [Details ->](../skill-preflight-check.md) |
| [`review-standards`](../skill-review-standards.md) | helper | Review pipeline, source routing, and comment template standards for all review-oriented skills | [Details ->](../skill-review-standards.md) |
| [`coding`](../skill-coding.md) | helper | Helper skill that detects repo tools, frameworks, and languages, then loads matching coding guidelines from the shared guideline library — invoked by review, PR, and development skills, not directly by users | [Details ->](../skill-coding.md) |
| [`docs-guidelines`](../skill-docs-guidelines.md) | helper | Detects the document type being written and loads matching document guidelines — invoked by docs-write and docs-review | [Details ->](../skill-docs-guidelines.md) |
| [`docs-md`](../skill-docs-md.md) | helper | Markdown feature detection and formatting guidelines — pagesmith, GitHub, and plain markdown | [Details ->](../skill-docs-md.md) |
| [`architecture`](../skill-architecture.md) | helper | Helper skill that provides software architecture patterns, principles, and review criteria. Used by review, audit, and design skills | [Details ->](../skill-architecture.md) |
| [`workspace-conventions`](../skill-workspace-conventions.md) | helper | Workspace file conventions — temp files, diagram output, artifact locations, and .gitignore management | [Details ->](../skill-workspace-conventions.md) |

## Connector Skills

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`github`](../skill-github.md) | helper | GitHub operations via gh CLI — PR reviews, comments, issues, and repository access | [Details ->](../skill-github.md) |
| [`bitbucket`](../skill-bitbucket.md) | helper | Bitbucket REST API operations — PR reviews, comments, repository access, and pipeline status | [Details ->](../skill-bitbucket.md) |
| [`confluence`](../skill-confluence.md) | helper | Confluence REST API operations — page CRUD, comments, attachments, and space management | [Details ->](../skill-confluence.md) |
| [`jira`](../skill-jira.md) | helper | Jira REST API operations — issue management, comments, search, projects, boards, and sprints | [Details ->](../skill-jira.md) |

## Self-Sufficient Pattern

Task skills are designed to stay usable even in partial installations. They prefer shared helper skills when those helpers are available, but the inline fallback summaries inside each `SKILL.md` preserve the critical rules for workflow, communication, formatting, and validation.
