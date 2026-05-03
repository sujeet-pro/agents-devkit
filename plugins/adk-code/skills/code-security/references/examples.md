# `code-security` — worked examples

## Example 1 — fix a CVE in a dependency

**Prompt:** `/adk-code:code-security "fix CVE-2025-12345 in the @acme/auth package"`

**Phase 0:** Slug `secure-cve-2025-12345`. Repo `~/code/acme/checkout-api`. WebFetch the NVD entry: CVE-2025-12345 is in `@acme/auth` versions <2.4.7; allows token forgery via algorithm confusion.

**Phase 1:** Clean. Branch `secure/cve-2025-12345`. Tests green on HEAD.

**Phase 2 threat model:**

```
1. Untrusted input: JWT in Authorization header on every authenticated endpoint.
2. Privileged action: granting authorization to act as the claimed user.
3. Asset: any user's session / data.
4. Actor: unauthenticated external user (with a forged token).
5. Residual risk: the upgrade closes the algorithm-confusion path. Other JWT vulnerabilities (e.g. weak signing key, replay attacks) are not in scope for this task.
```

**Phase 3 boundary:** Input boundary: `middleware/authenticate.ts:18` (the JWT verification call). Output / privileged action: `req.user = decoded` at line 24, which the rest of the request handler trusts.

**Phase 4 exploit test:** Author a test that creates a forged token using the algorithm-confusion technique (the advisory provides a reproducer):

```ts
// tests/auth/cve-2025-12345.test.ts
test("rejects a token signed with HS256 when key was for RS256 (CVE-2025-12345)", async () => {
  const forged = forgeTokenViaAlgorithmConfusion();
  const res = await request(app).get("/api/me").set("Authorization", `Bearer ${forged}`);
  expect(res.status).toBe(401);
});
```

Run on HEAD: test FAILS — the response is 200; the forged token is accepted.

`exploit-test.md`:
```markdown
## Exploit test
- File: tests/auth/cve-2025-12345.test.ts
- Behavior: forged token via algorithm confusion → server accepts → 200.
- Failing output: "Expected 401, received 200; user.id = 'attacker-targeted-id'"
- Confidence: high; matches the advisory's reproducer.
```

**Phase 5 mitigation:** Upgrade `@acme/auth` from 2.4.5 to 2.4.7 (the patched version). The package.json is the only change.

`plan.md`:
```markdown
## Mitigation
Upgrade @acme/auth: 2.4.5 → 2.4.7 (patches CVE-2025-12345).

## Files touched
| File | Action | Why |
| --- | --- | --- |
| package.json | edit | bump @acme/auth to ^2.4.7 |
| pnpm-lock.yaml | regenerate | from `pnpm install` |

## Boundary
The library's internal JWT verification is now algorithm-aware; no
application-code change needed.
```

Run `pnpm install`. Re-run the exploit test: GREEN — forged token now rejected with 401.

**Phase 6 validate:** Full `auth` test suite green. Typecheck + lint green.

**Phase 7 security-reviewer:** Spawn agent. Findings:
- No-finding: the upgrade is the canonical fix per the CVE advisory.
- Question: any other JWT-handling code paths in the repo? Yes — `tests/auth/legacy-routes.ts` uses an older inline JWT verifier. Recommendation: remove the inline verifier in a follow-up.

**Phase 8 report:** Notes the residual risk: "legacy inline JWT verifier in `tests/auth/legacy-routes.ts` is unused but exists; spawn `code-refactor` to remove."

---

## Example 2 — input validation on a new upload endpoint

**Prompt:** `/adk-code:code-security "add input validation on the new /api/upload endpoint"`

**Phase 0:** Slug `secure-upload-validation`. Repo `~/code/acme/document-api`. The upload endpoint was added recently in a feature branch; this task hardens it.

**Phase 1:** Clean. Branch `secure/upload-validation`. Tests green.

**Phase 2 threat model:**

```
1. Untrusted input: multipart/form-data on POST /api/upload (file + filename).
2. Privileged action: writing the file to S3 with the user-supplied filename; serving it back via /api/download/{filename}.
3. Asset: storage cost (DOS via large files); confidentiality (path traversal via filename → access to other users' files); served-file safety (uploaded .exe / .php served back to other users).
4. Actor: authenticated external user.
5. Residual risk: scanning for malware / advanced steganography is out of scope. We accept that legitimate-looking files may contain malicious content.
```

**Phase 3 boundary:** Input boundary: `routes/upload.ts:8` (the multer middleware). Output / privileged action: S3 PUT at line 22, and the served route `routes/download.ts`.

**Phase 4 exploit tests:** 4 tests:

```ts
test("rejects upload > 10MB", async () => {
  const big = Buffer.alloc(11 * 1024 * 1024);
  const res = await request(app).post("/api/upload").attach("file", big, "big.bin");
  expect(res.status).toBe(413);
});

test("rejects filenames with path-traversal", async () => {
  const res = await request(app).post("/api/upload")
    .attach("file", small, "../../etc/passwd");
  expect(res.status).toBe(400);
});

test("rejects executable extensions", async () => {
  const res = await request(app).post("/api/upload").attach("file", small, "evil.exe");
  expect(res.status).toBe(400);
});

test("rejects mismatched magic bytes", async () => {
  const exeBytes = Buffer.from([0x4D, 0x5A]);  // MZ - exe
  const res = await request(app).post("/api/upload")
    .attach("file", exeBytes, "innocent.txt");
  expect(res.status).toBe(400);
});
```

Run on HEAD: ALL 4 fail. The upload accepts everything.

**Phase 5 mitigation:** Add 4 boundary checks at `routes/upload.ts`:
- `multer({ limits: { fileSize: 10 * 1024 * 1024 } })`.
- `validateFilename(name)` rejects path traversal + null bytes.
- `validateExtension(name)` allowlist of `.txt / .pdf / .png / .jpg`.
- `validateMagicBytes(file.buffer, name)` checks first 4 bytes match the extension.

Re-run: all 4 tests pass.

**Phase 6 validate:** Full `document-api` suite green.

**Phase 7 security-reviewer:** Spawn agent. Findings:
- Should-have: the served-file path also serves files; add `Content-Disposition: attachment` header to prevent rendering as HTML/script. Fixed in this diff.
- Question: anti-virus scanning? Out of scope per the threat model.

**Phase 8 report:** Lists 4 mitigations + the C-D header. Residual risk: "no AV scanning; out of scope per threat model".

---

## Example 3 — tighten CORS on the public storefront API

**Prompt:** `/adk-code:code-security "tighten CORS on the public storefront API"`

**Phase 0:** Slug `secure-storefront-cors`. Repo `~/code/acme/storefront-api`.

**Phase 1:** Clean. Branch `secure/storefront-cors`. Tests green.

**Phase 2 threat model:**

```
1. Untrusted input: cross-origin requests with custom headers / cookies.
2. Privileged action: serving authenticated endpoints (e.g. /api/me, /api/cart) where the response includes session-bound data.
3. Asset: the user's session cookie (and the data it gates).
4. Actor: malicious site that the user happens to visit while logged into our storefront.
5. Residual risk: this fix prevents browser-side cross-origin reads of authenticated endpoints. Server-side requests (which do not send cookies anyway) are not in scope.
```

**Phase 3 boundary:** Input boundary: `app.ts:14` (the `cors()` middleware). Currently configured with `origin: '*'` and `credentials: true` — which browsers reject (specs forbid wildcard + credentials), so the actual behavior is "credentials don't go through cross-origin", but the config implies otherwise and may invite future drift.

**Phase 4 exploit test:** Test that a cross-origin request from `https://malicious.example.com` to `/api/me` (with credentials) does NOT receive the response body cross-origin.

```ts
test("rejects cross-origin requests from non-allowlisted origins", async () => {
  const res = await request(app).get("/api/me")
    .set("Origin", "https://malicious.example.com")
    .set("Cookie", "session=valid-session");
  // The browser would block; our server sets headers that prevent the browser from reading the body.
  expect(res.headers["access-control-allow-origin"]).not.toBe("*");
  expect(res.headers["access-control-allow-origin"]).not.toBe("https://malicious.example.com");
});
```

Run on HEAD: FAILS — header is `*`.

**Phase 5 mitigation:** Replace `cors({ origin: '*', credentials: true })` with an allowlist:

```ts
const ALLOWED_ORIGINS = [
  "https://www.acme.com",
  "https://staging.acme.com",
  "https://www.acme.dev",  // local dev origin
];

app.use(cors({
  origin: (origin, cb) => {
    if (!origin) return cb(null, true);  // same-origin / non-browser
    cb(null, ALLOWED_ORIGINS.includes(origin));
  },
  credentials: true,
}));
```

Re-run: PASSES.

**Phase 6 validate:** Full suite green. Manually tested in the dev console: same-origin works; cross-origin from `acme.com` works; cross-origin from `malicious.example.com` rejected.

**Phase 7 security-reviewer:** Findings:
- Should-have: also add `SameSite=Strict` to the session cookie. (This is an additional mitigation for the same threat — defense in depth at the cookie layer.) Fixed in this diff.
- Question: do we have any third-party iframes that legitimately make cross-origin requests? Confirm with the operator. Default: no — proceed.

**Phase 8 report:** Lists the CORS allowlist + the `SameSite=Strict` cookie change. Residual risk: "if a future feature requires a third-party origin, must explicitly add to ALLOWED_ORIGINS; CSP may also need updating; consider a CI check that disallows wildcard CORS in app.ts".

---

## Example 4 — add rate-limit on the login endpoint

**Prompt:** `/adk-code:code-security "add rate-limit on /api/auth/login to prevent credential stuffing"`

**Phase 0:** Slug `secure-login-rate-limit`. Repo `~/code/acme/auth-service`.

**Phase 1:** Clean. Branch `secure/login-rate-limit`. Tests green.

**Phase 2 threat model:**

```
1. Untrusted input: POST /api/auth/login with username + password.
2. Privileged action: authenticating; on success, issuing a session.
3. Asset: any user's session / account.
4. Actor: unauthenticated external user (running a credential-stuffing script).
5. Residual risk: rate-limit by IP can be circumvented with a botnet (lots of IPs, low rate per IP). Account-lockout is the deeper defense (out of scope here; deferred to a separate task because it requires user-experience design).
```

**Phase 3 boundary:** Input boundary: `routes/auth/login.ts:6` (the route handler). The rate-limit lives at this entry.

**Phase 4 exploit test:** Test that the 11th attempt within 1 minute is rate-limited:

```ts
test("rate-limits login: 10 per minute per IP", async () => {
  for (let i = 0; i < 10; i++) {
    const res = await request(app).post("/api/auth/login").send({ username: "x", password: "wrong" });
    expect(res.status).toBe(401);  // wrong password but allowed
  }
  const res = await request(app).post("/api/auth/login").send({ username: "x", password: "wrong" });
  expect(res.status).toBe(429);  // rate-limited
});
```

Run on HEAD: FAILS — there is no rate-limit; all 11 return 401.

**Phase 5 mitigation:** Add `express-rate-limit` middleware at `routes/auth/login.ts`:

```ts
const loginLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,
  message: "Too many login attempts; try again later.",
  standardHeaders: true,
  legacyHeaders: false,
});

router.post("/login", loginLimiter, loginHandler);
```

Re-run: PASSES.

**Phase 6 validate:** Full `auth-service` suite green.

**Phase 7 security-reviewer:** Findings:
- Should-have: rate-limit by IP only — with a botnet, this is circumventable. Recommend account-lockout as a follow-up (deeper defense). NOT fixed in this diff (separate concern; needs UX).
- Question: does the rate-limit storage (in-memory by default) survive across instances? No — in distributed deployment, each instance has its own counter. Recommend: switch to Redis-backed rate-limit storage. NOT fixed in this diff (configuration change; separate task).

**Phase 8 report:** Lists the rate-limit + 2 residual risks (account-lockout + Redis-backed storage). Both are follow-up `code-write` / `code-security` tasks.
