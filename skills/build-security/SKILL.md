---
name: build-security
description: |
  Implement a security-hardening change — input validation at the boundary, authn/authz fix, secrets handling, security header, CORS policy, dependency CVE patch, rate limit, CSRF/XSS/injection mitigation, file-upload hardening — using a three-tier boundary system (Always do / Ask first / Never do), OWASP Top 10 awareness, and pre-commit secret scanning. Different from `@adk:audit-repo` (a.k.a. `adk-audit-repo`) which finds and reports vulnerabilities, and from the `agents/security-reviewer.md` agent which reviews changes for security implications. Use when the deliverable is a code change that closes a known or suspected security gap. Do not use to do a full security audit (use `@adk:audit-repo`) or to triage an active incident (use `@adk:observability-incident` (a.k.a. `adk-observability-incident`)).
metadata:
  category: build
  kind: task
  layer: 4
  modes: [auto, fix]
---

# build-security — security hardening with explicit boundaries

Standalone task skill under the `@adk:build` (a.k.a. `adk-build`) category router. Closes security gaps with the smallest correct change, never weakens an existing protection, and adds a regression test where applicable.

## When to use

- Add input validation at a route / handler / message boundary.
- Replace a homegrown auth flow with a vetted library; rotate hashing scheme; enforce password policy.
- Add an authorization check (RBAC / row-level / tenant-scoped).
- Patch a CVE flagged by `npm audit` / `pip-audit` / `cargo audit` / Dependabot / Snyk.
- Add or fix a security header (CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`).
- Tighten or fix a CORS policy.
- Fix an XSS / SQL injection / SSRF / path traversal / SSTI / open redirect.
- Add rate limiting, login throttling, or password-reset token TTL.
- Harden a file upload (type allowlist, size limit, scan, separate origin).
- Remove a leaked secret + rotate the credential.

## When NOT to use

- Find vulnerabilities across the repo → `@adk:audit-repo` (a.k.a. `adk-audit-repo`).
- Review someone's PR for security gaps → `agents/security-reviewer.md` (called by `@adk:review-pr`).
- Active incident with credential leak / data exfiltration → `@adk:observability-incident` (a.k.a. `adk-observability-incident`) first; this skill handles the patch after.
- Web-app a11y / perf hardening → `@adk:build-perf` (a.k.a. `adk-build-perf`) / `@adk:frontend-feature` (a.k.a. `adk-frontend-feature`).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<gap>` | yes | What weakness is being closed (e.g. "no rate limit on /login", "CVE-2025-XXXXX in `package@x.y.z`", "missing CSP"). |
| `<source>` | yes | Where the gap was found: audit, advisory, pen-test, customer report, hunch with evidence. |
| `<scope>` | optional | Path filter for the change. |
| `--auto` | optional | Skip approval gates (still validates). |
| `--mode fix` | optional | Same as `auto` but no approval gate; intended for CI / `--auto` chains. |

## Workflow

1. **Confirm intent** — restate the gap, the source, and the proposed mitigation. Approval gate unless `--auto` or `--mode fix`. Classify against the **three-tier boundary** (see `references/three-tier-boundaries.md`):
   - **Always do**: just do it (input validation, parameterized queries, password hashing).
   - **Ask first**: notable change in posture (auth flow swap, CORS opening, rate-limit relaxation).
   - **Never do**: explicitly refuse (disabling CSRF/CSP, weakening password policy, hard-coding secrets, skipping authz).
2. **Reproduce or cite** — for vuln fixes: produce a failing security test or cite the advisory ID + version range. For preventive hardening: cite the OWASP item / CWE / threat-model entry.
3. **Pre-commit secret scan** — run `git diff --cached | grep -iE 'password|secret|api[_-]?key|token|private[_-]?key'` (or repo's secret-scan tool). If a secret is in the diff, STOP, rotate the credential, then redo the change without it.
4. **Plan the smallest correct fix** — pick from `references/owasp-patterns.md`. The fix MUST:
   - Validate at the boundary (edge), not deep in business logic.
   - Use vetted libraries for crypto/auth (no homegrown).
   - Default-secure (allowlist, not denylist; deny by default in authz).
   - Add a `Retry-After` to any rate-limit response.
   - Never weaken an existing protection without explicit approval.
5. **Implement** — smallest correct change. Touch ONLY the security-relevant code; security fixes that drag along refactors are harder to audit.
6. **Add a regression test** — a test that fails without the fix and passes with it (security test suite, fuzz test, header assertion, authz contract test).
7. **Validate** — repo-native typecheck + lint + tests; `npm audit` / equivalent shows the original CVE resolved; security headers verified (curl / `chrome-devtools` MCP); auth/authz contract tests pass.
8. **Report** — gap closed, mitigation applied, regression test added, residual security risk, follow-up items (e.g. "rotate prod credential separately", "add monitor for repeated 429s").

## Hard rules

- **Never weaken a protection** to make tests pass. Fix the test.
- **Validate once, at the edge.** Inner code trusts inner data.
- **Allowlists > denylists** for input, file types, origins, redirects.
- **Vetted libraries for crypto, auth, password hashing.** No homegrown.
- **Secrets never go in the diff.** Pre-commit grep is mandatory; repo secret scanning is the backstop.
- **A leaked secret is rotated, not just removed.** History is forever.
- **Authz checks are explicit and per-action.** No "they got past auth so they're trusted".
- **Generic error messages externally; specific logs internally.** Don't leak SQL, stack, or paths.
- **Rate limits return 429 with `Retry-After`.** Don't drop traffic silently.

## Anti-patterns

- Catching the exception and re-throwing a different one to "hide" the SQLi error → fix the query.
- Adding `cors({ origin: '*' })` to make local dev work → use a proper allowlist.
- Storing API tokens in `localStorage` for SPAs → httpOnly cookie, sameSite=Lax/Strict.
- Validating in the middle of business logic and again at the edge → keeps drifting; consolidate to the edge.
- "Disable CSP for one page" → list the specific source you need; don't disable the whole policy.
- Bumping a dep to fix a CVE without checking the changelog for breaking changes → run the test suite.
- Hashing passwords with MD5/SHA1/SHA256 → use bcrypt (≥ 12 rounds) / argon2id / scrypt.
- Returning 200 with `success: false` for auth failures → use 401/403 (preserves existing-resource-leak semantics).

## Examples

```
adk-build-security "Add input validation to POST /api/users (was passing raw body to ORM)" --source code-review-finding
```

```
adk-build-security "Patch CVE-2025-12345 in axios@1.6.x → 1.7.7" --source dependabot --mode fix
```

```
adk-build-security "Add CSP header excluding unsafe-inline; allow self + cdn.example.com" --source owasp-a05
```

```
adk-build-security "Add login rate limit: 10 per 15 min per IP, return 429 + Retry-After" --source threat-model-A07
```

## Clarifying questions (default-ask)

1. **What gap is being closed and what is the source of the finding?** — _How to pick:_ Reject vague "make it more secure"; require a specific weakness + a specific source (CVE, OWASP item, audit finding, threat-model entry).
2. **Three-tier classification — Always / Ask / Never?** — _How to pick:_ See `references/three-tier-boundaries.md`. If "Never", refuse and explain. If "Ask", run the approval gate even under `--auto`.
3. **Is there an existing similar protection elsewhere in the repo to match?** — _How to pick:_ Match the repo's existing pattern (validator, header set, error envelope) — uniformity is a security property.

## Default vs detailed output

**Default report:** Gap / source / mitigation / regression test / `npm audit` (or equivalent) status / residual risk / follow-up.

**Detailed report (on request or `--verbose`):** Add the OWASP / CWE mapping, the threat-model entry, the rejected mitigations and why, and a "what an attacker would do now" summary.

**Artifact:** `security-fix-bundle` — Code change + regression test + audit-tool clean output + (if applicable) credential-rotation checklist.

**Artifact path:** `.temp/notes/security-<slug>-mitigation.md` (mitigation log + audit output). Code lands in the repo proper.
