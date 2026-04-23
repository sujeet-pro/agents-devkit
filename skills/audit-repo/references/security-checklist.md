# Security checklist — repo audit

Optional reference loaded by `audit-repo` when the audit covers security (default). Concrete, scoped checklist a senior security engineer would run on a code repo. Each item maps to OWASP Top 10 (2021).

## Pre-commit hygiene

- [ ] No secrets in the repo: `git log -p | rg -i 'password|secret|api[_-]?key|token|private[_-]?key|BEGIN (RSA|EC|OPENSSH) PRIVATE KEY' | head -20` should be empty.
- [ ] No `.env` / `.env.local` checked in (`.gitignore` includes them).
- [ ] No personal credentials in fixtures / test data.
- [ ] Repo's secret scanner enabled (TruffleHog / GitLeaks / GitHub secret scanning).
- [ ] `npm audit --audit-level=high` (or `pip-audit`, `cargo audit`, `bundle audit`) is clean or has documented exceptions.

## Authentication (A07)

- [ ] Passwords hashed with bcrypt (≥ 12 rounds) / argon2id / scrypt — never MD5 / SHA1 / plain SHA256.
- [ ] Login throttling: ≤ 10 attempts / 15 min per IP+username; returns 429 + `Retry-After`.
- [ ] Password-reset tokens: ≥ 256 bits entropy, ≤ 1 hour TTL, single-use.
- [ ] MFA available for admin / privileged accounts.
- [ ] Session token storage: httpOnly + secure + sameSite=Lax/Strict cookie. NEVER `localStorage` for SPAs.
- [ ] Session rotation on privilege change (login, password change, role change).
- [ ] Account-enumeration resistance: same response time + same wording for "user not found" vs "wrong password".
- [ ] Vetted auth library used (not homegrown).

## Authorization (A01)

- [ ] Default-deny on protected routes.
- [ ] Per-action authz check (`can(user, action, resource)`), not "they got past auth so they're trusted".
- [ ] Resource-level / tenant-level scoping enforced (no `WHERE id = req.params.id` without `AND tenant_id = req.user.tenant_id`).
- [ ] No IDs from URL trusted as authority (verify ownership).
- [ ] Privilege escalation paths reviewed (admin invite, role change, impersonation).

## Input validation (A03)

- [ ] All untrusted inputs validated at the edge (Zod / Pydantic / Joi / OpenAPI middleware).
- [ ] Validation is at ONE layer (the edge), not duplicated deep in the call stack.
- [ ] Parameterized queries / prepared statements / ORM bindings — never string-concat user input into SQL / NoSQL / LDAP / shell / template.
- [ ] File uploads: type allowlist, size limit, name normalization, served from a separate origin if rendered.
- [ ] URL allowlist for SSRF-relevant outbound calls (block link-local / private ranges).
- [ ] Path-traversal prevention on filesystem reads (`path.resolve` + boundary check).

## Output handling (A03 / XSS)

- [ ] HTML output auto-escaped by templating engine (no raw `{{{...}}}` / `dangerouslySetInnerHTML` without sanitization).
- [ ] DOMPurify (or equivalent) for any user-provided HTML.
- [ ] No `eval` / `new Function(userInput)` / dynamic `require(userInput)`.
- [ ] CSV / SVG / JSON-in-HTML treated as untrusted on output.

## Security headers (A05)

- [ ] `Content-Security-Policy` set, `default-src 'self'`, no `'unsafe-inline'`/`'unsafe-eval'` without scoped justification.
- [ ] `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`.
- [ ] `X-Content-Type-Options: nosniff`.
- [ ] `X-Frame-Options: DENY` (or framing controlled by CSP `frame-ancestors`).
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`.
- [ ] `Permissions-Policy` minimized to features actually used.
- [ ] No `Server: …` / `X-Powered-By: …` revealing framework versions.

## CORS

- [ ] Origin allowlist (no wildcard `*`).
- [ ] If `Access-Control-Allow-Credentials: true`, origin MUST be a specific allowlisted value, not `*`.
- [ ] Preflight cached with `Access-Control-Max-Age` reasonable.
- [ ] Methods + headers minimized to what's actually used.

## Data protection (A02)

- [ ] TLS for all transit (no plain HTTP for app endpoints).
- [ ] Encryption at rest for PII / payment / tokens.
- [ ] Secrets in a secret manager (Vault, AWS Secrets Manager, Doppler), not env files committed to ops repo.
- [ ] Logs scrubbed for PII / tokens / Authorization headers.
- [ ] Request IDs in logs; full payloads NOT.

## Dependency security (A06)

- [ ] Lockfile committed (`package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`, `Pipfile.lock`).
- [ ] Dependabot / Renovate configured with weekly updates.
- [ ] CVE scanning in CI (`npm audit --audit-level=high` or Snyk / OSV-Scanner).
- [ ] No abandoned deps (no commits in 24+ months without a documented exception).
- [ ] No deprecated transitive deps showing on install.

## Error handling (A05 / A09)

- [ ] Generic `INTERNAL_ERROR` envelope at the edge — no stack traces, SQL fragments, internal paths, env vars in 5xx responses.
- [ ] Logs include enough context to diagnose (request ID, user ID, action, resource); not enough to leak (no full payloads with PII).
- [ ] Auth events logged: login success, login failure, password reset, MFA challenge, session refresh.
- [ ] Authz denials logged with enough context to detect probing.

## Rate limiting & abuse

- [ ] Login + password-reset + signup endpoints rate-limited.
- [ ] Expensive endpoints (search, export, report) rate-limited.
- [ ] 429 responses include `Retry-After`.
- [ ] Webhook receivers verify HMAC signature.
- [ ] CSRF: SameSite cookies OR Synchronizer-Token; never disabled.

## Software supply chain (A08)

- [ ] CI actions pinned to SHA, not version tag.
- [ ] Reproducible builds where possible.
- [ ] SBOM generated for releases.
- [ ] Signed releases (Sigstore / `gh attestation`).
- [ ] Branch protection on main (required reviews, required CI, signed commits if used).

## OWASP Top 10 (2021) — quick reference

| # | Category | Look for |
| --- | --- | --- |
| A01 | Broken Access Control | URL ID trust, missing tenant scoping, IDOR |
| A02 | Cryptographic Failures | Plain HTTP, weak hashing, hardcoded keys, ECB |
| A03 | Injection | SQL/NoSQL/LDAP/Shell/SSTI/XSS, missing edge validation |
| A04 | Insecure Design | No threat model, no rate limit, no defense in depth |
| A05 | Security Misconfiguration | Missing headers, default creds, verbose errors |
| A06 | Vulnerable Components | Outdated deps, no audit in CI, abandoned deps |
| A07 | Identification & Auth Failures | Weak password policy, no throttling, weak session mgmt |
| A08 | Software & Data Integrity Failures | Unsigned packages, unverified webhooks, unpinned actions |
| A09 | Security Logging & Monitoring Failures | No auth-event logging, no alerting, no log retention |
| A10 | SSRF | Unfiltered outbound URLs, no allowlist, no metadata-IP block |
