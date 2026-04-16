---
title: 'adk-audit-repo'
description: 'Audit a repository for correctness risks, maintainability issues, and validation gaps. Use when you need a prioritized improvement list instead of a line-by-line PR review'
skill_name: adk-audit-repo
category: task
workflow_tier: full
user_invocable: true
---

# adk-audit-repo

Use `adk-audit-repo` to audit a repository for correctness risks, maintainability issues, and validation gaps. Use when you need a prioritized improvement list instead of a line-by-line PR review. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-audit-repo` belongs to the `task` layer and is declared at the `full` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--scope` | path | repo root | Limit the audit surface |
| `--focus` | `quality`, `security`, `performance`, `dependencies`, `all` | `all` | Primary audit lens |
| `--auto` | flag | off | Skip confirmations; run end-to-end and present findings directly |
| `--help` | flag | off | Show the skill and stop |

### Parameter Notes

- `--focus` changes what the skill optimizes for and often changes which child agents, checks, or review dimensions are loaded.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

See `references/workflow.md` for full phase details.

### Phase 1 -- Scope (gate: approval unless `--auto`)
Confirm audit dimensions, target path, and focus area with the user. Clarify exclusions.

### Phase 2 -- Scan
Run comprehensive checks across 5 dimensions. Collect raw signals for each.

#### 1. Code Quality
**Check for**:
- Cyclomatic complexity hotspots (functions > 15, files > 300 lines)
- Code duplication (3+ lines, 2+ occurrences; near duplicates with minor variation)
- Naming inconsistencies (mixed conventions, abbreviations, misleading names)
- Dead code: unreachable functions, unused exports/imports, commented-out blocks
- Architecture violations: circular dependencies, layer bypasses, god modules
- Coupling: high afferent/efferent coupling, shared mutable state

**Score 0-4**: 0=Systemic violations (circular deps, pervasive duplication, no structure), 1=Major problems (god modules, high complexity, significant duplication), 2=Partial (some structure, notable gaps in naming, duplication, or layering), 3=Good (mostly clean, minor complexity or duplication), 4=Excellent (well-structured, low coupling, clear naming, minimal duplication)

#### 2. Security
**Check for**:
- Secrets in code: hardcoded API keys, tokens, passwords, connection strings
- Input validation gaps: unsanitized user input, missing boundary checks
- Auth/authz holes: missing permission checks, broken access control patterns
- Dependency vulnerabilities: known CVEs in direct and transitive dependencies
- Logging sensitive data: PII, tokens, or credentials in log output
- Insecure defaults: debug mode on, permissive CORS, missing rate limiting

**Score 0-4**: 0=Critical exposure (secrets in code, no auth checks, known CVEs), 1=Major gaps (missing input validation, weak auth patterns, unpatched deps), 2=Partial (some security measures, notable gaps remain), 3=Good (solid auth, input validation, minor issues), 4=Excellent (defense in depth, no secrets, deps patched, proper access control)

#### 3. Testing
**Check for**:
- Untested public functions/methods and critical paths (auth, payment, data mutation)
- Test coverage gaps vs. claimed coverage
- Tests asserting implementation details instead of behavior
- Missing edge cases: error paths, empty inputs, boundary values
- Flaky tests: timing-dependent, order-dependent, shared state
- Test infrastructure: missing CI integration, no coverage tracking

**Score 0-4**: 0=No tests or broken suite (tests fail, no CI), 1=Minimal (few tests, critical paths uncovered, no edge cases), 2=Partial (some coverage, significant gaps in critical paths or edge cases), 3=Good (critical paths covered, minor edge-case gaps, CI runs), 4=Excellent (high meaningful coverage, edge cases handled, fast reliable suite)

#### 4. Documentation
**Check for**:
- README accuracy: setup instructions match actual build/run process
- API doc drift: documented endpoints/signatures vs. actual code
- Stale comments: comments that contradict current code behavior
- Missing ADRs: significant architectural decisions without recorded rationale
- Onboarding gaps: new developer cannot build and test from docs alone
- Outdated diagrams or architecture docs

**Score 0-4**: 0=No docs (no README, no comments, no API docs), 1=Minimal (README exists but outdated or misleading), 2=Partial (some docs, notable staleness or onboarding gaps), 3=Good (accurate README, some API docs, minor staleness), 4=Excellent (comprehensive, accurate, new developer can self-serve)

#### 5. Dependencies
**Check for**:
- Outdated packages: major version behind, known vulnerabilities
- Unused dependencies: installed but never imported
- Missing lockfile or lockfile out of sync with manifest
- Pinning hygiene: unpinned versions that could break on install
- License compliance: incompatible licenses in dependency tree
- Transitive risk: deep dependency chains with unmaintained packages

**Score 0-4**: 0=Critical (known CVEs, no lockfile, many unused), 1=Major (several outdated with vulnerabilities, poor pinning), 2=Partial (some outdated, lockfile present but gaps), 3=Good (mostly current, lockfile clean, minor unused), 4=Excellent (all current, locked, no unused, licenses checked)

### Phase 3 -- Deep Dive
Dispatch subagents for specialized analysis:
- `adk-security-reviewer` for security dimension
- `adk-code-reviewer` for code quality dimension
- Run dependency-vulnerability and dead-code checks in parallel

### Phase 4 -- Score
Score each dimension 0-4 using the criteria defined in Phase 2.

| Score | Label | Meaning |
| --- | --- | --- |
| 4 | Excellent | No significant issues |
| 3 | Good | Minor issues only |
| 2 | Fair | Notable issues requiring attention |
| 1 | Poor | Serious issues affecting reliability |
| 0 | Critical | Immediate action required |

**Rating bands** (sum of 5 dimensions):
- 18-20 Excellent -- minor polish only
- 14-17 Good -- address weak dimensions
- 10-13 Acceptable -- significant work needed
- 6-9 Poor -- major overhaul required
- 0-5 Critical -- fundamental issues across the board

Dimensions scored: **code quality**, **security**, **testing**, **documentation**, **dependencies**.

### Phase 5 -- Findings
Severity-ordered issues with P0-P3 ratings:
- **P0** -- Critical risk, fix immediately
- **P1** -- High risk, fix this sprint
- **P2** -- Medium risk, plan a fix
- **P3** -- Low risk, address when convenient

Group into **quick-wins**, **planned**, and **strategic improvements**.

### Phase 6 -- Report
Deliver:
1. Executive summary (2-3 sentences)
2. Health score card (table)
3. Detailed findings (severity-ordered)
4. Recommended actions (effort-tagged)
5. Blind spots and residual risks

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```markdown

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/review-comment-format.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- Decisions interactive, execution automatic. Never make irreversible changes without approval. `--auto` skips confirmations but still reports everything.
- **Plan First** -- Phased workflow with approval gates. Show the audit plan, get sign-off, then scan.
- **Brainstorm After Findings, Not Before Scanning** -- use only a light brainstorming handoff when the user wants remediation planning or fix prioritization across multiple paths.
- **Concise by Default** -- Health score card and top findings first. Offer to elaborate on any dimension.
- **Parallel Agentic Teams** -- Dispatch `adk-security-reviewer` for security scans and `adk-code-reviewer` for code quality deep dives. Orchestrator coordinates, never duplicates subagent work.
- **Principal Engineer Lens** -- Challenge scope before accepting it. Prioritize repeated patterns over isolated nits. Recommend the smallest high-leverage fix first.

### Persona

See `references/persona.md` for the full Repository Health Inspector persona.

- **Mission**: Find the highest-leverage correctness, maintainability, and validation risks in a codebase and present them as a scored, actionable health report.
- **Voice**: Direct, evidence-backed, severity-ordered. Leads with scores, not prose.
- **Hard rules**: Evidence before opinion. Patterns over nits. Blind spots stay visible.
- **Evidence expectations**: Every finding cites code, config, test output, or tool evidence. Missing runtime evidence is flagged, never hidden.

### When To Use

- Reviewing a codebase area for quality or risk
- Auditing for security, performance, or dependency issues
- Finding a prioritized improvement list with health scores
- Comparing repo health before/after a major change

### When NOT To Use

- Single-diff PR review -- use `adk-review-pr`
- Live site quality checks -- use `adk-audit-site`
- Writing or fixing code -- use `adk-build`
- Research or documentation -- use `adk-research` or `adk-review-docs`

### Pre-flight

Run `python3 scripts/preflight.py` before any audit work.
If the script reports a missing dependency, stop and tell the user.

### Interaction Protocol

### Intent Confirmation
Unless `--auto` is set, confirm before starting:
- Audit scope (full repo or scoped path)
- Primary audit lens
- Areas to exclude or prioritize

### Findings Presentation
Each finding uses the format:

```
F<n> [Type][Severity]: Title
Confidence: High|Medium|Low | Dimension: <dim> | Scope: <file:line or area>
Effort: quick-win | planned | strategic

**Issue Summary** -- What is wrong.
**Why This Matters** -- Impact if unaddressed.
**Suggested Fix** -- Actionable remediation.
**Verify** -- How to confirm the fix (optional).
```

Types: **Bug**, **Risk**, **Improvement**, **Nitpick**, **Question**
Severity: **P0** (Critical) > **P1** (High) > **P2** (Medium) > **P3** (Low)
Dimensions: **architecture**, **security**, **performance**, **code-quality**, **testing**, **dependencies**, **documentation**

### User Response
After findings, the user responds with:
- `a-N` -- accept finding N
- `r-N` -- reject finding N
- `e-N` -- expand finding N (more detail)
- `all` -- accept all findings

Example: `a-1, a-3, a-6, r-5, e-2`

### Parallel Agents

| Agent | Role | Dispatched When |
| --- | --- | --- |
| `adk-security-reviewer` | Security-focused deep scan | `--focus security` or `--focus all` |
| `adk-code-reviewer` | Code quality and pattern analysis | `--focus quality` or `--focus all` |

Each subagent receives scoped context and returns structured findings. The orchestrator merges, deduplicates, and severity-ranks the combined results.

### Validation

- Every finding references code, config, or tool evidence
- Severity and priority are explicit
- Recommendations are scoped and actionable
- Blind spots and untested areas are visible in the report
- Health scores are justified by the findings that informed them

### Executive Summary

<2-3 sentences>

### Health Score Card

| # | Dimension | Score | Label | Key Finding |
| --- | --- | --- | --- | --- |
| 1 | Code Quality | 3 | Good | Cyclomatic complexity > 20 in 3 functions |
| 2 | Security | 2 | Fair | API key in config, 2 unpatched CVEs |
| 3 | Testing | 1 | Poor | Auth flow has zero test coverage |
| 4 | Documentation | 3 | Good | README setup steps outdated |
| 5 | Dependencies | 2 | Fair | 8 outdated, 3 unused packages |
| **Total** | | **11/20** | **Acceptable** | |

### Findings (N total: X P0, Y P1, Z P2, W P3)

### P0 -- Critical
<findings using F<n> format from review-comment-format.md>

### P1 -- High
<findings>

### P2 -- Medium / P3 -- Low
<findings>

### Recommended Actions

| Priority | Action | Effort | Dimension |
| --- | --- | --- | --- |
| 1 | Rotate exposed API key, add to .env | quick-win | security |

### Blind Spots

- <areas not covered or needing runtime verification>

### Next Steps

- <what to do after this audit>
- Re-run audit after fixes to see score improve
```

### Anti-Patterns / Red Flags

- **Scope creep**: Auditing all 5 dimensions when the user asked `--focus security`. Confirm scope first.
- **Opinion without evidence**: Saying "error handling is weak" without citing the function, file, and line where a catch block is missing. Every finding must include a code reference.
- **Nit avalanche**: Reporting 30 P3 formatting nits when 3 P0 security issues exist. Prioritize repeated patterns over isolated style violations. Cap P3 findings at 10.
- **Hidden blind spots**: Scoring testing at 3/4 when no test runner executed and coverage was inferred from file counts. If tests could not be run, the score must reflect that.
- **Fix without ask**: Rewriting a function during the audit. The audit skill reports findings; it does not apply fixes unless explicitly asked.
- **Inflated scores**: Giving security 4/4 when dependency vulnerability scanning was not performed. Unassessed sub-checks lower the maximum achievable score.
- **Generic recommendations**: Saying "improve test coverage" instead of "add integration tests for `UserService.createUser` and `PaymentService.charge`, which handle auth and payment with zero coverage."

### Related Skills

- `adk-review-pr` -- single-diff code review
- `adk-review-local-changes` -- review uncommitted work
- `adk-audit-site` -- live site quality audit
- `adk-test` -- test execution and verification
- `adk-research` -- deep research tasks

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-audit-repo
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-audit-repo --auto
```
