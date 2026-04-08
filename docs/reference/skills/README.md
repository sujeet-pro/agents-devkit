---
title: Skill Reference
description: Complete reference for all 51 ADK skills — parameters, workflows, and examples
order: 1
---

# Skill Reference

Each skill page documents parameters, workflow phases, shared skills, and usage examples. Use `--help` on any skill to see its parameters in the CLI.

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

---

## Orchestrator

| Skill | Description | Reference |
|-------|-------------|-----------|
| [`use`](./use.md) | Default entry point — expands intent, identifies skills, confirms plan, executes | [Details →](./use.md) |

## Review Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`code-review`](./code-review.md) | router | Detects review type, routes to sub-skill | [Details →](./code-review.md) |
| [`code-review-pr`](./code-review-pr.md) | full | PR, local, or branch review with fix/describe/finalize | [Details →](./code-review-pr.md) |
| [`code-review-repo`](./code-review-repo.md) | full | Whole-repository review and improvement plan | [Details →](./code-review-repo.md) |
| [`code-review-fix`](./code-review-fix.md) | full | Fix PR review comments, reply, resolve threads | [Details →](./code-review-fix.md) |

## Development Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`dev`](./dev.md) | router | Detects dev task type, routes to sub-skill | [Details →](./dev.md) |
| [`dev-build`](./dev-build.md) | full | Implement, debug, enhance, TDD, verify, worktree, quick | [Details →](./dev-build.md) |
| [`dev-refactor`](./dev-refactor.md) | full | Extract, rename, restructure, simplify, modernize | [Details →](./dev-refactor.md) |
| [`dev-migrate`](./dev-migrate.md) | full | Framework/library/version migration | [Details →](./dev-migrate.md) |
| [`dev-commit`](./dev-commit.md) | full | Smart commit messages and PR descriptions | [Details →](./dev-commit.md) |

## Documentation Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`docs`](./docs.md) | router | Detects doc task type, routes to sub-skill | [Details →](./docs.md) |
| [`docs-write`](./docs-write.md) | full | Formal engineering documents with optional publishing | [Details →](./docs-write.md) |
| [`docs-crud`](./docs-crud.md) | full | Per-page lifecycle: create, update, improve, comment-reply | [Details →](./docs-crud.md) |
| [`docs-review`](./docs-review.md) | full | Multi-dimensional document quality review | [Details →](./docs-review.md) |
| [`docs-repo`](./docs-repo.md) | full | Repository-wide documentation generation | [Details →](./docs-repo.md) |
| [`docs-confluence`](./docs-confluence.md) | full | Confluence read/write/sync with format mapping | [Details →](./docs-confluence.md) |

## Diagram Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`diagram`](./diagram.md) | router | Auto-detects engine, routes to diagram sub-skill | [Details →](./diagram.md) |
| [`diagram-mermaid`](./diagram-mermaid.md) | full | 21 Mermaid diagram types with diagramkit rendering | [Details →](./diagram-mermaid.md) |
| [`diagram-excalidraw`](./diagram-excalidraw.md) | full | Hand-drawn style with themed palettes | [Details →](./diagram-excalidraw.md) |
| [`diagram-drawio`](./diagram-drawio.md) | full | Precise layout with rich cloud icon library | [Details →](./diagram-drawio.md) |
| [`diagram-graphviz`](./diagram-graphviz.md) | full | DOT graphs with WASM rendering | [Details →](./diagram-graphviz.md) |

## Planning & Research Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`plan`](./plan.md) | full | Brainstorm, write, execute, and track plans | [Details →](./plan.md) |
| [`research`](./research.md) | full | Multi-agent cited research (2 or 4 agents) | [Details →](./research.md) |
| [`spec`](./spec.md) | full | Specifications, analysis, checklists, constitutions | [Details →](./spec.md) |

## Quality & Design Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`audit`](./audit.md) | full | Security, performance, dependency, codebase audits | [Details →](./audit.md) |
| [`design`](./design.md) | full | UI/UX design with 5 HTML preview variations | [Details →](./design.md) |
| [`test`](./test.md) | abbreviated | Interactive user acceptance testing | [Details →](./test.md) |
| [`chart`](./chart.md) | full | Data charts from CSV/JSON (30+ chart types) | [Details →](./chart.md) |

## Project & Session Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`project`](./project.md) | full | Project init, milestones, idea backlog | [Details →](./project.md) |
| [`handoff`](./handoff.md) | full | Session handoff and context threads | [Details →](./handoff.md) |
| [`team`](./team.md) | full | Multi-model and agent team coordination | [Details →](./team.md) |
| [`setup`](./setup.md) | abbreviated | CLI tools, MCP servers, hooks, config | [Details →](./setup.md) |
| [`deps-tracker`](./deps-tracker.md) | full | Upstream dependency tracking and sync | [Details →](./deps-tracker.md) |
| [`interactivity`](./interactivity.md) | full | Structured interaction orchestration (options, forms, review) | [Details →](./interactivity.md) |

---

## Guideline Skills (auto-invoked)

| Skill | Purpose | Reference |
|-------|---------|-----------|
| [`workflow`](./workflow.md) | 6-phase workflow framework with complexity-adaptive skipping | [Details →](./workflow.md) |
| [`communication`](./communication.md) | Communication style: lead with conclusion, no preamble, concrete specifics | [Details →](./communication.md) |
| [`principal-engineer`](./principal-engineer.md) | PE questioning: need? simplest? alternatives? maintenance? clarity? | [Details →](./principal-engineer.md) |
| [`agentic-teams`](./agentic-teams.md) | Child-agent contract and 9 standard team shapes | [Details →](./agentic-teams.md) |
| [`output-format`](./output-format.md) | Verbosity modes, PR comment templates, priority labels | [Details →](./output-format.md) |
| [`interaction`](./interaction.md) | Inline protocols: intent confirm, approach select, plan approve | [Details →](./interaction.md) |
| [`preflight-check`](./preflight-check.md) | Tool dependency and MCP readiness validation | [Details →](./preflight-check.md) |
| [`review-standards`](./review-standards.md) | Review pipeline, comment templates, source routing | [Details →](./review-standards.md) |
| [`coding`](./coding.md) | Detects tech stack, loads matching coding guidelines (16 files) | [Details →](./coding.md) |
| [`architecture`](./architecture.md) | Architecture patterns, principles, and anti-pattern detection | [Details →](./architecture.md) |
| [`docs-guidelines`](./docs-guidelines.md) | Detects document type, loads matching writing guidelines (24 files) | [Details →](./docs-guidelines.md) |
| [`docs-md`](./docs-md.md) | Detects markdown target, loads formatting guidelines | [Details →](./docs-md.md) |
| [`workspace-conventions`](./workspace-conventions.md) | Temp files, diagram output, artifact locations | [Details →](./workspace-conventions.md) |

## Connector Skills (auto-invoked)

| Skill | Purpose | Reference |
|-------|---------|-----------|
| [`github`](./github.md) | GitHub PR, issue, review operations via `gh` CLI | [Details →](./github.md) |
| [`bitbucket`](./bitbucket.md) | Bitbucket PR, comment, repo operations via REST API | [Details →](./bitbucket.md) |
| [`confluence`](./confluence.md) | Confluence page, comment, space operations | [Details →](./confluence.md) |
| [`jira`](./jira.md) | Jira issue, board, project, search operations | [Details →](./jira.md) |

---

## Self-Sufficient Pattern

Every task skill includes inline fallback summaries for all shared knowledge:

- **Full install** (Claude plugin): Task skills invoke guideline skills for rich guidance
- **Partial install** (skills.sh, individual skills): Task skills fall back to inline summaries
- **No knowledge loss**: Inline summaries contain the essential rules from each guideline skill
