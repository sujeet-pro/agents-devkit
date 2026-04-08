---
title: "code-review-repo"
description: Review an entire repository for architecture, code quality, patterns, and tech debt with a prioritized improvement plan
skill_name: code-review-repo
category: task
workflow_tier: full
user_invocable: true
---

# code-review-repo

Reviews an entire repository and produces a prioritized improvement plan. Unlike `/adk:code-review-pr` (which reviews a PR diff) or `/adk:audit` (which runs focused audits), this skill builds a holistic view of the codebase and recommends a ranked set of changes across architecture, code quality, patterns, testing, documentation, and security.

## When to Use

- Audit the overall health of a codebase
- Identify architecture violations and coupling issues
- Find code quality hotspots (complexity, duplication, dead code)
- Detect pattern inconsistencies and anti-patterns across modules
- Surface tech debt and prioritize remediation
- Review testing coverage gaps and test quality
- Assess documentation completeness
- Evaluate security surface area

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `[path]` | directory path or omitted | `.` (repo root) | Scope review to a specific package or directory |
| `--focus` | `architecture` \| `quality` \| `patterns` \| `debt` \| `security` \| `performance` \| `all` | `all` | Weight review toward specific dimensions. Comma-separated for multiple |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--mode` | `auto` \| `standard` \| `interactive` | `auto` | `auto` skips confirmations and uses standard depth |
| `--output` | `markdown` \| `json` | `markdown` | Output format |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Default** (`--focus all`) | Runs all six review dimensions in parallel |
| **Focused** (`--focus <area>`) | Limits review to specified dimensions only |
| **Auto-detection** (no `--focus`) | Scans the user's prompt for context keywords to select focus areas |
| **Keyword → architecture** | coupling, boundaries, layers, modules, monolith, microservice |
| **Keyword → quality** | duplication, complexity, readability, naming, error handling |
| **Keyword → patterns** | consistency, conventions, anti-patterns, style |
| **Keyword → debt** | TODO, FIXME, deprecated, legacy, workaround |
| **Keyword → security** | auth, injection, XSS, OWASP, secrets |
| **Keyword → performance** | latency, memory, bundle, N+1, cache |
| `--mode auto` | Skips Phase 0-2 confirmations, uses standard depth |
| `--verbosity short` | Executive summary with top 10 findings only |
| `--verbosity detailed` | Full findings with code excerpts, references, and remediation examples |

## Priorities

The skill reviews across **6 dimensions**, each covered by a dedicated child agent:

1. **Architecture** — module boundaries, coupling analysis, dependency direction, API surface area, state management, data flow, scalability constraints
2. **Code Quality** — complexity hotspots, duplication detection, error handling consistency, naming clarity, dead code and unused exports
3. **Patterns & Consistency** — coding style consistency, design pattern usage, anti-pattern detection (god objects, feature envy, shotgun surgery), convention drift
4. **Testing** — coverage gaps, test quality (assertion density, mocking, isolation), structure, integration vs unit balance, flaky test indicators
5. **Documentation** — README completeness, API documentation coverage, architecture decision records, code comment quality, onboarding documentation
6. **Security Surface** — authentication and authorization patterns, input validation, secrets management, dependency vulnerabilities, data handling (PII, encryption, logging)

Findings are ranked into four priority tiers: **P0 — Critical** (fix immediately), **P1 — High** (fix this quarter), **P2 — Medium** (fix when touching the area), **P3 — Low** (backlog).

## Key Behaviors

- **Prompt keyword auto-detection**: infers `--focus` from natural language when not explicitly set
- **Wave-based parallel execution**: 4 review waves — structure & dependencies, code analysis per module, cross-cutting concerns, synthesis
- **Child agents per dimension**: dedicated agents for architecture, quality, patterns, testing, documentation, security
- **Deduplication**: findings describing the same root cause from multiple agents are merged, not double-counted
- **Human review gate**: merged findings are presented to the user before finalizing — allows reclassification, removal, or added context
- **Review-only**: does not modify repository files; produces a review artifact

## Workflow

Follows the full 6-phase workflow for all reviews.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm scope (entire repo vs specific packages/dirs), focus areas, and output format |
| 1. Research & Options | yes | Research codebase structure, build mental model, identify key patterns and anti-patterns |
| 2. Approach Selection | yes | Present 2-3 review depth options: quick scan, standard review, deep audit |
| 3. Planning | yes | Plan review waves by package/module for parallel execution |
| 4. Execute | yes | Execute review via parallel child agents per dimension |
| 5. Validate & Learn | yes | Merge findings, deduplicate, prioritize by impact, produce improvement plan |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect source, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `review-standards` | always | Review pipeline and canonical comment template |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch child agents with distinct review roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

Produces a markdown report saved to `.temp/review-repo/review-report.md` with these sections:

- **Executive Summary** — 3-5 bullet points: overall health, top concerns, recommended first actions
- **Scope & Methodology** — what was reviewed, depth level, focus areas, agents used
- **Architecture Review** — module boundaries, coupling, layering, API design
- **Code Quality** — complexity, duplication, error handling, naming
- **Patterns & Consistency** — style consistency, design patterns, anti-patterns, convention drift
- **Testing** — coverage gaps, test quality, structure, balance
- **Documentation** — README, API docs, ADRs, code comments, onboarding
- **Security Surface** — auth, input validation, secrets, dependencies, data handling
- **Prioritized Improvement Plan** — P0 through P3 tiers with action timelines
- **Appendix** — raw findings, methodology notes, tools used

`--verbosity short` outputs only Executive Summary + Prioritized Improvement Plan. `--verbosity detailed` includes code excerpts, file paths, and remediation examples for every finding.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:code-review-pr` | Review a specific PR diff, not the whole repo |
| `/adk:audit` | Focused audits (security, performance, dependency, codebase) |
| `/adk:plan` | Execute the improvement plan produced by this skill |
| `/adk:dev-build` | Implement specific improvements from findings |

## Examples

```
/adk:code-review-repo
/adk:code-review-repo --focus architecture
/adk:code-review-repo --focus quality,patterns --verbosity detailed
/adk:code-review-repo src/backend/ --focus debt
/adk:code-review-repo --mode auto --focus all
/adk:code-review-repo packages/core/ --focus security,performance
```
