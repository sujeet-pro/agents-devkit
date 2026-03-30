# Security Audit Stage

This stage is loaded when `--focus` includes `security` or defaults to `all`.

## Scope

Deep security-focused code review covering OWASP Top 10, auth flows, data handling, secret detection, and dependency vulnerabilities.

## Required Child Agents

Run at least these child agents in parallel:

- **auth-reviewer**: authentication and authorization flows, session management, JWT handling. Checks for missing auth guards, privilege escalation paths, token expiry, and session fixation.
- **data-flow-analyzer**: traces sensitive data through the system, checks encryption at rest and in transit, logging of sensitive fields, exposure through APIs or error messages, and PII handling.
- **dependency-scanner**: checks for known CVEs, GitHub Security Advisories, and ecosystem-specific advisories for each dependency. Classifies findings by severity (Critical, High, Medium, Low).
- **owasp-checker**: systematic OWASP Top 10 review against the codebase. Checks injection, broken auth, sensitive data exposure, XML external entities, broken access control, security misconfiguration, XSS, insecure deserialization, known vulnerabilities, and insufficient logging.

## Workflow

1. **Detect technology stack.** Identify frameworks, languages, and runtime to determine which security checks are relevant.
2. **Load coding guidelines.** Invoke `/coding` to detect repo frameworks and load matching coding guidelines.
3. **Scan authentication flows.** Trace auth paths from entry points through middleware to protected resources. Check for missing guards, weak token handling, and session management issues.
4. **Trace data flows.** Map sensitive data from input to storage to output. Check encryption, sanitization, logging, and exposure at each boundary.
5. **Check OWASP Top 10.** Systematically evaluate the codebase against each OWASP Top 10 category with framework-specific checks.
6. **Scan dependencies.** Check all dependencies against known CVE databases and advisory sources. Flag critical and high severity vulnerabilities.
7. **Detect secrets.** Scan for hardcoded secrets, API keys, tokens, and credentials in source code, configuration files, and environment files.
8. **Synthesize findings.** Merge all child agent results, deduplicate, and produce the final report sections ordered by severity.

## Output Sections

- **Executive Summary**: overall security posture with critical findings count
- **OWASP Top 10 Assessment**: findings organized by OWASP category with severity and remediation
- **Authentication & Authorization**: auth flow issues, missing guards, token handling
- **Data Handling**: encryption gaps, PII exposure, logging of sensitive data
- **Secret Detection**: hardcoded secrets, exposed credentials, insecure configuration
- **Dependency Vulnerabilities**: CVEs by severity with affected packages and fix versions
- **Remediation Plan**: findings ordered by severity with concrete fix steps

When `--format pr`, structure the output as a PR description with a severity-ordered checklist of remediation tasks.
