# `code-security` — threat-model template

The 5-line threat model in `threat-model.md` is the most-read document of the security task. Keep it short, specific, and falsifiable.

## Shape

EXACTLY 5 lines, in this order:

```
1. Untrusted input source: <where it enters>
2. Privileged action / output: <what the system does>
3. Asset at risk: <what's protected>
4. Threat actor: <who; access level>
5. Acceptable residual risk: <what attacker can still do after mitigation>
```

## Why 5 lines

- Forces specificity (vs. a 3-page "we should think about security" doc).
- Each line is a checkpoint; if you can't fill one, the threat is unclear.
- Reviewable in 30 seconds.

## Example 1 — SQL injection

```
1. Untrusted input: q parameter on GET /api/search.
2. Privileged action: SQL query against orders table.
3. Asset: orders table contents (incl. customer email + total).
4. Actor: unauthenticated external user.
5. Residual risk: parameterized queries are immune to SQL syntax injection. NoSQL-injection variants do not apply (PostgreSQL only). Side-channel timing attacks possible but out of scope.
```

## Example 2 — XSS

```
1. Untrusted input: HTML content in user-provided comment field on POST /api/comments.
2. Privileged action: rendering the comment in the HTML response served to other users.
3. Asset: other users' sessions / data via script execution in their browser.
4. Actor: authenticated user posting to a public-readable thread.
5. Residual risk: HTML escaping at output blocks reflected/stored XSS. DOM-based XSS via client-side templating is out of scope (client uses React with no dangerouslySetInnerHTML).
```

## Example 3 — Auth bypass (CVE patch)

```
1. Untrusted input: JWT in Authorization header on every authenticated endpoint.
2. Privileged action: granting authorization to act as the claimed user.
3. Asset: any user's session / data.
4. Actor: unauthenticated external user with a forged token.
5. Residual risk: the upgrade closes the algorithm-confusion path. Other JWT vulnerabilities (e.g. weak signing key, replay attacks) are not in scope for this task.
```

## Example 4 — File upload hardening

```
1. Untrusted input: multipart/form-data file + filename on POST /api/upload.
2. Privileged action: writing the file to S3 with the user-supplied filename; serving it back via /api/download/{filename}.
3. Asset: storage cost (DOS via large files); confidentiality (path traversal → access to other users' files); served-file safety (uploaded executables served back to other users).
4. Actor: authenticated external user.
5. Residual risk: AV scanning is out of scope. We accept that legitimate-looking files may contain malicious content (e.g. encoded PDFs).
```

## Example 5 — CSRF

```
1. Untrusted input: cross-origin POST to /api/account/email-change carrying the user's session cookie.
2. Privileged action: changing the user's email (account takeover vector).
3. Asset: the user's account (the new email becomes the password-recovery target).
4. Actor: malicious site the user visits while logged into our app.
5. Residual risk: SameSite=Strict cookie + CSRF token at the boundary blocks the standard CSRF; clickjacking via iframe is mitigated by X-Frame-Options DENY. SSRF / TOCTOU / token leakage are out of scope.
```

## Example 6 — rate limiting

```
1. Untrusted input: POST /api/auth/login with username + password.
2. Privileged action: authenticating; on success, issuing a session.
3. Asset: any user's session / account.
4. Actor: unauthenticated external user (running a credential-stuffing script).
5. Residual risk: rate-limit by IP can be circumvented with a botnet (distributed low-rate attack). Account-lockout is the deeper defense; out of scope.
```

## Example 7 — secrets handling

```
1. Untrusted input: log-line content from various code paths.
2. Privileged action: writing log lines to stdout (which feeds a log aggregator).
3. Asset: secrets (API keys, tokens, passwords) that may appear in log lines.
4. Actor: anyone with read access to the log aggregator (currently: ops team + on-call rotation).
5. Residual risk: pattern-based secret redaction in the log middleware catches common shapes (Bearer tokens, AWS keys). Custom-shaped secrets (e.g. internal token formats) require explicit redaction rules; out of scope until inventoried.
```

## Anti-examples (bad threat models)

| Wrong shape | Why it's wrong |
| --- | --- |
| `1. Various inputs. 2. Various actions. 3. User data. 4. Bad guys. 5. Some risk.` | Vague. Specifically what input, action, asset, actor, risk? |
| `1. SQL injection.` (single line, no other slots) | Missing 4 slots. |
| `1. The /api/search endpoint is vulnerable. 2. … 3. … 4. … 5. …` | Slot 1 should describe the input source, not the entire vulnerability. |
| `5. None.` | No mitigation has zero residual risk; specify what's still possible. |

## When residual risk is high

If the residual risk is high (the mitigation only covers a small part of the threat), say so explicitly:

```
5. Residual risk: this mitigation closes ONLY the GET /api/search path. POST /api/search-export has the same SQL injection signature and is NOT addressed in this task. Spawn a follow-up `code-security` for that path. Recommended priority: high.
```

The follow-up gets a separate `code-security` task.

## When threat actor changes mid-design

The actor in slot 4 affects the right mitigation. Examples:

- **Unauthenticated external user**: rate-limits, public-API hardening, CSRF / XSS, SSRF.
- **Authenticated user**: authz checks (per-user data scoping), tenant isolation.
- **Authenticated admin**: rare; admin-tier audit logging.
- **Insider**: usually out of scope for `code-security`; mitigate with org-process controls (least privilege, audit trails).
- **Supply-chain**: dependency CVE handling, lockfile integrity, SLSA-level builds.

If the actor is ambiguous (could be any of the above), pick the most-conservative (the one with least access) for the threat model; mitigations that cover that actor usually cover the others.

## When the threat is one of "the OWASP Top 10"

For canonical attack classes, the threat model can lean on the OWASP cheat sheet for slot 5:

```
5. Residual risk: per OWASP XSS Prevention Cheat Sheet, output encoding via React's auto-escaping covers stored / reflected XSS. DOM-based XSS prevented by avoiding dangerouslySetInnerHTML (verified via lint rule `react/no-danger`). Out of scope: third-party scripts; CSP nonce strategy.
```

That's still 1 line — citing the cheat sheet for context, not pasting it.
