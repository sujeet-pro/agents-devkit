---
name: audit-security
description: Use when you need a deep security-focused code review covering OWASP Top 10, auth flows, data handling, secret detection, and dependency vulnerabilities
user_invocable: true
arguments:
  - name: scope
    description: "Audit scope: full, auth, data, dependencies (default: full)"
    required: false
  - name: format
    description: "Output format: markdown, pr (default: markdown)"
    required: false
---

# Security Audit

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

## Preflight

Before scanning the codebase or launching child agents, run:

`zsh scripts/check-skill-deps.zsh audit-security`

## Guideline Loading

Always load:

- `skills/_references/guidelines/coding/general.md`
- `skills/_references/guidelines/coding/backend-general.md`
- `skills/_references/guidelines/coding/security.md`

Load additional guidelines when the codebase includes frontend code:

- `skills/_references/guidelines/coding/frontend-nextjs.md`

## Required Child Agents

Run at least these child agents in parallel:

- **Auth reviewer** (when `scope` includes full or auth): analyzes authentication and authorization flows end-to-end. Reviews session management, token handling (JWT validation, expiration, refresh), password storage (hashing algorithm, salting), OAuth/OIDC implementation, RBAC/ABAC enforcement, and privilege escalation vectors.
- **Data flow analyzer** (when `scope` includes full or data): traces sensitive data through the application from input to storage to output. Checks for injection vulnerabilities (SQL, NoSQL, command, LDAP, XPath), XSS vectors, CSRF protection, insecure deserialization, sensitive data exposure in logs or error messages, and encryption at rest and in transit.
- **Dependency scanner** (when `scope` includes full or dependencies): scans dependency manifests for known CVEs using advisory databases. Checks for dependencies with known security issues, abandoned packages with unpatched vulnerabilities, and typosquatting risks. Complements `/devkit:audit-dependency` with a security-specific lens.
- **OWASP checker**: systematically reviews the codebase against the OWASP Top 10 categories. For each category, identifies specific code patterns and configurations that indicate vulnerability. Uses `/devkit:research` with `depth=standard` to research current attack vectors relevant to the detected technology stack.

## Workflow

1. **Detect attack surface.** Scan the repository to identify:
   - Public-facing endpoints and APIs
   - Authentication and authorization entry points
   - File upload and download handlers
   - External service integrations
   - Database interaction layers
   - User input processing paths
   - Configuration and secrets management

2. **Review authentication and authorization** (when `scope` includes full or auth):
   - Authentication mechanism implementation and configuration
   - Session management (creation, validation, expiration, invalidation)
   - Token handling (JWT claims validation, signature verification, expiration)
   - Password policy enforcement and storage (bcrypt/scrypt/argon2)
   - Multi-factor authentication implementation when present
   - OAuth/OIDC flow correctness
   - Role and permission checks on every protected endpoint
   - Privilege escalation paths (horizontal and vertical)

3. **Trace data flows** (when `scope` includes full or data):
   - Input validation and sanitization at every entry point
   - SQL/NoSQL query construction (parameterized vs. concatenated)
   - Command execution patterns (shell injection vectors)
   - HTML/JavaScript rendering (XSS: reflected, stored, DOM-based)
   - CSRF token implementation and validation
   - Sensitive data in URLs, logs, error messages, or client-side storage
   - Encryption usage: TLS configuration, data at rest, key management
   - PII handling and data retention patterns

4. **Scan dependencies** (when `scope` includes full or dependencies):
   - Known CVEs in direct and transitive dependencies
   - Dependency age and maintenance status
   - Lock file integrity and reproducibility
   - Supply chain risks (post-install scripts, unpinned versions)

5. **OWASP Top 10 systematic check.** For each applicable category:
   - A01: Broken Access Control
   - A02: Cryptographic Failures
   - A03: Injection
   - A04: Insecure Design
   - A05: Security Misconfiguration
   - A06: Vulnerable and Outdated Components
   - A07: Identification and Authentication Failures
   - A08: Software and Data Integrity Failures
   - A09: Security Logging and Monitoring Failures
   - A10: Server-Side Request Forgery (SSRF)

6. **Secret detection.** Scan the repository and git history for:
   - Hardcoded credentials, API keys, and tokens
   - Private keys and certificates
   - Database connection strings with embedded passwords
   - `.env` files committed to version control
   - Secrets in CI/CD configuration files

7. **Classify and prioritize findings.** Rate each finding:
   - **Severity**: Critical, High, Medium, Low, Informational
   - **Exploitability**: Easy, Moderate, Difficult
   - **Impact**: Data breach, Service disruption, Privilege escalation, Information disclosure
   - **Confidence**: Confirmed, Likely, Possible

8. **Generate report.** Merge child agent outputs into the final security report.

Save intermediary artifacts to `.temp/security-audit/`.

## Output

A security audit report containing:

- **Executive Summary**: overall security posture with critical findings count and top recommendations
- **Attack Surface Map**: entry points, authentication boundaries, and data flow overview
- **Findings by Severity**: each finding with:
  - Severity and OWASP category
  - Affected file(s) and line references
  - Description of the vulnerability
  - Proof of concept or exploitation scenario
  - Recommended fix with code example
  - References (CWE ID, OWASP link, CVE when applicable)
- **OWASP Top 10 Coverage**: assessment status for each category with findings or clean bill
- **Dependency Vulnerabilities**: CVE list with affected packages and remediation
- **Secret Detection Results**: any exposed secrets with location and recommended rotation
- **Recommendations**: prioritized remediation plan ordered by severity and exploitability
- **Positive Findings**: security controls that are correctly implemented (to preserve during remediation)

When `format=pr`, structure the output as a PR description with a severity-ordered checklist of remediation tasks.
