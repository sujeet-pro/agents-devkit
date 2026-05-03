# `code-security` — anti-patterns

## Security theater

- **`app.use(helmet())`** added without identifying which header matters. Helmet enables ~12 headers; some are valuable (HSTS, X-Frame-Options) but most don't apply to your threat. Name the threat; pick the matching header.
- **Adding `Content-Security-Policy: default-src 'self'`** without testing that the app actually works under it. Frequently this breaks the app silently and the operator opens it back up to `*` during the next firefight.
- **"Validating" with `if (!input) return;`** — that's a presence check, not a validation.
- **Hashing a password with `md5()`** — unbroken in the 1990s; broken now. Use bcrypt / scrypt / argon2.
- **Generating a "token" with `Math.random()` (Node) or `random.random()` (Python)** — not cryptographically random. Use `crypto.randomBytes` / `secrets.token_bytes`.
- **A regex check that "looks like" validation** but accepts the exploit (e.g. SQL injection slipping past a regex that didn't account for unicode tricks). Use the framework's parameterized API.

## "Defense in depth" misapplied

- **Auth check in the middleware AND in the controller AND in the service AND in the repository** — the same check 4 times. Drift inevitable; one will be more permissive than the others; the more permissive one is now the actual contract.
- **Input validation at the API gateway AND in the route handler AND in the service AND at the DB.** The DB layer should TRUST the validated inputs from the boundary.
- True defense in depth is **complementary** redundancies (auth at the network layer + auth at the application layer + audit logging on every privileged action). Not the same check repeated.

## Mitigation drift

- **Tightening validation in the new code path** but not the old. Attackers find the old path.
- **Adding a rate limit on the new endpoint** but the old endpoint (with the same vulnerability) lives. Sweep with `audit-repo` for similar patterns.
- **Patching the SQL injection in the search query** but not the export query (which has the same shape). List as residual risk + follow-up.

## Mitigation in the wrong layer

- **Filtering out `<script>` tags in middleware** (an XSS attempt) — but the actual rendering path uses `dangerouslySetInnerHTML` further down, which doesn't escape. The right boundary is the rendering layer, not the middleware.
- **Validating the JSON shape with zod in the controller** but then in the repository layer constructing SQL with string concatenation (an SQL injection). The validation didn't help; the parameterization is the right boundary for SQLi.
- **Adding `helmet.contentSecurityPolicy`** but the app inlines scripts from React (which CSP would block). Test that the mitigation doesn't break the legitimate path.

## Disclosure mistakes

- **Committing the exploit details** in the commit message before the fix has rolled out. Public commit history is searchable.
- **Mentioning the CVE in the PR description** before disclosure. Same.
- **Filing a public GitHub Issue** for an internal-found vulnerability. Use a private security advisory or a private channel.
- **Talking about the unfixed vulnerability in a public Slack channel.** Bad.

## Skipping the regression test

- **Pushing the fix without a regression test.** CVE re-introductions happen often (the fix gets reverted, the bug comes back, nobody notices because no test).
- **Adding a test that asserts on the wrong thing** (e.g. "test that the function exists") instead of the actual exploit.
- **Adding a test that passes both before and after.** It's not testing the vulnerability.
- **Treating the security test as "manual verification"** — it must be in the suite + runs in CI.

## Failing open

- **`if (!validation(input)) { /* log warning */ }`** — the input passes through. Should reject.
- **`try { auth(req); } catch { /* allow */ }`** — auth check threw an error; the code allows the request. Should reject.
- **Default-allow** when the validation is uncertain. Default-deny is the security-default.
- **Caching auth results** with a long TTL — a revoked token may continue to work for the cache duration.

## Swallowing the "did the mitigation actually defend?" question

- **Adding the mitigation; tests pass; ship.** Without an exploit test that proves the mitigation blocks, the "fix" might not fix.
- **Replacing one vulnerability with another** (e.g. switching from one regex to another that has its own bypass).
- **Adding the mitigation that the CVE advisory recommends, without checking it actually applies to this codebase** (the advisory may assume a specific version or framework).

## Overreach

- **Patching CVE in `@acme/auth` AND rewriting the password storage AND adding 2FA** — three security tasks; split. Each has its own threat model and regression test.
- **"Comprehensive security review while we're at it"** — that's `audit-repo`. Don't bundle.
- **Adding security headers across all endpoints** as a side-effect of a single CVE fix. List as follow-up; don't bundle.

## Reporting

- **Burying the threat model.** It's the most-read part of the artifact.
- **Hiding the residual risk.** Every mitigation has residual risk; surface it (e.g. "this fix prevents SQL injection via the q param; SQL injection via other params is out of scope for this task — sweep with audit-repo").
- **Saying "fixed" without showing the exploit-test red→green transition.** Always show the transition.
- **Not running the security-reviewer agent.** It's part of the workflow; not optional.
