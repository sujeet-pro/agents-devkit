---
title: 'use'
description: 'Use when starting any task to expand intent, identify the right DevKit skills, confirm the plan early with the user, and then execute the approved workflow'
skill_name: use
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# use

Use `use` when you want DevKit to route pipeline work to the right downstream skill. Its job is classification and parameter forwarding, not doing the downstream work itself.

## Overview

`use` belongs to the `routing` layer and is declared at the `orchestrator` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<task description>` | free-text | required | Describe what you want to accomplish |
| `--auto` | flag | off | Skip confirmations (for scripted/CI usage) |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level for all downstream skills |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.

## How It Works

Routing begins by resolving intent. Explicit override flags take priority; otherwise the detection rules below choose a downstream skill, stage, or engine based on the prompt and repository context.

Once the route is fixed, the router keeps parameter forwarding narrow and predictable so the downstream skill receives the same important selectors the user provided.

### Shared Skills

The orchestrator invokes these shared skills and passes their guidance to downstream skills. When a shared skill is not installed, the orchestrator uses the inline summary.

| Skill | Invoked | Inline Fallback |
|-------|---------|-----------------|
| `/adk:workflow` | always, routes to target skill's family | Workflow families: Quick Action (confirm → execute → verify), Standard Task (confirm → research → execute → validate), Complex Build (full 6-step with approach selection and planning), Investigative Loop (iterative discovery). Each skill declares its family. `--auto` bypasses confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Markdown default. |
| `/adk:principal-engineer` | medium/large | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | medium/large | Launch 2+ child agents with distinct roles for the task type. |
| `/adk:interaction` | interactive phases | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |

### Workflow

The orchestrator follows: **prompt → prompt expansion (scoping) → skill identification → multi-skill/agent execution → validation**.

All skills follow a **human-in-the-loop** and **plan-first** approach:
- The user approves direction before execution starts
- Non-trivial work requires an approved plan
- Auto mode (`--auto`) skips confirmations for scripted or CI usage

This skill must make the workflow human-in-the-loop as early as possible:

1. expand the user's intent before doing real work
2. show concise visible reasoning
3. identify skills, scripts, tools, and MCPs
4. confirm the approach and plan with the user
5. use multiple skills and agents to perform the task following the approved plan
6. validate and summarize

### Execution

Once the user approves the plan (or `--auto` is set):

1. invoke the selected downstream skills in order
2. use multiple agents when tasks are parallelizable
3. keep progress visible at natural checkpoints
4. avoid asking for more information unless the approved assumptions are broken by reality
5. for Medium and Large execution, write progress updates and show inline progress per `/adk:interaction`

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **Trivial tasks**: inline intent confirmation, abbreviated plan, direct execution, quick validation
- **Small tasks**: inline or lightweight confirmation, light research, brief plan approval, execution, verification
- **Medium tasks**: full intent review, research/options, interactive approach selection, approved implementation plan, tracked execution
- **Large tasks**: same as medium plus Principal Engineer check, stronger questioning, phased execution, and progress dashboard
- **Explicit skill invocation by the user**: keep that skill in the pipeline, but still run Phase 0 and plan-before-execute
- **`--auto`**: skip user confirmations at intent, approach, and plan gates — execute directly

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

**Concise by default.** Adapt output to `--verbosity`:

- **short**: one-line summary + next action
- **standard** (default): phase summary card, approved pipeline, compact progress, outcome with "need details?" offer
- **detailed**: standard output plus decision notes, artifact paths, and full reasoning

When `--verbosity` is not set, use **standard** — show the compact version and offer to elaborate.

## Related Skills

### Adjacent Skills

- `/adk:plan` — use directly when the user explicitly asks to brainstorm, write, execute, or track a plan
- `/adk:team` — use when the user explicitly wants multi-model or multi-agent orchestration as the primary task

## Additional Reference

### Skill Routing Table

### Task Skills

| Skill | Area | Invocation | Description |
|-------|------|------------|-------------|
| code-review-pr | Review | `/adk:code-review-pr` | Code review: PR, local, branch + fix/comment |
| code-review-repo | Review | `/adk:code-review-repo` | Whole-repo review with improvement plan |
| code-review-fix | Review | `/adk:code-review-fix` | Fix PR comments, reply, mark resolved |
| docs-review | Review | `/adk:docs-review` | Review documents (local, Confluence, Google Docs, in-repo) for accuracy and completeness |
| dev-build | Dev | `/adk:dev-build` | Implement features, fix bugs, enhance code, TDD |
| dev-refactor | Dev | `/adk:dev-refactor` | Extract, rename, restructure, simplify, modernize code |
| dev-migrate | Dev | `/adk:dev-migrate` | Framework/library migration with breaking change analysis |
| dev-commit | Dev | `/adk:dev-commit` | Smart commit messages and PR descriptions |
| docs-write | Docs | `/adk:docs-write` | Create/update formal documents (ADR, RFC, blog, changelog) |
| docs-repo | Docs | `/adk:docs-repo` | Generate comprehensive repo documentation |
| docs-crud | Docs | `/adk:docs-crud` | Manage documentation lifecycle (create/update/improve) |
| docs-confluence | Docs | `/adk:docs-confluence` | Confluence-specific doc read/write with format mapping |
| plan | Plan | `/adk:plan` | Brainstorm, write, execute, and track plans |
| spec | Spec | `/adk:spec` | Write specs, analyze consistency, generate checklists |
| research | Research | `/adk:research` | Multi-agent research with citations |
| diagram-mermaid | Diagram | `/adk:diagram-mermaid` | Mermaid diagrams with full syntax reference |
| diagram-excalidraw | Diagram | `/adk:diagram-excalidraw` | Excalidraw hand-drawn style diagrams |
| diagram-graphviz | Diagram | `/adk:diagram-graphviz` | Graphviz DOT diagrams |
| diagram-drawio | Diagram | `/adk:diagram-drawio` | Draw.io precise layout diagrams |
| design | Design | `/adk:design` | UI/UX design direction + visual audit |
| audit | Quality | `/adk:audit` | Audit: codebase, security, performance, dependencies |
| test | QA | `/adk:test` | User acceptance testing |
| project | Project | `/adk:project` | Initialize projects, manage milestones and ideas |
| handoff | Session | `/adk:handoff` | Pause/resume work sessions |
| setup | Setup | `/adk:setup` | Configure CLI tools and MCP servers |
| deps-tracker | Project | `/adk:deps-tracker` | Track upstream dependencies and sync |
| interactivity | Interaction | `/adk:interactivity` | Structured user interaction orchestration (inline, agent-first) |
| chart | Data Viz | `/adk:chart` | Create data charts (bar, line, pie, scatter, area, 30+ types) from CSV/JSON |
| team | Team | `/adk:team` | Multi-model review, agent team dispatch |

### Routing Skills

| Skill | Invocation | Description |
|-------|------------|-------------|
| use | `/adk:use` | Orchestrator: expand intent, confirm route, execute |
| code-review | `/adk:code-review` | Code review router: detects type, routes to code-review-pr/repo/fix |
| docs | `/adk:docs` | Documentation router: detects task, routes to docs-write/crud/repo/review/confluence |
| dev | `/adk:dev` | Development router: detects task, routes to dev-build/refactor/migrate/commit |
| diagram | `/adk:diagram` | Diagram router: detects engine, routes to diagram-mermaid/excalidraw/drawio/graphviz |

### Guideline Skills (auto-invoked by task skills)

| Skill | Invocation | Description |
|-------|------------|-------------|
| workflow | `/adk:workflow` | Workflow families (quick-action, standard-task, complex-build, investigative-loop) with complexity scaling |
| communication | `/adk:communication` | Communication style: lead with conclusion, no preamble, concrete specifics |
| principal-engineer | `/adk:principal-engineer` | PE questioning: need? simplest? alternatives? maintenance? clarity? |
| agentic-teams | `/adk:agentic-teams` | Child-agent contract and standard team shapes |
| output-format | `/adk:output-format` | Verbosity modes, PR comment templates, priority labels |
| interaction | `/adk:interaction` | Inline protocols for intent confirm, approach select, plan approve |
| preflight-check | `/adk:preflight-check` | Preflight validation for dependencies, MCP, and tools |
| review-standards | `/adk:review-standards` | Review pipeline, comment template, source routing |
| coding | `/adk:coding` | Detects repo stack, loads coding guidelines |
| docs-guidelines | `/adk:docs-guidelines` | Detects doc type, loads writing guidelines |
| docs-md | `/adk:docs-md` | Detects markdown target, loads formatting guidelines |
| architecture | `/adk:architecture` | Architecture patterns, principles, and anti-pattern detection |
| workspace-conventions | `/adk:workspace-conventions` | Where to create files: temp in `.temp/`, diagrams in `diagrams/`, respect `diagramkit.config.json`, light+dark output |

### Core Rules

1. Run **Phase 0: Intent Expansion** before selecting the final pipeline.
2. Make reasoning visible, but concise and decision-oriented.
   Never dump hidden chain-of-thought or a long internal monologue.
3. For Medium and Large work, challenge the approach like a Principal Engineer:
   do we need this, what is the simplest version, what are the alternatives, and what is the maintenance cost?
4. The user must approve the direction before execution starts (unless `--auto`).
5. For non-trivial work, execution starts only after an approved plan exists.
6. Every downstream skill invocation must be explainable from the confirmed intent.
7. **Concise by default**: show the compact result first. After task completion, offer "Need a detailed breakdown?" — elaborate only when the user says yes.

### Phase 0: Intent Expansion

Start by expanding the prompt using `references/intent-expansion.md`.

For Medium and Large work, invoke the **adk-intent-analyst** agent to pressure-test the prompt expansion before presenting it to the user.

### What to Produce — Phase Summary Card

On **every prompt**, produce a compact phase summary card that the user sees immediately. This is the first thing the user reads before any work happens:

```text

### Phase Summary

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

The phase summary card must include:

- one-line goal
- skills pipeline (this skill pack + any other installed skills detected)
- which phases will run vs skip (based on complexity)
- complexity level with rationale
- PE check for Medium or Large work

### Confirmation

- **Trivial / Small**: inline phase summary card is enough
- **Medium / Large**: write `intent.json` to `.temp/<task-slug>/`, then show the phase summary card and wait for approve/edit/simplify/cancel
- **`--auto`**: skip confirmation, proceed directly

If the user simplifies or edits the intent, re-run the expansion and only then continue.

### Platform-Specific Tool Mapping

Detect the agent platform and load the appropriate tool mapping:

- **Codex**: load `references/codex-tools.md` — maps Claude tool names to Codex equivalents (`Task` → `spawn_agent`, etc.)
- **Gemini CLI**: load `references/gemini-tools.md` — maps Claude tool names to Gemini equivalents
- **Claude Code**: no mapping needed (native)

### Skill Routing

Load `references/routing-patterns.md` for the full routing table and parameter resolution rules.

Pick the smallest useful pipeline that covers the confirmed intent. Resolve parameters by reading each skill's `argument-hint` and `Parameters` section, inferring what the prompt provides, and marking the rest as defaults or needing confirmation.

### Quick Routing Signals

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
| "chart" / "graph data" / "bar chart" / "pie chart" / "line chart" / "data visualization" | `/adk:chart` |
| "design" / "UI" / "mockup" | `/adk:design` |
| "audit" / "security review" / "performance review" | `/adk:audit` |
| "review this doc" / "review the RFC" | `/adk:docs-review` |
| "generate docs" / "document this repo" | `/adk:docs-repo` |
| "review the docs" / "check documentation" | `/adk:docs-review` |
| "update the docs" / "fix this doc" / "respond to doc comments" | `/adk:docs-crud` |
| "create TDD" / "create HLD" / "create LLD" / "create PRD" / "create ERD" / "incident report" / "status report" / "API reference" | `/adk:docs-crud` |
| "test" / "acceptance test" / "verify" | `/adk:test` |
| "new project" / "init" / "milestone" | `/adk:project` |
| "handoff" / "save session" / "resume" | `/adk:handoff` |
| "setup" / "configure" / "install tools" | `/adk:setup` |
| "check upstream" / "sync dependencies" | `/adk:deps-tracker` |
| "run interactive workflow" / "collect missing inputs" / "structured user Q&A" / "ask me for parameters" | `/adk:interactivity` |
| "multi-model" / "team review" / "agent team" | `/adk:team` |
| "review" / "code review" (no specific target) | `/adk:code-review` |
| "docs" / "documentation" (no specific target) | `/adk:docs` |
| "dev" / "develop" (no specific target) | `/adk:dev` |
| "Confluence page" / "publish to Confluence" | `/adk:docs-confluence` |

### Complexity and Phase Use

Use `/adk:workflow` as the source of truth.

- **Trivial**: inline intent confirm, no separate options phase, direct execution
- **Small**: inline intent confirm, light research, brief planning, direct execution
- **Medium**: full Phase 0-5
- **Large**: full Phase 0-5 plus PE check and phased execution

When uncertain, classify as Medium.

### Approach Selection

For Medium and Large work, do not lock the pipeline silently.

1. research enough to present 2-3 viable options
2. call out the simplest option explicitly
3. explain pros, cons, effort, and risk
4. let the user pick, mix, or simplify

Present approaches using the Approach Selection protocol from `/adk:interaction`.

### Planning Gate

Execution must follow an approved plan (unless `--auto`).

### Plan Expectations

The approved plan must include:

- tasks or waves
- affected files or deliverables
- verification steps
- explicit sequencing when dependencies exist

For Medium and Large work:

1. draft the plan
2. review it with the **adk-plan-reviewer** agent
3. let the user approve it
4. only then execute it

Present the plan using the Plan Approval protocol from `/adk:interaction` for Medium and Large tasks.

### Validation and Learning

End every `/adk:use` run with a compact summary:

```text

### Done

**Result**: <one-line outcome>
**Verified**: <what was validated>
**Changed**: <what diverged from the plan, if anything>
**Key insight**: <one sentence the user should remember>

Need a detailed breakdown?
```

Only expand into full details if the user asks for it.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:use <prompt-text>
/adk:use review this PR: https://github.com/org/repo/pull/42
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:use <prompt-text> --verbosity detailed
```
