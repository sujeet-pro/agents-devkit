# Review Comment Format

Standard format for all review and audit findings across ADK skills.
This file is the canonical source. Skills that produce review findings
copy this into their `references/review-comment-format.md`.

## Comment Structure

```
[Type][Severity]: Comment Title
Confidence: <low | medium | high> | Dimension: <dimension> | Scope: <scope>

Issue Summary:
Briefly explain the issue or observation. Include minimal, relevant
code snippets or document excerpts.

Why This Matters:
Explain the potential impact — maintainability risks, security
implications, architectural degradation, or performance effects.

Suggested Fix:
Provide a focused resolution path, alternative approach, or
improvement recommendation.

Verify / Clarify (optional):
Mention if external validation or product/platform input is required.
```

## Field Definitions

### Type


| Value        | Meaning                                                |
| ------------ | ------------------------------------------------------ |
| `Question`   | Seeks clarification or rationale                       |
| `Praise`     | Highlights well-executed code, design, or approach     |
| `Issue`      | Points out an error, bug, or violation of expectations |
| `Suggestion` | Proposes improvement but not mandatory                 |
| `NitPick`    | Minor cosmetic or non-functional tweak                 |


### Severity


| Value          | Meaning                                      | Merge Impact                    |
| -------------- | -------------------------------------------- | ------------------------------- |
| `Critical`     | Breaks functionality or introduces high risk | Must fix before merge           |
| `Blocker`      | Prevents merge or release until resolved     | Blocks merge                    |
| `Must Have`    | Important for quality                        | Fix recommended before approval |
| `Should Have`  | Fix desirable soon                           | Not merge-blocking              |
| `Nice to Have` | Low priority, optional improvement           | No merge impact                 |


### Dimension


| Value           | Applies To | Description                                  |
| --------------- | ---------- | -------------------------------------------- |
| `security`      | code, docs | Data exposure, auth flows, compliance        |
| `architecture`  | code       | Structural or design-level concerns          |
| `patterns`      | code       | Deviations from standard design principles   |
| `code-quality`  | code       | Readability, maintainability, testability    |
| `performance`   | code, site | Efficiency and resource utilization          |
| `documentation` | docs, code | Clarity and accuracy of written explanations |
| `accessibility` | site, UI   | Inclusivity and usability                    |
| `readability`   | code, docs | Naming, structure clarity, logical flow      |
| `correctness`   | code, docs | Factual accuracy and behavioral correctness  |
| `completeness`  | docs       | Missing sections, gaps in coverage           |
| `consistency`   | docs, code | Terminology, formatting, style uniformity    |
| `seo`           | site       | Search engine optimization                   |
| `content`       | site, docs | Quality and relevance of content             |


### Scope

The driving principle or system domain:

- Clean Code
- Performance Optimization
- Design System
- API Consistency
- Security Compliance
- Scalability
- Maintainability
- Test Coverage
- Error Handling
- Data Integrity

## Stable Finding IDs

Every finding gets a sequential ID for user interaction:

- `F1`, `F2`, `F3`, etc. within a single review session
- IDs are stable — they do not change when findings are reordered
- User references findings by ID: `a-1,3` (accept), `r-2` (reject), `e-4` (edit)

## Format by Context

### Code Review Findings (adk-review-pr, adk-review-local-changes)

```
F1 [Issue][Must Have]: Improper Token Handling in Auth Middleware
Confidence: high | Dimension: security | Scope: Security Compliance

Issue Summary:
The `verifyToken()` method in `src/middleware/auth.ts:42` does not
validate token expiration. Stale session tokens pass authorization.

Why This Matters:
Increases risk of unauthorized access and compromised user sessions.

Suggested Fix:
Add expiration validation using JWT claims:
  if (decoded.exp < Date.now() / 1000) throw new UnauthorizedError()

Verify / Clarify:
Confirm with platform team whether tokens auto-renew on refresh.
```

### Repository Audit Findings (adk-audit-repo)

```
F1 [Issue][Should Have]: N+1 Query Pattern in User Service
Confidence: high | Dimension: performance | Scope: Performance Optimization

Issue Summary:
`src/services/user.ts:78-92` fetches user roles in a loop inside
`getUsersWithRoles()`. Each iteration triggers a separate DB query.

Why This Matters:
Linear query growth with user count. At 1000 users, this generates
1001 queries instead of 2.

Suggested Fix:
Batch-load roles with a single `WHERE user_id IN (...)` query.

Effort: quick-win (< 1 hour)
```

### Document Review Findings (adk-review-docs)

```
F1 [Issue][Must Have]: Outdated API Endpoint in Setup Guide
Confidence: high | Dimension: correctness | Scope: API Consistency

Issue Summary:
Section "Authentication" references `/api/v1/auth/login` but the
codebase shows the endpoint was moved to `/api/v2/auth/login` in
commit a3f8c2d (2026-03-15).

Why This Matters:
New developers following the guide will get 404 errors during setup.

Suggested Fix:
Update the endpoint to `/api/v2/auth/login` and add a note about
the v1 deprecation timeline.
```

### Site Audit Findings (adk-audit-site)

```
F1 [Issue][Critical]: Missing HTTPS Redirect
Confidence: high | Dimension: security | Scope: Security Compliance

Issue Summary:
http://example.com loads without redirecting to HTTPS. Mixed content
warnings appear on the login page.

Why This Matters:
Credentials transmitted in plaintext. Browsers flag the site as
insecure, reducing user trust.

Suggested Fix:
Add HTTP-to-HTTPS redirect at the load balancer or web server level.
Enforce HSTS header with min 1-year max-age.
```

## Consolidation Rules

When multiple findings affect the same location:

1. Group related findings under a single F-ID
2. Use the highest severity among the group
3. List each sub-issue as a bullet under the consolidated finding
4. Keep the finding actionable — one fix should address the group

## Summary Format

After all findings, present a summary:

```
---
Summary: N findings (X critical, Y must-have, Z suggestions)
Praise: N positive observations
Questions: N items needing clarification
```

