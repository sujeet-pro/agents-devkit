# Constitution Write

This stage creates, updates, or audits a versioned project constitution -- the set of non-negotiable principles and quality gates that all downstream work must comply with. The constitution is the highest-authority governance document in a project and takes precedence over specs, plans, and implementation decisions.

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Understand requirements, scan existing plans and context; Focused research on chosen approach, proposal at .temp/proposal/ |
| 2. Approach Selection | yes | Present 2-3 approaches, user picks or mixes; Iterate on proposal with user feedback |
| 3. Planning | yes | Break into tasks/waves for parallel agentic teams |
| 4. Execute | yes | Execute the planning workflow |
| 5. Validate & Learn | yes | Validate plan completeness and feasibility |

## Preflight

Before starting any constitution work, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If `.temp/project-init/` does not exist, create it and ensure `.temp/` is listed in `.gitignore`.

## Constitution Format

All constitutions follow this structure:

```markdown
---
constitution_version: 1.0.0
ratified: <ISO-8601>
last_amended: <ISO-8601>
---
# Project Constitution

## Principles
### 1. <Principle Name>
<Description and rationale>

### 2. <Principle Name>
...

## Quality Gates
- <gate 1>
- <gate 2>

## Amendment History
| Version | Date | Change | Rationale |
|---------|------|--------|-----------|
| 1.0.0   | <date> | Initial ratification | -- |
```

## Versioning

Follow semantic versioning for the constitution:

- **MAJOR** (e.g., 1.0.0 -> 2.0.0): a new principle is added or an existing principle is removed.
- **MINOR** (e.g., 1.0.0 -> 1.1.0): an existing principle is edited or a quality gate is added/removed/changed.
- **PATCH** (e.g., 1.0.0 -> 1.0.1): clarification, typo fix, or formatting change with no semantic impact.

Always update `last_amended` and append to the Amendment History table on every version change.

## Storage

Save the constitution to `.temp/project-init/CONSTITUTION.md` by default. If a constitution already exists at the project root (e.g., `CONSTITUTION.md`), prefer that location for updates and audits.

When `--format` is `google-doc` or `confluence`, also publish to that platform after the markdown version is saved locally.

## Action: Create

Default action when no existing constitution is found.

### Phase 1: Codebase Discovery

Launch child agents in parallel to discover principles from the project:

- **Codebase analyst**: reads the project structure, configuration files, linting rules, CI pipelines, test setups, and existing documentation. Extracts implicit principles the project already follows (e.g., "all code must pass ESLint", "minimum 80% test coverage").
- **Pattern researcher**: examines code patterns, architectural decisions, dependency choices, and commit history to infer values the team prioritizes (e.g., "prefer composition over inheritance", "no direct database access outside the data layer").
- **Risk analyst**: identifies areas where the project lacks governance -- missing tests, inconsistent patterns, security gaps, accessibility omissions. Proposes principles that would close these gaps.

Merge results in the parent session: deduplicate overlapping findings, preserve minority opinions when they change risk assessment, and mark single-agent findings as lower confidence until corroborated.

If no codebase exists (greenfield project), skip codebase discovery and proceed directly to Phase 2 with general best-practice principles tailored to the project type from the user's description.

### Phase 2: Principle Proposal (Interactive)

Propose principles one at a time for user approval. Present 5-7 principles total, ordered by impact (highest first):

```text
## Principle [N/total]

Name: <principle name>
Description: <what it means>
Rationale: <why it matters>
Enforcement: <how other skills check compliance>

Action: [A]ccept | [E]dit | [R]eject | [A]dd new principle
```

#### Actions

- **Accept**: lock the principle into the constitution as-is.
- **Edit**: let the user revise the name, description, rationale, or enforcement. Stay in the edit loop until the user accepts or rejects the revised version.
- **Reject**: discard the principle entirely. It will not appear in the constitution.
- **Add new**: let the user propose a principle not suggested by the analysis. Prompt for name, description, rationale, and enforcement, then present it in the same format for confirmation.

#### Loop Rules

1. Process principles in impact order (highest first).
2. After all proposed principles are processed, ask if the user wants to add any additional principles.
3. If the user says "accept all remaining", lock all unprocessed principles.
4. If the user says "reject all remaining", discard all unprocessed principles.
5. A constitution must have at least 1 principle. If all are rejected, prompt the user to add at least one.

In `auto-approve` mode, present all principles as a consolidated list and accept them automatically.

### Phase 3: Quality Gates (Interactive)

Based on the accepted principles, propose quality gates that enforce them. Examples:

- Test coverage thresholds (unit, integration, e2e)
- Linting and formatting requirements
- Accessibility standards (WCAG level if applicable)
- Performance budgets (bundle size, response time, Core Web Vitals)
- Security requirements (dependency scanning, secret detection)
- Documentation standards (JSDoc, README, ADR)
- Review requirements (minimum approvals, required reviewers)

Present each gate for approval:

```text
## Quality Gate [N/total]

Gate: <gate description>
Enforces Principle: <which principle(s) this supports>
Verification: <how compliance is checked -- CI, linting, manual review>

Action: [A]ccept | [E]dit | [R]eject | [A]dd new gate
```

Actions follow the same pattern as Phase 2.

In `auto-approve` mode, present all gates as a consolidated list and accept them automatically.

### Phase 4: Ratification

Present the complete constitution for final review:

```text
## Constitution Draft

Version: 1.0.0
Principles: N
Quality Gates: N

<full constitution content>

Action: [R]atify | [E]dit section | [S]tart over
```

- **Ratify**: set `ratified` and `last_amended` to the current ISO-8601 timestamp, write the constitution to storage, and publish if a non-markdown format was requested.
- **Edit section**: return to Phase 2 or Phase 3 for targeted revisions, then return here.
- **Start over**: discard the draft and restart from Phase 1.

In `auto-approve` mode, ratify automatically.

## Action: Update

Used when an existing constitution is found and the user wants to amend it.

### Phase 1: Load Existing Constitution

Read the current constitution from storage. Parse the version number, principles, quality gates, and amendment history. Display a summary:

```text
## Current Constitution

Version: <current version>
Ratified: <date>
Last Amended: <date>
Principles: N
Quality Gates: N

<list of principle names>
```

### Phase 2: Amendment Proposal (Interactive)

Ask the user what they want to change, or launch child agents to suggest amendments based on:

- **Codebase drift analyst**: compares the constitution against current codebase state. Identifies principles that are no longer followed or gaps where new principles are needed.
- **Enforcement auditor**: checks whether quality gates are actually enforced in CI/CD, linting, and review processes. Flags gates with no enforcement mechanism.

Present each proposed amendment one at a time:

```text
## Amendment [N/total]

Type: [add principle | edit principle | remove principle | add gate | edit gate | remove gate]
Target: <principle or gate being changed>
Current: <current text, if editing or removing>
Proposed: <new text, if adding or editing>
Rationale: <why this change is needed>
Version Impact: <MAJOR | MINOR | PATCH>

Action: [A]ccept | [E]dit | [R]eject
```

#### Actions

- **Accept**: queue the amendment for application.
- **Edit**: let the user revise the proposed change. Stay in the edit loop until the user accepts or rejects.
- **Reject**: discard the amendment.

#### Loop Rules

1. Process amendments in order of version impact (MAJOR first, then MINOR, then PATCH).
2. If the user says "accept all remaining", queue all unprocessed amendments.
3. If the user says "reject all remaining", discard all unprocessed amendments.

In `auto-approve` mode, present all amendments as a consolidated list and accept them automatically.

### Phase 3: Version Bump and Ratification

Calculate the new version number based on the highest-impact accepted amendment:

- Any MAJOR amendment -> bump MAJOR, reset MINOR and PATCH.
- Any MINOR amendment (no MAJOR) -> bump MINOR, reset PATCH.
- Only PATCH amendments -> bump PATCH.

Present the updated constitution for final review:

```text
## Updated Constitution

Previous Version: <old>
New Version: <new>
Amendments Applied: N
Amendments Rejected: N

<full updated constitution content>

Action: [R]atify | [E]dit | [R]evert to previous version
```

- **Ratify**: update `constitution_version` and `last_amended`, append all accepted amendments to the Amendment History table, write to storage, and publish if requested.
- **Edit**: return to Phase 2 for further changes.
- **Revert**: discard all amendments and keep the existing version.

In `auto-approve` mode, ratify automatically.

## Action: Audit

Used to check existing code, plans, specs, or other artifacts against the constitution.

### Phase 1: Load Constitution and Targets

Read the current constitution from storage. If no constitution exists, stop and instruct the user to run `create` first.

Identify audit targets. If the user specified targets, use those. Otherwise, scan for:

- Specs in `.temp/specs/`
- Plans in `.temp/plans/`
- Source code in the project `src/` or equivalent directories
- CI/CD configuration files
- Package and dependency files

### Phase 2: Parallel Audit

Launch child agents to audit targets against the constitution:

- **Principle compliance auditor**: checks each artifact against every principle. Produces a compliance matrix showing pass/fail/partial for each principle-artifact pair.
- **Quality gate auditor**: verifies that each quality gate has an active enforcement mechanism and that current measurements meet the thresholds.
- **Drift detector**: identifies patterns in the codebase that contradict constitutional principles, even when individual files pass.

Merge results: deduplicate, assign severity (critical, high, medium, low), and confidence scores.

### Phase 3: Violation Report (Interactive)

Present each violation one at a time, ordered by severity (critical first):

```text
## Violation [N/total] - [severity: critical|high|medium|low]

Principle/Gate: <which principle or quality gate is violated>
Location: <file, spec, plan, or artifact where the violation occurs>
Confidence: NN%

Issue
<description of the violation>

Suggested Remediation
<how to fix the violation>

Action: [A]cknowledge | [W]aive | [D]ispute | [S]kip
```

#### Actions

- **Acknowledge**: mark the violation as confirmed; it will appear in the final report as requiring remediation.
- **Waive**: mark the violation as intentionally accepted. Prompt for a waiver rationale. Waivers appear in the report but do not count as open violations.
- **Dispute**: mark the violation as a false positive. Prompt for dispute rationale. Disputed items appear in the report separately.
- **Skip**: defer to the end. After all other violations are processed, return to skipped items for a final decision.

#### Loop Rules

1. Process violations in severity order (critical first).
2. If the user says "acknowledge all remaining", mark all unprocessed violations as confirmed.
3. If the user says "waive all remaining", prompt for a blanket waiver rationale and apply to all unprocessed violations.

In `auto-approve` mode, acknowledge all violations automatically.

### Phase 4: Audit Summary

Display the audit report:

```text
## Constitution Audit Report

Constitution Version: <version>
Audit Date: <ISO-8601>
Artifacts Audited: N

Compliance Summary:
- Principles Fully Met: N/N
- Principles Partially Met: N/N
- Principles Violated: N/N
- Quality Gates Passing: N/N
- Quality Gates Failing: N/N

Violations:
- Critical: N
- High: N
- Medium: N
- Low: N

Acknowledged (requires remediation): N
Waived: N
Disputed: N

Top Priority Remediations:
1. <most critical remediation>
2. <second most critical>
3. <third most critical>
```

Save the audit report to `.temp/project-init/CONSTITUTION-AUDIT-<ISO-8601-date>.md`.

## Mode Behavior

| Phase | `interactive` (default) | `auto-approve` |
|-------|------------------------|----------------|
| Create: Discovery | Full parallel analysis | Full parallel analysis |
| Create: Principles | One-by-one approval | Consolidated list, auto-accept |
| Create: Quality Gates | One-by-one approval | Consolidated list, auto-accept |
| Create: Ratification | Final review gate | Auto-ratify |
| Update: Load | Display summary | Display summary |
| Update: Amendments | One-by-one approval | Consolidated list, auto-accept |
| Update: Ratification | Final review gate | Auto-ratify |
| Audit: Violations | One-by-one triage | Auto-acknowledge all |
| Audit: Summary | Display report | Display report |
