# OWASP Top 10 (2021) — mitigation patterns

This is a fast lookup for `build-security`. Each row maps an OWASP item to the standard mitigation pattern this skill applies. Use as the menu for the "plan the smallest correct fix" step.

| OWASP item | Mitigation pattern (default) | Library / mechanism examples |
| --- | --- | --- |
| **A01 Broken Access Control** | Deny-by-default authz on every protected route; explicit per-action checks (`can(user, action, resource)`); resource-level + tenant-level scoping; never trust IDs from the URL alone. | Cerbos, OPA/Rego, CASL, custom RBAC with audit logging. |
| **A02 Cryptographic Failures** | TLS for all transit; encrypt PII / tokens at rest with vetted libs; bcrypt (≥ 12) / argon2id for passwords; cryptographically-random tokens (`crypto.randomBytes`); never log secrets. | `bcrypt`, `argon2`, `libsodium`, AWS KMS / GCP KMS / Vault for keys. |
| **A03 Injection** (SQLi / NoSQLi / OS command / LDAP / SSTI) | Parameterized queries / prepared statements; ORM bindings; templating with auto-escape; never `eval`; sanitize file paths against traversal. | Knex, Prisma, SQLAlchemy, mongoose with strict schema, `child_process.execFile` (not `exec`). |
| **A04 Insecure Design** | Threat-model the feature before code (STRIDE / attack-tree); design for least privilege; default-deny; assume the perimeter is breached. | Threat model doc lives in `docs/security/`; reviewed in PR. |
| **A05 Security Misconfiguration** | Set security headers; disable directory listing; disable verbose errors in prod; default-deny CORS; tight cookie attributes; remove default creds. | `helmet` (Express), Next.js / SvelteKit security headers, `secure_headers` (Rails). |
| **A06 Vulnerable & Outdated Components** | `npm audit --audit-level=high` (or pip/cargo equivalent) in CI; Dependabot / Renovate; pin lockfiles; review changelogs before bumping. | Dependabot, Renovate, Snyk, OSV-Scanner. |
| **A07 Identification & Authentication Failures** | Vetted auth library; MFA for admin; account lockout / throttling on login + reset; rotate session on privilege change; secure session storage. | Auth0, Clerk, Lucia, NextAuth, `passport`, `express-rate-limit`. |
| **A08 Software & Data Integrity Failures** | Signed packages, SLSA / SBOM provenance; verify webhooks (HMAC); pin CI actions to SHA, not tag; signed git commits where possible. | Sigstore, `gh attestation`, GitHub Actions pinned to SHA. |
| **A09 Security Logging & Monitoring Failures** | Log auth events (success + failure), authz denials, admin actions, high-value mutations; ship to a central store; alert on anomalies. | Datadog Cloud SIEM, Sentry security events, OpenTelemetry. |
| **A10 Server-Side Request Forgery (SSRF)** | Validate outbound URLs against an allowlist; resolve DNS once and reuse the IP; block link-local / private ranges; egress proxy / firewall. | `ssrfilter`, custom allowlist middleware. |

## Standard middleware stack (Node/Express example)

```js
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';

const app = express();

app.use(helmet());
app.use(express.json({ limit: '100kb' }));
app.use(cors({
  origin: ['https://app.example.com'],
  credentials: true,
  methods: ['GET','POST','PUT','PATCH','DELETE'],
}));

app.use('/api/auth/', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
}));
```

## Standard input validation pattern (TypeScript + Zod)

```ts
import { z } from 'zod';

const CreateUserBody = z.object({
  email: z.string().email().max(254),
  password: z.string().min(12).max(128),
  display_name: z.string().min(1).max(80),
}).strict();

app.post('/api/users', (req, res) => {
  const parsed = CreateUserBody.safeParse(req.body);
  if (!parsed.success) {
    return res.status(422).json({
      error: { code: 'VALIDATION_ERROR', details: parsed.error.issues, request_id: req.id },
    });
  }
  // parsed.data is now trusted
});
```

## Standard error envelope (matches `build-api`'s `error-semantics.md`)

```json
{ "error": { "code": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "request_id": "req_..." } }
```

Never include stack traces, SQL fragments, internal paths, env var names, or credentials in 5xx bodies.
