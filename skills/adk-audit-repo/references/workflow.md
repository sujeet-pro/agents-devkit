# ADK Audit Repo Workflow

## Phase 1 -- Scope
**Gate: approval unless `--auto`**

1. Confirm the audit target (full repo or `--scope` path)
2. Confirm the primary focus (`quality`, `security`, `performance`, `dependencies`, or `all`)
3. Identify exclusions (vendored code, generated files, specific directories)
4. State the audit dimensions that will be covered
5. If `--auto`, log the resolved scope and proceed

**Approval prompt**: "Audit [scope] with [focus] lens. Dimensions: [list]. Exclusions: [list]. Proceed?"

## Phase 2 -- Scan

1. Map the repository structure: languages, frameworks, entry points, dependency manifests
2. Run per-dimension checks using the checklists defined in SKILL.md Phase 2:
   - **Code Quality**: cyclomatic complexity, duplication, dead code, coupling, naming, architecture violations
   - **Security**: secrets in code, input validation, auth patterns, dependency CVEs, logging PII, insecure defaults
   - **Testing**: coverage gaps, untested critical paths, implementation-detail tests, flaky tests, CI integration
   - **Documentation**: README accuracy, API doc drift, stale comments, missing ADRs, onboarding gaps
   - **Dependencies**: outdated packages, unused deps, lockfile hygiene, pinning, license compliance, transitive risk
3. Collect raw signals into a per-dimension evidence log
4. For each checklist item, record: checked/unchecked, evidence found, confidence level

## Phase 3 -- Deep Dive

1. Dispatch `adk-security-reviewer` (if security dimension is in scope):
   - Scoped to `--scope` path or full repo
   - Returns structured security findings with severity and evidence
2. Dispatch `adk-code-reviewer` (if code quality dimension is in scope):
   - Scoped to `--scope` path or full repo
   - Returns code quality findings: architecture violations, coupling, duplication
3. Run dependency and dead-code analysis in parallel with subagent work
4. Merge subagent results with scan-phase signals

**Subagent contract**: Each subagent receives the scope, focus, and exclusion list. Each returns findings in the standard format: `F<n> [Type][Severity]: Title` with evidence, impact, and suggested fix.

## Phase 4 -- Score

1. Aggregate findings per dimension
2. Calculate health score (0-4) per dimension using SKILL.md criteria:
   - 4 (Excellent): no P0 or P1 findings, at most minor P2/P3
   - 3 (Good): no P0, at most 1-2 P1, minor P2/P3
   - 2 (Fair): no P0, multiple P1 or notable P2 issues
   - 1 (Poor): 1+ P0 or many P1 findings
   - 0 (Critical): multiple P0 findings or systemic failure
3. Record the key finding per dimension (most impactful issue for score card)
4. Calculate aggregate score (sum of 5 dimensions, max 20)
5. Assign rating band: 18-20 Excellent, 14-17 Good, 10-13 Acceptable, 6-9 Poor, 0-5 Critical
6. Record the findings that justified each score
7. If a dimension could not be fully assessed, cap its max score at 2 and note the gap

## Phase 5 -- Findings

1. Merge all findings from scan, deep dive, and subagents
2. Deduplicate overlapping findings across sources
3. Assign final severity: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
4. Tag effort: quick-win, planned, strategic
5. Order by severity, then by effort (quick-wins first within each severity)
6. Assign stable IDs: F1, F2, F3, ...

## Phase 6 -- Report

1. Write executive summary (2-3 sentences covering overall health and top risks)
2. Render health score card as a table
3. Present findings grouped by severity with stable IDs
4. List recommended actions with priority, effort, and dimension tags
5. State blind spots: dimensions not assessed, areas needing runtime verification
6. Offer next steps: re-audit after fixes, deeper dive into specific dimension, related skills

## Validation Rules

- Every finding references code, config, or tool evidence
- Severity and priority are explicit on every finding
- Recommendations are scoped and actionable (not vague "improve this")
- Blind spots and untested areas appear in the final report
- Health scores are traceable to the findings that produced them
- Subagent findings are attributed to their source
- Duplicate findings across sources are merged, not repeated
