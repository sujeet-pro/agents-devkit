---
name: adk-code-review-repo
description: "adk - [full] [code-review] Review an entire repository — architecture, code quality, patterns, tech debt. Prioritized improvement plan."
user-invocable: true
argument-hint: "[path] [--focus architecture|quality|patterns|debt|security|performance|all] [--verbosity short|standard|detailed]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Review Repo

This skill reviews an entire repository and produces a prioritized improvement plan. Unlike `/adk:code-review-pr` (which reviews a PR diff) or `/adk:audit` (which runs focused audits), this skill builds a holistic view of the codebase and recommends a ranked set of changes across architecture, code quality, patterns, testing, documentation, and security.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. Cross-platform markdown safe for GitHub + Bitbucket. |
| `/adk:review-standards` | always (review skills) | Pipeline: intake → ingestion → parallel review → consolidation → output → postback. Canonical comment template with severity, confidence, concern, depth, dimension, guideline. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |

This skill is review-only. Do not modify repository files. Produce a review artifact.

---

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/adk-<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `[path]` | directory path or omitted | `.` (repo root) | Scope review to a specific package or directory |
| `--focus` | `architecture`, `quality`, `patterns`, `debt`, `security`, `performance`, `all` | `all` | Weight review toward specific dimensions. Comma-separated for multiple |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--mode` | `auto`, `standard`, `interactive` | `auto` | `auto` skips confirmations and uses standard depth |
| `--output` | `markdown`, `json` | `markdown` | Output format |
| `--help` | -- | -- | Show this help section and exit |

### Behavior Variations

- **Default** (`--focus all`): runs all six review dimensions in parallel.
- **Focused** (`--focus <area>`): limits review to specified dimensions.
- **Auto-detection**: when `--focus` is not set, the skill scans the user's prompt for context keywords:
  - coupling, boundaries, layers, modules, monolith, microservice -> `architecture`
  - duplication, complexity, readability, naming, error handling -> `quality`
  - consistency, conventions, anti-patterns, style -> `patterns`
  - TODO, FIXME, deprecated, legacy, workaround -> `debt`
  - auth, injection, XSS, OWASP, secrets -> `security`
  - latency, memory, bundle, N+1, cache -> `performance`
  - If no keywords match or multiple areas match, defaults to `all`
- **`--mode auto`**: skips Phase 0-2 confirmations, uses standard depth.
- **`--verbosity short`**: executive summary with top 10 findings only.
- **`--verbosity detailed`**: full findings with code excerpts, references, and remediation examples.

### Examples

```
/adk:code-review-repo
/adk:code-review-repo --focus architecture
/adk:code-review-repo --focus quality,patterns --verbosity detailed
/adk:code-review-repo src/backend/ --focus debt
/adk:code-review-repo --mode auto --focus all
/adk:code-review-repo packages/core/ --focus security,performance
```

---

## Preflight

Run before scanning the codebase or launching child agents:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

---

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm scope (entire repo vs specific packages/dirs), focus areas, and output format |
| 1. Research & Options | yes | Research codebase structure, build mental model, identify key patterns and anti-patterns |
| 2. Approach Selection | yes | Present 2-3 review depth options: quick scan, standard review, deep audit |
| 3. Planning | yes | Plan review waves by package/module for parallel execution |
| 4. Execute | yes | Execute review via parallel child agents per dimension |
| 5. Validate & Learn | yes | Merge findings, deduplicate, prioritize by impact, produce improvement plan |

---

## Phase 0: Scope Confirmation

Confirm with the user before starting:

1. **Scope**: entire repo, specific directories, or specific packages
2. **Focus areas**: which dimensions to review (default: all)
3. **Depth**: quick scan, standard, or deep audit
4. **Output**: where to save the report

In `--mode auto`, skip confirmation and use: entire repo, all dimensions, standard depth.

---

## Phase 1: Codebase Research

Build a mental model of the repository before reviewing:

1. **Repository structure**: top-level layout, package boundaries, entry points
2. **Tech stack detection**: invoke `/adk:coding` to detect frameworks, languages, and load matching coding guidelines
3. **Key files**: README, contributing guides, CI config, dependency manifests
4. **Git history signals**: recent churn (frequently changed files), contributor patterns, age of oldest untouched code
5. **Existing patterns**: naming conventions, error handling patterns, test structure, dependency injection approach

Output: `.temp/review-repo/01-codebase-model.md`

---

## Phase 2: Depth Selection

Present 2-3 review depth options:

| Depth | Scope | Time | Detail |
|-------|-------|------|--------|
| **Quick scan** | Top-level structure, high-signal files, dependency health | ~5 min | Executive summary, top 10 findings |
| **Standard review** | All packages, representative sampling of files per module | ~15 min | Full report with prioritized improvement plan |
| **Deep audit** | Every file, cross-cutting analysis, historical trend analysis | ~30 min | Comprehensive report with code excerpts and remediation examples |

In `--mode auto`, select standard review.

---

## Phase 3: Review Wave Planning

Group the review into waves for parallel execution:

**Wave 1 — Structure & Dependencies** (parallel):
- Repository layout and package boundaries
- Dependency graph and health
- Build and CI configuration

**Wave 2 — Code Analysis** (parallel, per module):
- Architecture patterns per module
- Code quality per module
- Pattern consistency across modules

**Wave 3 — Cross-Cutting** (parallel):
- Testing coverage and quality
- Documentation completeness
- Security surface area
- Performance patterns

**Wave 4 — Synthesis** (sequential):
- Merge and deduplicate findings
- Prioritize by impact
- Generate improvement plan

---

## Phase 4: Execute Review

### Required Team

Launch child agents in parallel, scoped to the resolved focus areas.

#### Architecture Agent
- Module boundaries and coupling analysis
- Dependency direction (no circular deps, clean layering)
- API surface area and contract clarity
- State management patterns
- Data flow and integration points
- Scalability constraints

#### Code Quality Agent
- Complexity hotspots (cyclomatic complexity, deep nesting)
- Duplication detection (copy-paste code, near-duplicates)
- Error handling consistency and completeness
- Naming clarity and convention adherence
- Dead code and unused exports

#### Patterns & Consistency Agent
- Coding style consistency across modules
- Design pattern usage (appropriate vs forced)
- Anti-pattern detection (god objects, feature envy, shotgun surgery)
- Convention drift between older and newer code
- Framework/library usage patterns

#### Testing Agent
- Test coverage gaps (untested public APIs, edge cases)
- Test quality (assertion density, mocking practices, test isolation)
- Test structure and organization
- Integration vs unit test balance
- Flaky test indicators

#### Documentation Agent
- README completeness and accuracy
- API documentation coverage
- Architecture decision records (present or missing)
- Code comments quality (helpful vs noise)
- Onboarding documentation

#### Security Surface Agent
- Authentication and authorization patterns
- Input validation and sanitization
- Secrets management (hardcoded values, env handling)
- Dependency vulnerabilities (known CVEs)
- Data handling (PII, encryption, logging)

Each agent produces findings in the canonical review comment format from `/adk:review-standards`.

---

## Phase 5: Merge & Prioritize

### Merge Rules

- Deduplicate findings that describe the same underlying issue from multiple agents
- Preserve minority opinions when they affect risk assessment
- Cross-reference findings: an architecture issue causing quality issues is one root cause, not two

### Prioritization

Rank findings into four tiers:

| Priority | Criteria | Action Timeline |
|----------|----------|-----------------|
| **P0 — Critical** | Security vulnerabilities, data loss risk, production stability | Fix immediately |
| **P1 — High** | Architecture violations blocking scaling, major tech debt compounding | Fix this quarter |
| **P2 — Medium** | Code quality issues, missing tests, documentation gaps | Fix when touching the area |
| **P3 — Low** | Style inconsistencies, minor improvements, nice-to-haves | Backlog |

### Human Review

Before finalizing the plan, present the merged findings to the user for review. Allow them to:
- Reclassify priority for specific findings
- Remove findings that are intentional trade-offs
- Add context the agents missed

---

## Output Format

Produce a markdown report saved to `.temp/review-repo/review-report.md` with these sections:

```markdown
# Repository Review: <repo-name>

## Executive Summary
<!-- 3-5 bullet points: overall health, top concerns, recommended first actions -->

## Scope & Methodology
<!-- What was reviewed, depth level, focus areas, agents used -->

## Architecture Review
<!-- Module boundaries, coupling, layering, API design -->

## Code Quality
<!-- Complexity, duplication, error handling, naming -->

## Patterns & Consistency
<!-- Style consistency, design patterns, anti-patterns, convention drift -->

## Testing
<!-- Coverage gaps, test quality, structure, balance -->

## Documentation
<!-- README, API docs, ADRs, code comments, onboarding -->

## Security Surface
<!-- Auth, input validation, secrets, dependencies, data handling -->

## Prioritized Improvement Plan

### P0 — Critical (fix immediately)
### P1 — High (fix this quarter)
### P2 — Medium (fix when touching the area)
### P3 — Low (backlog)

## Appendix
<!-- Raw findings, methodology notes, tools used -->
```

When `--verbosity short`, output only: Executive Summary + Prioritized Improvement Plan.
When `--verbosity detailed`, include code excerpts, file paths, and remediation examples for every finding.

---

## Adjacent Skills

- `/adk:code-review-pr` for PR-specific code review
- `/adk:audit` for focused audits (security, performance, dependency, codebase)
- `/adk:plan` for executing the improvement plan produced by this skill
- `/adk:dev-build` for implementing specific improvements
