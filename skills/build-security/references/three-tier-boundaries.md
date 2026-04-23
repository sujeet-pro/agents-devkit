# Three-tier security boundary system

Every security change `build-security` makes is classified into one of three tiers. The tier determines whether the agent proceeds, asks first, or refuses.

## Tier 1 — Always do (no approval needed)

These are protections you should add or improve without asking. They have low risk of regression and high security upside.

- Validate untrusted input at the boundary (Zod / Pydantic / Joi / OpenAPI middleware).
- Use parameterized queries / prepared statements / ORM bindings — never string-concat user input into SQL.
- Hash passwords with bcrypt (≥ 12 rounds) / argon2id / scrypt.
- Use `httpOnly`, `secure`, `sameSite=Lax` (or `Strict`) cookies for session tokens.
- Add or tighten `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`.
- Add rate limits to auth, password-reset, and signup endpoints. Return 429 + `Retry-After`.
- Sanitize HTML output (auto-escaping templates, `DOMPurify` for innerHTML).
- Patch a known CVE with a non-breaking version bump (verify changelog).
- Use cryptographically-secure random for tokens (`crypto.randomBytes` / `secrets.token_urlsafe`).
- Set a TTL on password-reset tokens (≤ 1 hour) and one-shot consume.
- Encrypt sensitive data at rest (PII, payment, tokens) using a vetted library.
- Remove unused secrets / disable unused service accounts.
- Add a generic `INTERNAL_ERROR` envelope at the edge — never leak stack / SQL / internal paths.

## Tier 2 — Ask first (explicit approval, even under `--mode fix`)

These are changes that materially shift posture. They MAY be correct, but require a human decision.

- Replace one auth library / pattern with another (e.g. session → JWT, JWT → session).
- Change rate-limit thresholds (any direction).
- Open or change CORS allowed origins.
- Change CSP `script-src` / `connect-src` allowlist (adding new sources).
- Change cookie `sameSite` from `Strict` → `Lax` or `Lax` → `None`.
- Major-version bump to a security-relevant dep (auth library, crypto library).
- Introduce a new third-party SaaS in the auth or data path.
- Change password policy (length, charset, history, expiry).
- Change session/JWT TTL (any direction).
- Change CSRF strategy (Synchronizer-Token → SameSite-only, etc.).
- Replace bcrypt rounds (cost factor change forces re-hashing on next login).
- Add a new file-upload endpoint (any non-trivial file ingress).
- Change the encryption-at-rest key management approach.

## Tier 3 — Never do (refuse and explain)

The skill REFUSES these even under `--auto` / `--mode fix`. The user has to file a separate, documented decision (e.g. an ADR) to override.

- Disable CSRF protection.
- Disable CSP / set CSP to `default-src *` / add `'unsafe-inline'` `'unsafe-eval'` without scoped justification.
- Remove or weaken authentication on a protected endpoint.
- Remove or weaken authorization checks ("trust the auth middleware").
- Disable certificate verification (`rejectUnauthorized: false`, `verify=False`, `--insecure`).
- Use ECB-mode block cipher / use a hardcoded IV / use a deprecated hash for new data.
- Hardcode a secret in source / commit a credential / commit `.env`.
- Disable `httpOnly` on session cookies / store session tokens in `localStorage` for SPAs.
- Echo unsanitized user input into HTML (`innerHTML = req.query.x`).
- Concatenate user input into a SQL / shell / NoSQL query string.
- Replace bcrypt with MD5/SHA1/SHA256 for password hashing.
- Allow file uploads without size limits / type allowlist / virus scan.
- Set `Access-Control-Allow-Origin: *` AND `Access-Control-Allow-Credentials: true`.
- Skip `npm audit` / lockfile maintenance "for now".
- Disable a security header to "make tests pass".
- Catch and silently swallow security-relevant exceptions.

## Decision rule

If unsure between tiers, **default to the higher tier** (Ask first instead of Always; Never instead of Ask). It is always correct to be more cautious about security than less.
