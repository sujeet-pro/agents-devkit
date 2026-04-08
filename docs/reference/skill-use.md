---
title: "use"
description: Orchestrator that expands intent, identifies skills, confirms the plan, and executes the approved workflow
skill_name: use
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# use

Default entry point for DevKit. Expands the user's intent, identifies the right skills, confirms the plan early, and then executes the approved workflow. Start here unless the user explicitly names a specific skill and clearly wants to bypass routing.

## When to Use

- Starting any DevKit task without knowing which skill to invoke
- General prompts that need routing to the right skill(s)
- Multi-skill workflows that require orchestration
- When you want intent expansion and plan approval before execution

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<task description>` | free-text | required | Describe what you want to accomplish |
| `--auto` | flag | off | Skip confirmations at intent, approach, and plan gates (for scripted/CI usage) |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level for all downstream skills |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Trivial tasks** | Inline intent confirmation, abbreviated plan, direct execution, quick validation |
| **Small tasks** | Inline or lightweight confirmation, light research, brief plan approval, execution, verification |
| **Medium tasks** | Full intent review, research/options, interactive approach selection, approved implementation plan, tracked execution |
| **Large tasks** | Same as medium plus Principal Engineer check, stronger questioning, phased execution, and progress dashboard |
| **Explicit skill invocation** | Keeps that skill in the pipeline, but still runs Phase 0 and plan-before-execute |
| **`--auto`** | Skips user confirmations at intent, approach, and plan gates — executes directly |

## Routing Logic

The orchestrator uses Phase 0 (Intent Expansion) to analyze the user's prompt and route to the appropriate skill(s). It picks the smallest useful pipeline that covers the confirmed intent.

### Detection Signals

| User says... | Route to |
|---|---|
| "review this PR" / "review my changes" | `/adk:code-review-pr` |
| "review this repo" / "audit the codebase" | `/adk:code-review-repo` |
| "fix the PR comments" / "address review feedback" | `/adk:code-review-fix` |
| "implement" / "build" / "add feature" / "fix bug" | `/adk:dev-build` |
| "refactor" / "extract" / "rename across" / "restructure" | `/adk:dev-refactor` |
| "migrate" / "upgrade from X to Y" / "migration" | `/adk:dev-migrate` |
| "commit" / "commit message" / "PR description" | `/adk:dev-commit` |
| "write an ADR" / "write a blog post" / "changelog" | `/adk:docs-write` |
| "plan" / "brainstorm" / "design a solution" | `/adk:plan` |
| "spec" / "requirements" / "checklist" | `/adk:spec` |
| "research" / "compare" / "investigate" | `/adk:research` |
| "diagram" / "visualize" / "flowchart" | `/adk:diagram` |
| "mermaid diagram" / "sequence diagram" | `/adk:diagram-mermaid` |
| "excalidraw" / "architecture overview diagram" | `/adk:diagram-excalidraw` |
| "graphviz" / "dot graph" | `/adk:diagram-graphviz` |
| "draw.io" / "network topology" | `/adk:diagram-drawio` |
| "chart" / "graph data" / "bar chart" / "pie chart" / "line chart" | `/adk:chart` |
| "design" / "UI" / "mockup" | `/adk:design` |
| "audit" / "security review" / "performance review" | `/adk:audit` |
| "review this doc" / "review the RFC" | `/adk:docs-review` |
| "generate docs" / "document this repo" | `/adk:docs-repo` |
| "review the docs" / "check documentation" | `/adk:docs-review` |
| "update the docs" / "fix this doc" / "respond to doc comments" | `/adk:docs-crud` |
| "create TDD" / "create HLD" / "create LLD" / "create PRD" / "create ERD" | `/adk:docs-crud` |
| "test" / "acceptance test" / "verify" | `/adk:test` |
| "new project" / "init" / "milestone" | `/adk:project` |
| "handoff" / "save session" / "resume" | `/adk:handoff` |
| "setup" / "configure" / "install tools" | `/adk:setup` |
| "check upstream" / "sync dependencies" | `/adk:deps-tracker` |
| "run interactive workflow" / "structured user Q&A" | `/adk:interactivity` |
| "multi-model" / "team review" / "agent team" | `/adk:team` |
| "review" / "code review" (no specific target) | `/adk:code-review` |
| "docs" / "documentation" (no specific target) | `/adk:docs` |
| "dev" / "develop" (no specific target) | `/adk:dev` |
| "Confluence page" / "publish to Confluence" | `/adk:docs-confluence` |

### Downstream Skills

#### Task Skills

| Skill | Area | Description |
|-------|------|-------------|
| `code-review-pr` | Review | PR, local, or branch code review + fix/describe/finalize |
| `code-review-repo` | Review | Whole-repo review with improvement plan |
| `code-review-fix` | Review | Fix PR comments, reply, mark resolved |
| `docs-review` | Review | Review documents for accuracy and completeness |
| `dev-build` | Dev | Implement features, fix bugs, enhance code, TDD |
| `dev-refactor` | Dev | Extract, rename, restructure, simplify, modernize |
| `dev-migrate` | Dev | Framework/library migration with breaking change analysis |
| `dev-commit` | Dev | Smart commit messages and PR descriptions |
| `docs-write` | Docs | Create/update formal documents (ADR, RFC, blog, changelog) |
| `docs-repo` | Docs | Generate comprehensive repo documentation |
| `docs-crud` | Docs | Manage documentation lifecycle |
| `docs-confluence` | Docs | Confluence-specific read/write with format mapping |
| `plan` | Plan | Brainstorm, write, execute, and track plans |
| `spec` | Spec | Write specs, analyze consistency, generate checklists |
| `research` | Research | Multi-agent research with citations |
| `diagram-mermaid` | Diagram | Mermaid diagrams with full syntax reference |
| `diagram-excalidraw` | Diagram | Excalidraw hand-drawn style diagrams |
| `diagram-graphviz` | Diagram | Graphviz DOT diagrams |
| `diagram-drawio` | Diagram | Draw.io precise layout diagrams |
| `chart` | Data Viz | Data charts from CSV/JSON |
| `design` | Design | UI/UX design direction + visual audit |
| `audit` | Quality | Codebase, security, performance, dependency audit |
| `test` | QA | User acceptance testing |
| `project` | Project | Initialize projects, manage milestones |
| `handoff` | Session | Pause/resume work sessions |
| `setup` | Setup | Configure CLI tools and MCP servers |
| `deps-tracker` | Project | Track upstream dependencies |
| `interactivity` | Interaction | Structured user interaction orchestration |

#### Routing Skills

| Skill | Description |
|-------|-------------|
| `team` | Multi-model review, agent team dispatch |
| `code-review` | Code review router: detects type, routes to code-review-pr/repo/fix |
| `docs` | Documentation router: detects task, routes to docs-write/crud/repo/review/confluence |
| `dev` | Development router: detects task, routes to dev-build/refactor/migrate/commit |
| `diagram` | Diagram router: detects engine, routes to diagram-mermaid/excalidraw/drawio/graphviz |

#### Guideline Skills (auto-invoked by task skills)

| Skill | Description |
|-------|-------------|
| `workflow` | 6-phase workflow framework with complexity-adaptive skipping |
| `communication` | Communication style: lead with conclusion, no preamble, concrete specifics |
| `principal-engineer` | PE questioning: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | Child-agent contract and standard team shapes |
| `output-format` | Verbosity modes, PR comment templates, priority labels |
| `interaction` | Inline protocols for intent confirm, approach select, plan approve |
| `preflight-check` | Preflight validation for dependencies, MCP, and tools |
| `review-standards` | Review pipeline, comment template, source routing |
| `coding` | Detects repo stack, loads coding guidelines |
| `docs-guidelines` | Detects doc type, loads writing guidelines |
| `docs-md` | Detects markdown target, loads formatting guidelines |
| `architecture` | Architecture patterns, principles, and anti-pattern detection |
| `workspace-conventions` | File placement conventions: temp in `.temp/`, diagrams in `diagrams/` |

## Core Rules

1. Run Phase 0 (Intent Expansion) before selecting the final pipeline
2. Make reasoning visible but concise and decision-oriented
3. For Medium and Large work, challenge the approach with Principal Engineer questions
4. The user must approve the direction before execution starts (unless `--auto`)
5. Execution starts only after an approved plan exists for non-trivial work
6. Every downstream skill invocation must be explainable from the confirmed intent
7. Concise by default: show compact result first, offer detailed breakdown on request

## Workflow

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | always | Expand prompt, detect skills, estimate complexity, produce Phase Summary Card |
| 1. Research & Options | medium+ | Research enough to present 2-3 viable options |
| 2. Approach Selection | medium+ | Present approaches, let user pick/mix/simplify |
| 3. Planning | non-trivial | Draft plan, review with `adk-plan-reviewer`, get user approval |
| 4. Execute | after approval | Invoke downstream skills, use parallel agents when possible |
| 5. Validate & Learn | always | Compact summary with result, verification, changes, and key insight |

### Phase Summary Card

Every prompt produces a Phase Summary Card as the first thing the user sees:

```text
## Phase Summary

**Goal**: <one-line restatement>

**Skills**: <skill-1> → <skill-2> → <skill-3>
**Phases**: 0 intent → 1 research → 3 plan → 4 execute → 5 validate
**Complexity**: <level> — <one-line rationale>

| Phase | Action | Status |
|-------|--------|--------|
| 0. Intent | Expand and confirm | pending |
| 1. Research | <what will be researched> | skip/pending |
| 2. Approach | <selection method> | skip/pending |
| 3. Plan | <planning scope> | skip/pending |
| 4. Execute | <what gets executed> | pending |
| 5. Validate | <validation method> | pending |

> approve · edit · simplify · cancel
```

## Shared Skills

| Skill | Invoked | Fallback |
|-------|---------|----------|
| `workflow` | always | 6-phase workflow with complexity-adaptive skipping |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py for tool and MCP validation |
| `output-format` | producing output | short/standard/detailed verbosity; markdown default |
| `principal-engineer` | medium/large | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | medium/large | Launch 2+ child agents with distinct roles |
| `interaction` | interactive phases | Inline protocols for confirmations and approvals |

## Output Format

Concise by default. All output is markdown.

- **short**: one-line summary + next action
- **standard**: Phase Summary Card, approved pipeline, compact progress, outcome with "need details?" offer
- **detailed**: standard output plus decision notes, artifact paths, and full reasoning

### Done Summary

```text
## Done

**Result**: <one-line outcome>
**Verified**: <what was validated>
**Changed**: <what diverged from the plan, if anything>
**Key insight**: <one sentence the user should remember>

Need a detailed breakdown?
```

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:plan` | User explicitly asks to brainstorm, write, execute, or track a plan |
| `/adk:team` | User explicitly wants multi-model or multi-agent orchestration as the primary task |

## Examples

```
/adk:use review this PR: https://github.com/org/repo/pull/42
/adk:use implement user authentication with OAuth2
/adk:use write an ADR for our caching strategy
/adk:use debug the failing CI pipeline
/adk:use audit this codebase for security and performance
/adk:use generate docs for this repo
/adk:use create a mermaid sequence diagram for the auth flow
/adk:use review this repo for architecture issues
/adk:use fix the PR comments on #42
```
