---
title: "spec"
description: Analyze specs, write specifications, generate checklists, and create project constitutions
skill_name: spec
category: task
workflow_tier: full
user_invocable: true
---

# spec

Unified specification skill: writes feature specs, analyzes cross-artifact consistency, generates requirements quality checklists, and creates project constitutions. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## When to Use

- Write a feature specification with user stories and acceptance criteria
- Analyze cross-artifact consistency across specs, plans, tasks, and implementation
- Generate a requirements quality checklist ("unit tests for English")
- Create, update, or audit a project constitution (governance principles and quality gates)
- Validate that requirements are complete, clear, and consistent

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<topic>` | free-text description | required | The subject to specify or analyze |
| `--mode` | `analyze` \| `write` \| `checklist` \| `constitution` | auto-detect | Force a specific specification mode |
| `--spec` | file path | none | Path to existing spec. Without `--mode`: implies analyze. With `--mode write`: uses as input context. With `--mode checklist`: validates the given spec |
| `--depth` | `quick` \| `standard` \| `thorough` | `standard` | Analysis/checklist depth level |
| `--action` | `create` \| `update` \| `audit` | auto-detect | Constitution action type |
| `--scope` | file path | none | Limit analysis to specific sections or files |
| `--format` | `markdown` \| `google-doc` \| `confluence` | `markdown` | Output format for constitution |
| `--interactive` | `interactive` \| `auto-approve` | `interactive` | Review mode for interactive sections |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **`--mode analyze`** | Read-only cross-artifact consistency analysis. Detects issues across specs, plans, tasks, and implementation. Runs child agents in parallel for completeness, consistency, constitution compliance, and gap detection |
| **`--mode write`** | Interactive feature specification creation. Captures requirements through clarification questions, launches domain experts plus research and code review child agents, produces spec with user stories, acceptance criteria, and edge cases |
| **`--mode checklist`** | Requirements quality validation. Generates "unit tests for English" that check completeness, clarity, and consistency. Produces traceable checklist with severity ratings and quality score |
| **`--mode constitution`** | Project governance document creation, update, or audit via `/adk:audit`. Creates versioned non-negotiable principles and quality gates that all downstream work must comply with |
| **`--spec` without `--mode`** | Auto-selects analyze mode (existing spec implies analysis) |
| **No spec, new topic** | Auto-selects write mode |

## Key Behaviors

- **Smart mode detection**: infers mode from context — existing spec triggers analyze, new topic triggers write
- **Cross-artifact analysis**: analyze mode checks consistency across specs, plans, tasks, and code
- **Parallel child agents**: analyze mode launches agents for completeness, consistency, compliance, and gap detection
- **Domain expert agents**: write mode spawns domain experts and research agents to enrich specifications
- **Traceable checklists**: checklist mode produces items with severity ratings, quality scores, and traceability
- **Versioned constitutions**: constitution mode creates governance docs with explicit versioning

## Workflow

Follows the 6-phase workflow. Each stage file defines which phases apply.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | all modes | Confirm goal, detect mode, identify tools needed |
| 1. Research & Options | all modes | Explore existing artifacts, gather constraints, scope the work |
| 2. Approach Selection | write, constitution | Surface alternatives and get user confirmation when needed |
| 3. Planning | write, constitution | Explicit task plan before execution for complex specs |
| 4. Execute | all modes | Run the selected stage workflow |
| 5. Validate & Learn | all modes | Validate output, summarize what changed and what was verified |

## Stage Selection

| Signal | Mode | Stage File |
|--------|------|------------|
| "analyze", "validate", "check consistency", "verify", existing spec via `--spec` | analyze | `stages/analyze.md` |
| "write spec", "define requirements", "draft specification", "feature spec", default for new topics | write | `stages/write.md` |
| "checklist", "quality check", "validate requirements", "unit tests for English" | checklist | `stages/checklist.md` |
| "constitution", "governance", "principles", "quality gates", "non-negotiable" | constitution | `stages/constitution.md` |

### Ambiguous Input

When invoked as `/adk:spec` with no qualifying action:

1. If the user references an existing spec or document → analyze mode
2. Otherwise → write mode

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect dependencies, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

All output is markdown. Verbosity adapts to `--verbosity`:

- **short**: summary line only (e.g., "Spec written to .temp/specs/notifications/spec.md")
- **standard**: full structured output from the stage file's Output Format section
- **detailed**: standard output plus all child agent findings, decision rationale, and traceability matrices

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:plan` | Create implementation plans from specifications |
| `/adk:dev-build` | Implement code from plans |
| `/adk:code-review-pr` | Code review against specifications |

## Examples

```
/adk:spec write a feature spec for user notifications
/adk:spec --mode analyze .temp/specs/notifications/
/adk:spec --mode checklist .temp/specs/notifications/spec.md
/adk:spec --mode constitution
/adk:spec --mode constitution --action update
/adk:spec --mode constitution --action audit
/adk:spec --spec .temp/specs/auth/spec.md
```
