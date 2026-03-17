# Coding Guidelines Document Guidelines

## 1. Purpose & Audience

This guideline defines how to write and review documents that establish coding standards for a team or organization. A coding guidelines document turns implicit conventions into explicit, enforceable rules that improve code consistency, reduce review friction, and catch defects early.

**Primary audience:** Engineers authoring coding guidelines, tech leads establishing team standards, and platform teams building enforcement tooling.

**When to use:** When creating or revising coding standards for a language, framework, or codebase.

## 2. Required Sections

Every Coding Guidelines Document must include the following sections:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Scope & Applicability | What code, languages, and teams this document covers |
| 2 | Language/Framework Coverage | Which languages and frameworks have rules, and version ranges |
| 3 | Rule Categories | Logical groupings of rules with severity levels |
| 4 | Rules (using standard format) | Individual rules with ID, rationale, examples, and exceptions |
| 5 | Enforcement Strategy | How rules are checked: linters, CI, code review |
| 6 | Exception Process | How to request and document deviations from rules |
| 7 | Versioning & Change Management | How the guidelines evolve over time |

## 3. Content Standards

### 3.1 Scope Must Be Precise

State exactly what is covered and what is not:

Bad: "These guidelines apply to our codebase."
Good: "These guidelines apply to all TypeScript and Python code in the `backend/` and `shared/` directories. They do not apply to generated code, vendored dependencies, or migration scripts. Rules apply starting from TypeScript 5.0+ and Python 3.11+."

### 3.2 Rule Categories Must Have Severity Levels

Organize rules into categories and assign each rule a severity:

| Severity | Meaning | Enforcement | Merge Blocking? |
|----------|---------|-------------|----------------|
| Error | Must fix. Violation introduces bugs, security issues, or major inconsistency | Automated (linter/CI) | Yes |
| Warning | Should fix. Violation hurts readability or maintainability | Automated + review | Yes, unless exception granted |
| Advisory | Consider fixing. Best practice that improves code quality | Code review only | No |

Common rule categories:

- **Naming conventions** — Variables, functions, classes, files, constants
- **Error handling** — How errors are caught, logged, propagated
- **Code organization** — File structure, module boundaries, import ordering
- **Type safety** — Type annotations, null handling, generic usage
- **Testing** — Test naming, structure, coverage expectations
- **Security** — Input validation, secret handling, dependency policies
- **Performance** — Known anti-patterns, resource management

### 3.3 Every Rule Must Follow the Standard Format

Each rule must include all of the following fields:

- **Rule ID:** Unique, stable identifier (e.g., `TS-ERR-003`). Never reuse IDs.
- **Severity:** Error, Warning, or Advisory
- **Category:** Which category this rule belongs to
- **Description:** One sentence stating the rule
- **Rationale:** Why this rule exists. "Because we said so" is never acceptable. Explain the defect, inconsistency, or maintenance problem the rule prevents.
- **Good example:** Code that follows the rule, with a brief annotation
- **Bad example:** Code that violates the rule, with annotation explaining the problem
- **Exceptions:** When it is acceptable to violate this rule (or "None" if no exceptions)
- **Enforcement:** How this rule is checked (linter rule name, CI check, manual review)

Example rule:

> **TS-ERR-003** | Error | Error Handling
> **Description:** Never use empty catch blocks.
> **Rationale:** Empty catch blocks silently swallow errors, making failures invisible and debugging extremely difficult.
> **Good:** Catch block logs the error and re-throws with context.
> **Bad:** Catch block is empty or contains only a comment.
> **Exceptions:** None.
> **Enforcement:** ESLint rule `no-empty` (error level), CI blocks merge.

### 3.4 Both Good and Bad Examples Are Mandatory

Every rule must show at least one **good example** and one **bad example** with brief annotations. For rules where the boundary is subtle, include a **borderline example** explaining which side it falls on.

### 3.5 Enforcement Must Be Automated Where Possible

For each rule, define how it is enforced:

| Enforcement Level | When to Use | Examples |
|-------------------|-------------|---------|
| Automated (CI) | Rule is objectively checkable | Linter rules, format checks, type checking |
| Automated + Review | Automated check exists but edge cases need human judgment | Complexity thresholds, naming patterns |
| Manual review only | Rule requires contextual understanding | Architecture decisions, API design choices |

Target: at least 70% of Error-severity rules should have automated enforcement. If a rule cannot be automated, document why.

### 3.6 Exception Process Must Be Documented

Rules without an exception process become either ignored or resented. Define:

- **How to request an exception:** Where to file it (PR comment, issue, RFC)
- **What to include:** The rule ID, why it does not apply, what alternative was chosen
- **Who approves:** Role or specific person
- **How to mark the exception in code:** Suppression comment format (e.g., `// guideline-exception: TS-ERR-003 — reason`)
- **Expiration:** Whether exceptions are permanent or require periodic re-approval

### 3.7 Versioning Must Track Changes

Coding guidelines are living documents. Define:

- **Version numbering:** Semantic versioning recommended (major = breaking rule changes, minor = new rules, patch = clarifications)
- **Change process:** How new rules are proposed, reviewed, and adopted
- **Grace period:** How long teams have to comply with new rules (e.g., 2 sprints for Warnings, 1 sprint for Errors)
- **Changelog:** Every version must have a dated changelog entry listing added, changed, and removed rules by ID

## 4. Structure & Flow

1. **Scope first** — Readers need to know immediately whether this document applies to them.
2. **Categories and severity overview** — Establish the framework before listing individual rules.
3. **Rules grouped by category** — Within each category, order by severity (Error first, then Warning, then Advisory).
4. **Enforcement after rules** — Readers understand what is enforced after they know the rules.
5. **Exception process near the end** — Referenced as needed, not the first thing people read.
6. **Versioning last** — Governance of the document itself.

Keep rules scannable. Use consistent formatting so engineers can quickly find the rule ID, severity, and enforcement method.

## 5. Common Issues

| Issue | Problem | Fix |
|-------|---------|-----|
| Rules without rationale | Engineers ignore rules they do not understand | Every rule must explain the defect or problem it prevents |
| Missing examples | Ambiguous interpretation, inconsistent enforcement | Require both good and bad examples for every rule |
| All rules are "Error" severity | No prioritization, teams become numb to warnings | Use all three severity levels; reserve Error for genuine defect risks |
| No automated enforcement | Rules exist on paper but not in practice | Map each rule to a linter config or CI check where possible |
| No exception process | Engineers suppress warnings globally or ignore rules | Define a lightweight exception request and approval flow |
| Stale guidelines | Rules reference deprecated patterns or old library versions | Require quarterly review and version the document |
| Rules contradict each other | Two rules give conflicting guidance for the same situation | Cross-reference related rules and test for conflicts during review |
| No grace period for new rules | Existing code immediately violates new rules, creating noise | Define a compliance timeline and apply new rules to new code first |

## 6. Review Checklist

Before publishing a Coding Guidelines Document, verify every item:

- [ ] Scope explicitly states which languages, frameworks, directories, and teams are covered
- [ ] Language and framework versions are specified
- [ ] Rule categories are defined with clear severity levels (Error, Warning, Advisory)
- [ ] Every rule has a unique, stable ID that will not be reused
- [ ] Every rule includes a rationale explaining the "why," not just the "what"
- [ ] Every rule has at least one good example and one bad example with annotations
- [ ] Severity is appropriate: Error for defects/security, Warning for maintainability, Advisory for best practices
- [ ] At least 70% of Error-severity rules have automated enforcement (linter or CI)
- [ ] Each rule's enforcement method is specified (linter rule name, CI check, or manual review)
- [ ] Exception process defines how to request, approve, mark, and optionally expire exceptions
- [ ] Document uses semantic versioning with a dated changelog
- [ ] Change process defines how new rules are proposed, reviewed, and adopted
- [ ] Grace period is defined for new rules applied to existing code
- [ ] No two rules contradict each other for the same scenario
- [ ] Document has a version number and last-updated date
