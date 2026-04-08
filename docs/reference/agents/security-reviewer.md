---
title: "security-reviewer"
description: Security-focused code review covering OWASP, auth, data handling, dependencies
model: opus
---

# security-reviewer

Security-focused code reviewer covering OWASP Top 10, authorization patterns, data handling, and dependency vulnerabilities.

## Role

Analyzes code for security issues: injection vulnerabilities, authentication/authorization flaws, data exposure, insecure dependencies, and OWASP Top 10 compliance.

## Allowed Tools

Glob, Grep, Read, Bash, WebSearch, WebFetch

## Used By

- `audit` — security audit with sub-roles (auth-reviewer, data-flow-analyzer, dependency-scanner, owasp-checker, vulnerability-scanner)
- `code-review-pr` — security review dimension
