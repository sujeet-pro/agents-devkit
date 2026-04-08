---
title: "test"
description: Interactive user acceptance testing with test case extraction and failure diagnosis
skill_name: test
category: task
workflow_tier: abbreviated
user_invocable: true
---

# test

Interactive user acceptance testing that extracts testable deliverables from specs, plans, or requirements documents and walks the user through manual verification. Failed tests trigger automatic root cause diagnosis and optional fix plan generation. Uses abbreviated workflow (phases 2-3 skipped).

## When to Use

- Verify that an implementation meets its spec or requirements
- Walk through acceptance criteria from a PRD, spec, or plan document
- Extract testable behaviors from a requirements document
- Diagnose failures with root cause analysis
- Generate fix plans for failed test cases
- Run structured UAT before shipping

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<source>` | file path to spec, plan, or requirements doc | (required) | Document to extract test cases from |
| `--scope` | keyword filter | all test cases | Only include test cases matching these keywords |
| `--mode` | `interactive`, `auto-approve` | `interactive` | Whether to walk through each test case or run all automatically |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip all confirmations and approval gates |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Default** (`--mode interactive`) | Presents each test case one-by-one for pass/fail/skip/blocked |
| **Auto-approve** (`--mode auto-approve`) | Runs all test cases without interactive prompts, reports results at end |
| **Scoped** (`--scope <keywords>`) | Filters extracted test cases to only those matching specified keywords |
| **On failure** | Launches diagnosis agent for root cause analysis and optional fix plan generation |
| `--verbosity short` | Pass/fail summary table only |
| `--verbosity detailed` | Full test steps, diagnosis details, and fix plans for failures |

## Key Behaviors

- **Test case extraction**: parses source documents for user stories, acceptance criteria, functional requirements, edge cases, and non-functional requirements — categorizes each as functional, edge-case, or non-functional
- **Interactive testing loop**: presents each test case with steps to verify and expected result; user responds with pass/fail/skip/blocked
- **Automatic failure diagnosis**: on failure, launches a diagnosis agent to investigate root cause — reports affected files, confidence level, and suggested fix
- **Fix plan generation**: for failed items, generates fix plans compatible with `/adk:plan --mode execute`
- **Priority ordering**: processes test cases in priority order (P1 first, then P2, P3)
- **Bulk actions**: supports "pass all remaining" and "skip all remaining" shortcuts
- **UAT storage**: saves results to `.temp/uat/<source-slug>-uat.md`

## Workflow

Uses abbreviated workflow — phases 2 (Approach Selection) and 3 (Planning) are skipped.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal, source document, and success criteria |
| 1. Research & Options | yes | Analyze requirements and context from source document |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Extract test cases, run interactive testing loop, diagnose failures |
| 5. Validate & Learn | yes | Validate output quality and completeness |

## UAT Phases

| Phase | Activity | Output |
|-------|----------|--------|
| Extract Test Cases | Parse source doc for testable behaviors | Test plan with categorized cases (functional, edge-case, non-functional) |
| Interactive Testing | Present each case for pass/fail/skip/blocked | Per-case results with failure descriptions |
| Failure Diagnosis | Launch diagnosis agent on failures | Root cause, confidence, affected files, suggested fix |
| Fix Routing | Group related failures into fix tasks | Fix plans saved to `.temp/plans/<source-slug>-fixes.md` |
| Summary | Aggregate results and pass rate | UAT summary saved to `.temp/uat/<source-slug>-uat.md` |

## Required Child Agents

| Agent | Role |
|-------|------|
| Test case extractor | Reads source spec/plan, extracts concrete testable behaviors with expected outcomes |
| Diagnosis agent | Investigates root cause on failure using `/adk:dev-build --mode debug` patterns |
| Fix planner | Generates fix plans for failed items, ready for `/adk:plan --mode execute` |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect source, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

All output is markdown. The UAT summary includes:

- Source document path and total test case count
- Results breakdown: passed, failed, skipped, blocked
- Pass rate percentage
- Fix plans generated (with file path)
- Blocked items requiring manual resolution
- Post-summary prompt: accept current state, fix first, or re-test failed items

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:dev-build --mode verify` | Automated verification (tests, lint, types, build) instead of manual UAT |
| `/adk:dev-build --mode debug` | Investigate specific failures without structured UAT |
| `/adk:plan --mode execute` | Execute fix plans generated from UAT failures |
| `/adk:spec --mode write` | Write the specifications that feed UAT |

## Examples

```
/adk:test docs/spec.md
/adk:test docs/requirements.md --scope "authentication"
/adk:test .temp/plans/feature-plan.md --mode auto-approve
/adk:test docs/prd.md --verbosity detailed
/adk:test docs/spec.md --scope "API" --verbosity short
```
