---
title: "audit"
description: Codebase, security, performance, or dependency audit with auto-detected focus
skill_name: audit
category: task
workflow_tier: full
user_invocable: true
---

# audit

Full codebase audit across four dimensions: code quality, security, performance, and dependencies. Auto-detects focus from context keywords or accepts explicit `--focus`. Launches parallel child agent teams per focus area, produces a unified severity-ordered report, and optionally publishes to Confluence or Google Docs.

## When to Use

- Run a full-spectrum audit of a codebase (architecture, security, performance, dependencies)
- Perform a focused security audit (OWASP Top 10, auth flows, secret detection)
- Analyze performance bottlenecks (bundle size, latency, memory, anti-patterns)
- Audit dependencies for vulnerabilities, outdated packages, and license issues
- Review codebase architecture, duplication, and modernization opportunities
- Generate a PR-formatted remediation checklist
- Publish audit findings to Confluence or Google Docs

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--focus` | `codebase`, `security`, `performance`, `dependency`, `all` | `all` | Audit focus area. Can be a single value or comma-separated combination |
| `--scope` | `all`, file path, glob pattern, `production`, `development` | `all` | Limit audit to specific files, directories, or dependency scope |
| `--format` | `markdown`, `pr` | `markdown` | Output as markdown report or PR description with severity-ordered checklist |
| `--publish` | off, document destination | off | Publish the final artifact to a document destination (Confluence, Google Docs) |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip all confirmations and approval gates |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Default** (`--focus all`) | Runs all four audit dimensions: codebase, security, performance, dependency |
| **Focused** (`--focus <area>`) | Limits audit to one or more specified areas, reducing execution time |
| **Auto-detection** (no `--focus`) | Scans user prompt for keywords to infer focus area (e.g., OWASP → security, bundle size → performance, outdated → dependency, architecture → codebase). Defaults to `all` if ambiguous |
| `--scope <path>` | Limits scanning to specified files or directories |
| `--scope production` | For dependency audits, only audits production/runtime dependencies |
| `--scope development` | For dependency audits, only audits dev/build dependencies |
| `--format pr` | Structures output as a PR description with severity-ordered remediation checklist |
| `--publish` | After producing the markdown artifact, publishes to the specified document platform |
| `--verbosity short` | Executive summary with top findings only |
| `--verbosity detailed` | Full findings with code excerpts, references, and remediation examples |

## Priorities

Each focus area has its own priority framework:

1. **Security** — OWASP Top 10, authentication/authorization, data handling, secret detection, dependency CVEs
2. **Performance** — bundle analysis, latency patterns, memory management, anti-pattern detection with impact estimates
3. **Codebase** — architecture, ownership boundaries, build/test/release ergonomics, API quality, code patterns, documentation drift
4. **Dependency** — vulnerability counts by severity, outdated packages by update type, license issues, unmaintained package risk

Findings across all dimensions carry **severity** (Blocker > Critical > Should Have > May Have > Nitpick > Question), **confidence scores**, **concern domains**, and **review depth** tags.

## Key Behaviors

- **Review-only**: does not modify repository files — produces a report artifact or publishes to a document destination
- **Smart focus detection**: infers `--focus` from context keywords (OWASP/CVE → security, N+1/cache → performance, outdated/license → dependency, architecture/duplication → codebase)
- **Parallel agent teams**: launches specialized child agent teams per focus area, running all teams in parallel for `--focus all`
- **Guideline-aware**: invokes `/adk:coding` to detect the repo stack and load matching coding guidelines before analysis
- **Scope-aware dependency audits**: `--scope production` and `--scope development` filter dependency analysis to runtime or build dependencies respectively
- **Publishable output**: markdown reports can be published directly to Confluence or Google Docs via `--publish`

## Workflow

Follows the 6-phase workflow for all audits.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal, assumptions, required tools, and success criteria |
| 1. Research & Options | yes | Analyze scope, detect source type, load guidelines, auto-detect focus |
| 2. Approach Selection | yes | Present 2-3 approaches, user picks or mixes |
| 3. Planning | yes | Break into tasks/waves for parallel agentic teams |
| 4. Execute | yes | Produce the review using parallel child agents per focus area |
| 5. Validate & Learn | yes | Verify review completeness, accuracy, and actionability |

## Required Teams

The team composition depends on the resolved focus area(s). When running `all`, all teams launch in parallel.

| Focus | Agents | Roles |
|-------|--------|-------|
| **Codebase** | `adk-repo-auditor`, `adk-code-reviewer`, `adk-doc-reviewer`, domain specialist | Architecture, correctness, docs drift, frontend/backend specialization |
| **Security** | 4× `adk-security-reviewer` | auth-reviewer, data-flow-analyzer, dependency-scanner, owasp-checker |
| **Performance** | 4× `adk-code-reviewer` | bundle-analyzer, latency-analyzer, memory-analyzer, anti-pattern-scanner |
| **Dependency** | `adk-security-reviewer`, `adk-research-agent`, `adk-code-reviewer` | vulnerability-scanner, update-compatibility-checker, remediation-planner |

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
| `coding` | guideline loading | Detect stack, load matching coding guidelines |

## Output Format

All output is markdown by default. The report includes:

- **Executive Summary** — overall posture, top action items, focus areas covered (always present)
- **Codebase Findings** — repo structure, build/test ergonomics, API quality, code patterns, prioritized improvement backlog
- **Security Findings** — OWASP Top 10 findings, auth issues, data handling gaps, secret detection, severity-ordered remediation
- **Performance Findings** — stack summary, bundle/latency/memory analysis, anti-patterns with impact estimates, prioritized recommendations
- **Dependency Findings** — ecosystem breakdown, vulnerability table, outdated dependencies, license issues, remediation plan with effort estimates
- **Follow-Up** — clear next steps and checklist of action items

When `--format pr`, output is structured as a PR description with a severity-ordered checklist. When `--publish` is set, the artifact is published to the specified document destination.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:code-review-pr` | Focused diff review after addressing audit findings |
| `/adk:code-review-repo` | Holistic repo review when audit scope is whole-codebase |
| `/adk:dev-build` | Implement remediation from audit recommendations |
| `/adk:plan` | Sequence remediation work into an executable plan |

## Examples

```
/adk:audit
/adk:audit --focus security
/adk:audit --focus codebase --scope src/
/adk:audit --focus performance --scope src/api/ --verbosity detailed
/adk:audit --focus dependency --scope production --format pr
/adk:audit --focus security,performance
/adk:audit --publish --verbosity detailed
/adk:audit --focus codebase --publish
```
