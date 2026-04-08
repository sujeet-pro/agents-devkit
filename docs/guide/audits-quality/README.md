---
title: Audits & Quality
description: Run security, performance, dependency, and codebase audits with automated testing
order: 6
---

# Audits & Quality

ADK provides specialized audit capabilities for security, performance, dependency, and codebase quality. All audit skills are **read-only** — they produce findings and recommendations without modifying code.

## Scenarios

- [Run a security audit](#run-a-security-audit)
- [Run a performance audit](#run-a-performance-audit)
- [Audit dependencies](#audit-dependencies)
- [Full codebase audit](#full-codebase-audit)
- [Scoped audits](#scoped-audits)
- [User acceptance testing](#user-acceptance-testing)

---

## Run a Security Audit

Focus the audit on security vulnerabilities, injection points, authentication flaws, and data exposure:

```text
/adk:audit --focus security
```

The security audit checks for:

- SQL injection, XSS, CSRF vulnerabilities
- Authentication and authorization flaws
- Secrets and credentials in code
- Insecure dependencies
- Data exposure and privacy issues

### Scoped security audit

```text
/adk:audit --focus security --scope src/api/
```

---

## Run a Performance Audit

Identify performance bottlenecks, inefficient queries, memory leaks, and optimization opportunities:

```text
/adk:audit --focus performance
```

### Scoped performance audit

```text
/adk:audit --focus performance --scope src/services/
```

---

## Audit Dependencies

Check for outdated, vulnerable, or unused dependencies:

```text
/adk:audit --focus dependency
```

This analyzes:

- Known vulnerabilities (CVEs) in dependencies
- Outdated packages with available updates
- Unused dependencies that can be removed
- License compatibility issues

---

## Full Codebase Audit

Run all audit dimensions at once:

```text
/adk:audit --focus all
```

Or let ADK auto-detect the most relevant focus from your request:

```text
/adk:audit review this codebase for quality and security issues
```

---

## Scoped Audits

Limit the audit to specific directories:

```text
/adk:audit --focus codebase --scope src/
/adk:audit --focus security --scope src/auth/
```

### Output format

```text
/adk:audit --focus all --format markdown   # Default: structured markdown report
/adk:audit --focus all --format pr         # PR comment format for posting findings
```

### Publishing findings

```text
/adk:audit --focus security --publish
```

### Verbosity

```text
/adk:audit --focus all --verbosity short     # Executive summary only
/adk:audit --focus all --verbosity detailed  # Full findings with code snippets
```

---

## User Acceptance Testing

Use `test` for interactive user acceptance testing (UAT) based on specs, plans, or deliverables:

```text
/adk:test ./docs/specs/auth-spec.md
```

### How it works

1. Extracts testable deliverables from the source document
2. Generates test scenarios and acceptance criteria
3. Walks you through each test interactively
4. On failure: runs automated diagnosis patterns
5. Produces a test report

### Scoped testing

```text
/adk:test ./docs/specs/auth-spec.md --scope "login flow"
```

### Auto-approve mode

```text
/adk:test ./docs/specs/auth-spec.md --mode auto-approve
```

---

## Which Skill to Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Security audit | `audit` | `--focus security`, `--scope` |
| Performance audit | `audit` | `--focus performance`, `--scope` |
| Dependency audit | `audit` | `--focus dependency` |
| Full codebase audit | `audit` | `--focus all`, `--format` |
| Auto-detect audit focus | `audit` | (keywords auto-detected) |
| User acceptance testing | `test` | `<source>`, `--scope`, `--mode` |

## Related Skills

- **[`code-review-repo`](/reference/skill-code-review-repo/)** — whole-repo code review (overlaps with codebase audit)
- **[`dev-build --mode debug`](/reference/skill-dev-build/)** — fix issues found during audits
- **[`code-review-fix`](/reference/skill-code-review-fix/)** — fix review comments
