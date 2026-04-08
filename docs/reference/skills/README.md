---
title: Skill Reference
description: Complete reference for all 52 ADK skills — parameters, workflows, and examples
order: 1
---

# Skill Reference

Each skill page is a comprehensive reference covering what the skill does, all parameters with types and defaults, behavior variations, priorities, workflow phases, shared skills with load conditions and fallbacks, output format, adjacent skills, and usage examples. Use `--help` on any skill to see its parameters in the CLI.

## Strategy and Governance

- [Skill Landscape and Gap Analysis](../skill-LANDSCAPE.md)
- [Skill Inspiration Map](../skill-INSPIRATION-MAP.md)
- [Category Routing Map](../skill-CATEGORY-ROUTING.md)

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
| [`use`](../skill-use.md) | Default entry point — expands intent, identifies skills, confirms plan, executes | [Details →](../skill-use.md) |

## Review Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`code-review`](../skill-code-review.md) | router | Detects review type, routes to sub-skill | [Details →](../skill-code-review.md) |
| [`code-review-pr`](../skill-code-review-pr.md) | full | PR, local, or branch review with fix/describe/finalize | [Details →](../skill-code-review-pr.md) |
| [`code-review-repo`](../skill-code-review-repo.md) | full | Whole-repository review and improvement plan | [Details →](../skill-code-review-repo.md) |
| [`code-review-fix`](../skill-code-review-fix.md) | full | Fix PR review comments, reply, resolve threads | [Details →](../skill-code-review-fix.md) |

## Development Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`dev`](../skill-dev.md) | router | Detects dev task type, routes to sub-skill | [Details →](../skill-dev.md) |
| [`dev-build`](../skill-dev-build.md) | full | Implement, debug, enhance, TDD, verify, worktree, quick | [Details →](../skill-dev-build.md) |
| [`dev-refactor`](../skill-dev-refactor.md) | full | Extract, rename, restructure, simplify, modernize | [Details →](../skill-dev-refactor.md) |
| [`dev-migrate`](../skill-dev-migrate.md) | full | Framework/library/version migration | [Details →](../skill-dev-migrate.md) |
| [`dev-commit`](../skill-dev-commit.md) | full | Smart commit messages and PR descriptions | [Details →](../skill-dev-commit.md) |

## Documentation Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`docs`](../skill-docs.md) | router | Detects doc task type, routes to sub-skill | [Details →](../skill-docs.md) |
| [`docs-write`](../skill-docs-write.md) | full | Formal engineering documents with optional publishing | [Details →](../skill-docs-write.md) |
| [`docs-crud`](../skill-docs-crud.md) | full | Per-page lifecycle: create, update, improve, comment-reply | [Details →](../skill-docs-crud.md) |
| [`docs-review`](../skill-docs-review.md) | full | Multi-dimensional document quality review | [Details →](../skill-docs-review.md) |
| [`docs-repo`](../skill-docs-repo.md) | full | Repository-wide documentation generation | [Details →](../skill-docs-repo.md) |
| [`docs-confluence`](../skill-docs-confluence.md) | full | Confluence read/write/sync with format mapping | [Details →](../skill-docs-confluence.md) |

## Diagram Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`diagram`](../skill-diagram.md) | router | Auto-detects engine, routes to diagram sub-skill | [Details →](../skill-diagram.md) |
| [`diagram-mermaid`](../skill-diagram-mermaid.md) | full | 21 Mermaid diagram types with diagramkit rendering | [Details →](../skill-diagram-mermaid.md) |
| [`diagram-excalidraw`](../skill-diagram-excalidraw.md) | full | Hand-drawn style with themed palettes | [Details →](../skill-diagram-excalidraw.md) |
| [`diagram-drawio`](../skill-diagram-drawio.md) | full | Precise layout with rich cloud icon library | [Details →](../skill-diagram-drawio.md) |
| [`diagram-graphviz`](../skill-diagram-graphviz.md) | full | DOT graphs with WASM rendering | [Details →](../skill-diagram-graphviz.md) |

## Planning & Research Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`plan`](../skill-plan.md) | full | Brainstorm, write, execute, and track plans | [Details →](../skill-plan.md) |
| [`research`](../skill-research.md) | full | Multi-agent cited research (2 or 4 agents) | [Details →](../skill-research.md) |
| [`spec`](../skill-spec.md) | full | Specifications, analysis, checklists, constitutions | [Details →](../skill-spec.md) |

## Quality & Design Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`audit`](../skill-audit.md) | full | Security, performance, dependency, codebase audits | [Details →](../skill-audit.md) |
| [`design`](../skill-design.md) | full | UI/UX design with 5 HTML preview variations | [Details →](../skill-design.md) |
| [`test`](../skill-test.md) | abbreviated | Interactive user acceptance testing | [Details →](../skill-test.md) |
| [`chart`](../skill-chart.md) | full | Data charts from CSV/JSON (30+ chart types) | [Details →](../skill-chart.md) |

## Project & Session Skills (Task)

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`project`](../skill-project.md) | full | Project init, milestones, idea backlog | [Details →](../skill-project.md) |
| [`handoff`](../skill-handoff.md) | full | Session handoff and context threads | [Details →](../skill-handoff.md) |
| [`team`](../skill-team.md) | full | Multi-model and agent team coordination | [Details →](../skill-team.md) |
| [`setup`](../skill-setup.md) | abbreviated | CLI tools, MCP servers, hooks, config | [Details →](../skill-setup.md) |
| [`deps-tracker`](../skill-deps-tracker.md) | full | Upstream dependency tracking and sync | [Details →](../skill-deps-tracker.md) |
| [`interactivity`](../skill-interactivity.md) | full | Structured interaction orchestration (options, forms, review) | [Details →](../skill-interactivity.md) |
| [`create-skill`](../skill-create-skill.md) | abbreviated | Scaffold a new ADK skill with structure and frontmatter | [Details →](../skill-create-skill.md) |

---

## Guideline Skills (auto-invoked)

| Skill | Purpose | Reference |
|-------|---------|-----------|
| [`workflow`](../skill-workflow.md) | 6-phase workflow framework with complexity-adaptive skipping | [Details →](../skill-workflow.md) |
| [`communication`](../skill-communication.md) | Communication style: lead with conclusion, no preamble, concrete specifics | [Details →](../skill-communication.md) |
| [`principal-engineer`](../skill-principal-engineer.md) | PE questioning: need? simplest? alternatives? maintenance? clarity? | [Details →](../skill-principal-engineer.md) |
| [`agentic-teams`](../skill-agentic-teams.md) | Child-agent contract and 9 standard team shapes | [Details →](../skill-agentic-teams.md) |
| [`output-format`](../skill-output-format.md) | Verbosity modes, PR comment templates, priority labels | [Details →](../skill-output-format.md) |
| [`interaction`](../skill-interaction.md) | Inline protocols: intent confirm, approach select, plan approve | [Details →](../skill-interaction.md) |
| [`preflight-check`](../skill-preflight-check.md) | Tool dependency and MCP readiness validation | [Details →](../skill-preflight-check.md) |
| [`review-standards`](../skill-review-standards.md) | Review pipeline, comment templates, source routing | [Details →](../skill-review-standards.md) |
| [`coding`](../skill-coding.md) | Detects tech stack, loads matching coding guidelines (16 files) | [Details →](../skill-coding.md) |
| [`architecture`](../skill-architecture.md) | Architecture patterns, principles, and anti-pattern detection | [Details →](../skill-architecture.md) |
| [`docs-guidelines`](../skill-docs-guidelines.md) | Detects document type, loads matching writing guidelines (24 files) | [Details →](../skill-docs-guidelines.md) |
| [`docs-md`](../skill-docs-md.md) | Detects markdown target, loads formatting guidelines | [Details →](../skill-docs-md.md) |
| [`workspace-conventions`](../skill-workspace-conventions.md) | Temp files, diagram output, artifact locations | [Details →](../skill-workspace-conventions.md) |

## Connector Skills (auto-invoked)

| Skill | Purpose | Reference |
|-------|---------|-----------|
| [`github`](../skill-github.md) | GitHub PR, issue, review operations via `gh` CLI | [Details →](../skill-github.md) |
| [`bitbucket`](../skill-bitbucket.md) | Bitbucket PR, comment, repo operations via REST API | [Details →](../skill-bitbucket.md) |
| [`confluence`](../skill-confluence.md) | Confluence page, comment, space operations | [Details →](../skill-confluence.md) |
| [`jira`](../skill-jira.md) | Jira issue, board, project, search operations | [Details →](../skill-jira.md) |

---

## Self-Sufficient Pattern

Every task skill includes inline fallback summaries for all shared knowledge:

- **Full install** (Claude plugin): Task skills invoke guideline skills for rich guidance
- **Partial install** (skills.sh, individual skills): Task skills fall back to inline summaries
- **No knowledge loss**: Inline summaries contain the essential rules from each guideline skill
