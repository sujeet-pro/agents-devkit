---
title: 'guidelines/security'
description: '1. **Validate at trust boundaries**, not internally. Boundary = where untrusted input enters trusted code.'
source: 'shared/guidelines/security.md'
group: 'shared-guidelines'
order: 6309
---
# shared/guidelines/security

> Source: `shared/guidelines/security.md`

# guideline: security

> Loaded when the task touches auth, authz, input handling, crypto, secrets, dependencies, deserialization, file uploads, or anything user-input-shaped.

## Hard rules

1. **Validate at trust boundaries**, not internally. Boundary = where untrusted input enters trusted code.
2. **Authenticate before authorize** — every endpoint. No "anyone can read" without explicit comment.
3. **Authorize at the object level**: never just `is_logged_in`; check `can_user_X_access_object_Y`.
4. **Secrets**: never in code, never in repo, never in error responses, never in logs. Use a secret manager / env var; rotate on leak.
5. **Crypto**: use well-known libs (libsodium, openssl, language stdlib). Never roll your own. SHA-256 or stronger for hashing; AES-GCM for symmetric; argon2id / bcrypt(cost=12+) for passwords.
6. **Dependencies**: monitor with the repo's scanner (Dependabot, Snyk, Trivy). Don't pin to compromised versions.

## Common defects (look for these, by category)

- **SQLi**: raw string concat into SQL. Use parameterized queries / ORM.
- **Command injection**: untrusted input into `shell=True`. Use exec with arg list, never shell.
- **XSS**: user content rendered as HTML without escape. Use the framework's escape by default; never `dangerouslySetInnerHTML` on user content.
- **SSRF**: server-side fetch with user-controlled URL. Allowlist host + scheme.
- **Path traversal**: user-controlled filename in fs path. Resolve + check `os.path.commonpath`.
- **IDOR**: user-controlled object id in URL with no per-user check. Always check object ownership.
- **Insecure deserialization**: `pickle.loads`, Java `ObjectInputStream`. Use JSON; sign tokens if you must.
- **Open redirect**: user-controlled `?redirect=...`. Allowlist target hosts.
- **CSRF**: state-changing GET, or POST without token. POST + same-site cookie + CSRF token.
- **Verbose errors**: stack traces in 5xx responses. Generic message + request_id; full trace in logs.

## Threat-model checklist (for new features)

1. Who can call this? (Anonymous / authenticated / role X / internal.)
2. What can they read / write / delete?
3. What's the worst case if they're malicious?
4. What's the worst case if they're confused / careless?
5. What does the audit log show afterward?

## Anti-patterns

- "Defensive code" for inputs already validated upstream. Pick a boundary and validate there.
- Custom auth/session. Use the framework's.
- Rolling JWT verification. Use a vetted lib; check `alg`, `exp`, `aud`, `iss`.
- Logging "user attempted X with input Y" where Y might include secrets. Sanitize.
- "Block by user-agent" or "block by referer". Trivially bypassed.

## Cite when reviewing

- OWASP top 10 mapping for the defect.
- The specific `path:line` of the unsafe sink.
- The relevant CVE if a known dep vuln.
- `api-design.md` if it's an endpoint authz issue.
