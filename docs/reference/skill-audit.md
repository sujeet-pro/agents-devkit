---
title: 'audit'
description: 'Use when performing a codebase, security, performance, or dependency audit -- auto-detects focus or use --focus to specify'
skill_name: audit
category: task
workflow_tier: full
user_invocable: true
---

# audit

Use `audit` when performing a codebase, security, performance, or dependency audit -- auto-detects focus or use --focus to specify. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`audit` belongs to the `task` layer and is declared at the `full` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--focus` | `codebase`, `security`, `performance`, `dependency`, `all` | `all` | Audit focus area. Can be a single value or comma-separated combination |
| `--scope` | `all`, file path, glob pattern, `production`, `development` | `all` | Limit audit to specific files, directories, or dependency scope |
| `--format` | `markdown`, `pr` | `markdown` | Output as markdown report or PR description with checklist |
| `--publish` | off, document destination | off | Publish the final artifact to a document destination (Confluence, Google Docs) |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | -- | -- | Show this help section and exit |

### Parameter Notes

- `--focus` changes what the skill optimizes for and often changes which child agents, checks, or review dimensions are loaded.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--publish` adds a delivery step after generation so the result ends up in an external document destination.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family complex-build` | always | Complex Build workflow: confirm → research → select approach → plan → execute → validate. Full human-in-the-loop for architectural decisions. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. Cross-platform markdown safe for GitHub + Bitbucket. |
| `/adk:review-standards` | always (review skills) | Pipeline: intake → ingestion → parallel review → consolidation → output → postback. Canonical comment template with severity, confidence, concern, depth, dimension, guideline. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |
| `/adk:coding` | during guideline loading | Detect repo languages, frameworks, and tools. Load matching coding guidelines for the detected stack. |

---

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

Before scanning the codebase or launching child agents, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

### Focus Area Resolution

1. If `--focus` is explicitly provided, use that value.
2. Otherwise, scan the user's prompt for context keywords (see auto-detection rules above).
3. If auto-detection matches a single area, use that.
4. If auto-detection matches multiple areas, use those areas combined.
5. If nothing matches, default to `all`.

Once the focus is resolved, load the corresponding stage file(s):

- `codebase` -> `stages/codebase.md`
- `security` -> `stages/security.md`
- `performance` -> `stages/performance.md`
- `dependency` -> `stages/dependency.md`
- `all` -> load all four stage files

### Guideline Loading

Invoke the `/adk:coding` helper skill to detect the repo stack and load the appropriate coding guidelines. For codebase focus, use full detection (not scoped to changed files).

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **Default** (`--focus all`): runs all four audit dimensions -- codebase, security, performance, dependency.
- **Focused** (`--focus <area>`): limits audit to one or more specified areas, reducing execution time.
- **Auto-detection**: when `--focus` is not set, the skill auto-detects focus from context keywords:
  - OWASP, auth, CVE, vulnerability, injection, XSS -> `security`
  - bundle size, latency, memory, N+1, cache, profiling -> `performance`
  - outdated, dependency, npm audit, license, CVE, package -> `dependency`
  - architecture, code quality, duplication, structure -> `codebase`
  - If no keywords match or multiple areas match, defaults to `all`
- **`--scope <path>`**: limits scanning to specified files or directories
- **`--scope production`**: for dependency audits, only audits production/runtime dependencies
- **`--scope development`**: for dependency audits, only audits dev/build dependencies
- **`--format pr`**: structures output as a PR description with severity-ordered remediation checklist
- **`--publish`**: after producing the markdown artifact, publishes it to the specified document platform
- **`--verbosity short`**: executive summary with top findings only
- **`--verbosity detailed`**: full findings with code excerpts, references, and remediation examples

### Required Team

The team composition depends on the resolved focus area(s). When running `all`, launch all teams in parallel.

### Codebase Focus Team

- `adk-repo-auditor` for system-level architecture and maintainability
- `adk-code-reviewer` for correctness, security, performance, and code patterns
- `adk-doc-reviewer` for docs drift, onboarding quality, and examples
- `adk-guideline-auditor` for guideline compliance auditing
- one domain specialist based on the detected repo type: frontend, backend, or design system

### Security Focus Team

- `adk-security-reviewer` (role: auth-reviewer) for authentication and authorization flows, session management, JWT handling
- `adk-security-reviewer` (role: data-flow-analyzer) to trace sensitive data through the system, check encryption, logging, exposure
- `adk-security-reviewer` (role: dependency-scanner) to check for known CVEs, outdated packages, license issues
- `adk-security-reviewer` (role: owasp-checker) for systematic OWASP Top 10 review against the codebase

Each agent is a `adk-security-reviewer` child agent launched with a distinct role focus passed in its prompt context.

### Performance Focus Team

- `adk-code-reviewer` (role: bundle-analyzer) for dependency size breakdown, duplication, code-splitting gaps, and asset optimization
- `adk-code-reviewer` (role: latency-analyzer) for API call patterns, caching gaps, database query issues, and middleware overhead
- `adk-code-reviewer` (role: memory-analyzer) for potential leaks, data structures, and resource management
- `adk-code-reviewer` (role: anti-pattern-scanner) for performance anti-patterns with impact estimates

Each agent is a `adk-code-reviewer` child agent launched with a performance-specific role focus.

### Dependency Focus Team

- `adk-security-reviewer` (role: vulnerability-scanner) to check dependencies against known CVE databases and advisory sources
- `adk-research-agent` (role: update-compatibility-checker) to research changelogs and identify breaking changes, migration steps, and peer dependency conflicts
- `adk-code-reviewer` (role: remediation-planner) to synthesize findings into a prioritized action plan grouped by effort and risk

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

All output is markdown by default. Structure varies by deliverable type -- see the focus-area stage files for exact format.

### Output

Produce a unified audit report. Include only the sections relevant to the resolved focus area(s).

### Executive Summary

Always present. Summarizes overall posture, top action items, and focus areas covered.

### Codebase Findings (when focus includes `codebase`)

- Repository structure and ownership boundaries
- Build, test, and release ergonomics
- Public APIs and documentation quality
- Code patterns, duplication, and modernization opportunities
- Missing diagrams or architecture docs
- Prioritized improvement backlog
- Quick wins vs. strategic initiatives
- Documentation and diagram follow-ups

### Security Findings (when focus includes `security`)

- OWASP Top 10 findings
- Authentication and authorization issues
- Data handling and encryption gaps
- Secret detection results
- Dependency vulnerability summary
- Findings ordered by severity with remediation guidance

### Performance Findings (when focus includes `performance`)

- Technology stack summary
- Bundle analysis (frontend)
- Latency analysis
- Memory analysis
- Anti-pattern findings with impact estimates and code examples
- Prioritized recommendations by impact-to-effort ratio
- Quick wins and strategic improvements

### Dependency Findings (when focus includes `dependency`)

- Ecosystem breakdown, total dependencies, vulnerability counts by severity
- Vulnerability findings with affected package, severity, description, and fix
- Outdated dependencies table grouped by update type
- License issues
- Remediation plan with effort estimates and exact update commands
- Risk notes for unmaintained or deprecated packages

### Follow-Up

- Clear next steps that another agent can use to plan implementation
- Checklist of action items

When `--format pr`, structure the output as a PR description with a severity-ordered checklist of remediation tasks suitable for tracking progress.

If `--publish` is set, publish the final markdown artifact to the requested document source after the review completes.

## Related Skills

### Adjacent Skills

- `/adk:code-review-pr` — focused diff review after you address audit findings
- `/adk:code-review-repo` — holistic repo review when audit scope is whole-codebase
- `/adk:dev-build` — implement remediation from audit recommendations
- `/adk:plan` — sequence remediation work into an executable plan

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:audit
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:audit --focus security
/adk:audit --focus codebase --scope src/
/adk:audit --focus performance --scope src/api/ --verbosity detailed
/adk:audit --focus dependency --scope production --format pr
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:audit --focus performance --scope src/api/ --verbosity detailed
/adk:audit --focus dependency --scope production --format pr
/adk:audit --publish --verbosity detailed
/adk:audit --focus codebase --publish
```
