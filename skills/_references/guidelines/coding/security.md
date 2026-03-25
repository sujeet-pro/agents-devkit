# Security Review Guidelines

These guidelines apply to **application security** across all backend and frontend
services. They supplement the general guidelines with rules for building systems
that defend against the OWASP Top 10, manage authentication and authorization
correctly, handle secrets safely, and maintain a secure software supply chain.

---

## 1. OWASP Top 10

Every code review must consider the [OWASP Top 10 (2021)](https://owasp.org/Top10/)
attack categories. These represent the most critical security risks to web
applications, derived from real-world breach data.

- **A01: Broken Access Control.** Verify that every endpoint enforces authorization.
  Check for insecure direct object references (IDOR), missing function-level access
  control, and privilege escalation paths. Test that user A cannot access user B's
  data by manipulating IDs in URLs or request bodies.
- **A02: Cryptographic Failures.** Verify that sensitive data is encrypted in transit
  (TLS 1.2+) and at rest. Check for hardcoded secrets, weak algorithms (MD5, SHA1
  for passwords), and missing encryption on PII fields in databases.
- **A03: Injection.** Verify that all external input is parameterized or escaped
  before reaching interpreters (SQL, NoSQL, OS commands, LDAP, XPath). Never
  concatenate user input into query strings:
  ```typescript
  // VULNERABLE: SQL injection
  const query = `SELECT * FROM users WHERE email = '${email}'`;

  // SAFE: parameterized query
  const query = "SELECT * FROM users WHERE email = $1";
  const result = await db.query(query, [email]);
  ```
- **A04: Insecure Design.** Review for missing threat modeling, lack of rate limiting
  on sensitive operations, and absence of defense-in-depth. Security must be designed
  in, not bolted on. Use STRIDE or PASTA threat modeling frameworks during design
  reviews.
- **A05: Security Misconfiguration.** Check for default credentials, unnecessary
  features enabled, verbose error messages exposing internals, missing security
  headers, and overly permissive CORS policies. Automate configuration hardening
  via infrastructure-as-code and enforce it with policy-as-code tools (OPA, Kyverno).
- **A06: Vulnerable and Outdated Components.** Verify that dependency scanning is
  enabled in CI and that known vulnerabilities are triaged within SLA (critical: 24
  hours, high: 7 days, medium: 30 days).
- **A07: Identification and Authentication Failures.** Review password policies,
  session management, credential storage, and multi-factor authentication
  implementation. See Section 2 below.
- **A08: Software and Data Integrity Failures.** Verify that CI/CD pipelines validate
  artifact integrity, dependencies are pinned with lockfiles, and deserialization of
  untrusted data is avoided or sandboxed. Use Subresource Integrity (SRI) for CDN
  resources.
- **A09: Security Logging and Monitoring Failures.** Verify that authentication
  events, authorization failures, and input validation failures are logged with
  sufficient context for incident investigation. See the observability guidelines.
- **A10: Server-Side Request Forgery (SSRF).** Verify that user-supplied URLs are
  validated against an allowlist. Block requests to internal IP ranges
  (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`) and
  localhost.

> **Reference**: [OWASP Top 10 (2021)](https://owasp.org/Top10/),
> [OWASP Application Security Verification Standard (ASVS)](https://owasp.org/www-project-application-security-verification-standard/),
> [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

## 2. Authentication

- **Password hashing: use bcrypt or Argon2id.** Never use MD5, SHA-256, or any
  general-purpose hash function for passwords. Password hashes must be slow by
  design to resist brute-force attacks:
  ```typescript
  import argon2 from "argon2";

  // Hashing
  const hash = await argon2.hash(password, {
      type: argon2.argon2id,
      memoryCost: 65536,    // 64 MiB
      timeCost: 3,          // 3 iterations
      parallelism: 4,       // 4 threads
  });

  // Verification
  const valid = await argon2.verify(hash, password);
  ```
  - **Argon2id** is the OWASP-recommended default (2024). It resists both GPU-based
    and side-channel attacks.
  - **bcrypt** with cost factor 12+ is acceptable for existing systems. Plan
    migration to Argon2id for new implementations.
  - **PBKDF2** with HMAC-SHA256 and 600,000+ iterations is the NIST-recommended
    alternative (NIST SP 800-132) when Argon2 is unavailable.
- **Multi-Factor Authentication (MFA).** Require MFA for all administrative accounts
  and offer it for all user accounts. Support TOTP (RFC 6238) as the baseline;
  WebAuthn/FIDO2 as the preferred strong factor:
  - TOTP: Time-based One-Time Password using 6-digit codes with 30-second windows.
    Verify the current window and one adjacent window to account for clock drift.
  - WebAuthn: Phishing-resistant, hardware-backed authentication. Preferred for
    high-security accounts.
  - SMS-based MFA is better than no MFA but is vulnerable to SIM swapping. Do not
    use it as the sole second factor for high-value accounts.
- **Session management:**
  - Generate session IDs using a cryptographically secure random number generator
    (CSPRNG). Session IDs must be at least 128 bits of entropy.
  - Set session cookies with `Secure`, `HttpOnly`, `SameSite=Lax` (or `Strict`
    where appropriate), and an appropriate `Path` and `Domain`:
    ```
    Set-Cookie: session=<token>; Secure; HttpOnly; SameSite=Lax; Path=/; Max-Age=86400
    ```
  - Implement absolute session timeout (e.g., 24 hours) and idle timeout (e.g., 30
    minutes). Re-authenticate for sensitive operations (password change, payment).
  - Invalidate sessions server-side on logout. Do not rely on client-side cookie
    deletion alone.
  - Rotate session IDs after authentication state changes (login, privilege
    escalation) to prevent session fixation.
- **JWT best practices** (when using token-based auth):
  - Sign with RS256 or ES256 (asymmetric). Avoid HS256 in multi-service
    architectures where the shared secret would need to be distributed.
  - Set short expiration (`exp`): 15 minutes for access tokens. Use refresh tokens
    (stored server-side, rotated on use) for longer sessions.
  - Validate `iss`, `aud`, `exp`, and `nbf` on every request. Reject tokens
    missing required claims. Always validate the `alg` header to prevent `none`
    algorithm attacks.
  - Never store sensitive data in JWT payloads -- they are base64-encoded, not
    encrypted. Never store JWTs in localStorage; use HttpOnly cookies.
  - Implement token revocation via a short blocklist (for compromised tokens) or
    by keeping access token lifetimes short enough that revocation is unnecessary.

> **Reference**: [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html),
> [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html),
> [NIST SP 800-63B: Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html),
> [RFC 6238: TOTP](https://www.rfc-editor.org/rfc/rfc6238),
> [RFC 7519: JWT](https://www.rfc-editor.org/rfc/rfc7519)

## 3. Authorization

- **Enforce authorization at the service boundary.** Every API endpoint must verify
  that the authenticated principal is authorized to perform the requested action on
  the requested resource. Authorization checks must happen server-side; client-side
  checks are UX conveniences, not security controls.
- **RBAC (Role-Based Access Control)** is appropriate when permissions map cleanly
  to organizational roles and roles are relatively static:
  ```typescript
  // Role hierarchy: admin > manager > member > viewer
  const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
      admin:   ["read", "write", "delete", "manage_users", "manage_billing"],
      manager: ["read", "write", "delete"],
      member:  ["read", "write"],
      viewer:  ["read"],
  };

  function authorize(user: User, requiredPermission: Permission): boolean {
      return ROLE_PERMISSIONS[user.role].includes(requiredPermission);
  }
  ```
- **ABAC (Attribute-Based Access Control)** is appropriate when authorization
  depends on resource attributes, environmental conditions, or complex policies
  that RBAC cannot express:
  - "A user can edit a document if they are the owner OR a member of the document's
    team AND the document is not locked."
  - "A support agent can view customer data only during their shift hours and only
    for customers in their assigned region."
  - Use a policy engine (Open Policy Agent, Cedar, Casbin) for complex ABAC rules.
    Do not embed multi-condition authorization logic in application code.
- **Least privilege.** Grant the minimum permissions required for each role or
  service account. Audit permissions quarterly. Revoke unused permissions
  automatically where possible.
- **Common authorization vulnerabilities to check in reviews:**
  - **IDOR (Insecure Direct Object Reference)**: `GET /api/orders/123` returns
    order 123 regardless of who owns it. Always filter by the authenticated user's
    scope.
  - **Broken function-level access control**: Admin endpoints accessible to regular
    users because the route exists but the authorization middleware is missing.
  - **Privilege escalation via parameter tampering**: A user sets `role: "admin"` in
    their profile update request body.
  - **Missing authorization on sub-resources**: The parent resource is protected but
    child resources (attachments, comments) are not.

> **Reference**: [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html),
> [NIST SP 800-162: ABAC Guide](https://csrc.nist.gov/publications/detail/sp/800-162/final),
> [Open Policy Agent](https://www.openpolicyagent.org/),
> [AWS Cedar Policy Language](https://www.cedarpolicy.com/)

## 4. Secrets Management

- **Never store secrets in source code, environment files committed to version
  control, or container images.** Secrets must be injected at runtime from a
  dedicated secrets manager:
  - **Recommended**: HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager,
    Azure Key Vault.
  - **Acceptable for development**: `.env` files that are git-ignored (listed in
    `.gitignore` before any secrets are created).
  - **Never acceptable**: Hardcoded strings, committed `.env` files, secrets in
    Docker build args or layers.
- **Rotate secrets on a schedule.** Database passwords, API keys, and TLS
  certificates should have defined rotation periods. Automate rotation where
  possible (e.g., Vault dynamic secrets, AWS Secrets Manager rotation lambdas).
- **Use short-lived credentials** over long-lived API keys when the infrastructure
  supports it:
  - AWS IAM roles with STS temporary credentials instead of static access keys.
  - GCP Workload Identity Federation instead of service account keys.
  - Kubernetes service account tokens (projected, auto-rotated) instead of static
    secrets mounted as files.
- **Encrypt secrets at rest** in the secrets manager. Use envelope encryption
  (data key encrypted by a master key in KMS) for defense in depth.
- **Audit secret access.** Log every read of a secret (who, when, from where) and
  alert on anomalous access patterns.
- **Scan for leaked secrets in CI.** Use tools like `gitleaks`, `trufflehog`, or
  GitHub secret scanning to detect accidentally committed secrets. Block merges
  if secrets are detected.

> **Reference**: [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html),
> [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs),
> [NIST SP 800-57: Key Management](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)

## 5. Input Validation

- **Validate all external input at the service boundary.** Every field from HTTP
  request bodies, query parameters, headers, path parameters, file uploads, and
  message queue payloads must be validated before entering business logic.
- **Use schema validation libraries** that declare the expected shape and constraints
  declaratively:
  ```typescript
  // TypeScript with Zod
  const CreateUserSchema = z.object({
      email: z.string().email().max(254),
      name: z.string().min(1).max(200).trim(),
      age: z.number().int().min(13).max(150).optional(),
  });

  // Java with Jakarta Validation
  public record CreateUserRequest(
      @NotBlank @Email @Size(max = 254) String email,
      @NotBlank @Size(max = 200) String name,
      @Min(13) @Max(150) Integer age
  ) {}
  ```
- **Validate type, length, range, format, and business rules** in that order:
  1. **Type**: Is it a string, number, boolean, array?
  2. **Length/Size**: Is it within acceptable bounds? Reject unbounded strings and
     arrays that could cause memory exhaustion.
  3. **Range**: Is the number within valid bounds?
  4. **Format**: Does it match the expected pattern (email, UUID, date)?
  5. **Business rules**: Is the value valid in the domain context?
- **Reject unexpected fields.** Use allowlist validation (whitelist known fields)
  rather than denylist validation (blacklist known-bad fields). Strip or reject
  fields not in the schema to prevent mass assignment attacks.
- **Sanitize output, not input** for XSS prevention. Store data as-is and escape
  it at the rendering layer. Context-aware output encoding is more reliable than
  input sanitization:
  - HTML context: HTML-entity encode (`<` becomes `&lt;`).
  - JavaScript context: JavaScript-escape.
  - URL context: URL-encode.
  - CSS context: CSS-escape.
  Use a battle-tested templating engine with auto-escaping enabled by default
  (React JSX, Go `html/template`, Jinja2 with `autoescape=True`).

> **Reference**: [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html),
> [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html),
> [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)

## 6. Dependency Security

- **Run dependency vulnerability scanning in CI on every build.** Use `npm audit`,
  `pip-audit`, `mvn dependency-check:check`, or a commercial scanner (Snyk,
  Dependabot, Trivy).
- **Pin dependencies with lockfiles.** Commit `package-lock.json`, `yarn.lock`,
  `poetry.lock`, `go.sum`, or `Cargo.lock`. Lockfiles ensure reproducible builds
  and prevent supply chain attacks via dependency confusion.
- **Triage vulnerabilities by severity and exploitability:**

  | Severity | SLA | Action |
  |----------|-----|--------|
  | Critical (CVSS 9.0+) | 24 hours | Patch or mitigate immediately |
  | High (CVSS 7.0-8.9) | 7 days | Patch in next release cycle |
  | Medium (CVSS 4.0-6.9) | 30 days | Patch when convenient |
  | Low (CVSS 0.1-3.9) | 90 days | Track, patch at discretion |

- **Verify package integrity.** Use `npm audit signatures`, verify checksums, and
  prefer packages with provenance attestations (npm provenance, Sigstore for
  containers).
- **Minimize the dependency tree.** Every dependency is an attack surface. Before
  adding a dependency, consider: Can this be implemented in a few lines of
  application code? Is the package actively maintained? Does it have a history of
  security issues?
- **Use Software Bill of Materials (SBOM).** Generate SBOMs (SPDX or CycloneDX
  format) for production artifacts to enable rapid vulnerability response when a
  new CVE is disclosed.

> **Reference**: [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/),
> [NIST SP 800-218: SSDF](https://csrc.nist.gov/publications/detail/sp/800-218/final),
> [Snyk Vulnerability Database](https://security.snyk.io/),
> [SLSA Supply Chain Framework](https://slsa.dev/)

## 7. CORS and Security Headers

- **Configure CORS restrictively.** Never use `Access-Control-Allow-Origin: *` for
  authenticated APIs. Whitelist specific origins:
  ```typescript
  const corsOptions = {
      origin: ["https://app.example.com", "https://admin.example.com"],
      methods: ["GET", "POST", "PUT", "DELETE"],
      allowedHeaders: ["Content-Type", "Authorization"],
      credentials: true,
      maxAge: 86400,  // preflight cache: 24 hours
  };
  ```
- **Set security headers on every response.** Use `helmet` (Node.js), security
  middleware (Spring Security, Django), or a reverse proxy configuration:

  | Header | Value | Purpose |
  |--------|-------|---------|
  | `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Force HTTPS for 2 years |
  | `Content-Security-Policy` | `default-src 'self'; script-src 'self'` | Prevent XSS, data injection |
  | `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
  | `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Prevent clickjacking |
  | `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer leakage |
  | `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disable unnecessary browser APIs |

- **Content Security Policy (CSP)** must be specific to your application. Start
  with a strict policy and relax only as needed:
  ```
  Content-Security-Policy:
    default-src 'self';
    script-src 'self' 'nonce-{random}';
    style-src 'self' 'nonce-{random}';
    img-src 'self' data: https://cdn.example.com;
    connect-src 'self' https://api.example.com;
    font-src 'self';
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
  ```
  - Use nonce-based CSP (`'nonce-{random}'`) for inline scripts rather than
    `'unsafe-inline'`. Generate a unique nonce per request.
  - Deploy CSP in report-only mode first (`Content-Security-Policy-Report-Only`)
    to identify violations before enforcement.
  - Monitor CSP violation reports via the `report-to` directive.

> **Reference**: [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/),
> [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP),
> [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS),
> [HSTS Preload List](https://hstspreload.org/)

## 8. Review Checklist

- [ ] All endpoints enforce authorization (no missing access control checks)
- [ ] No IDOR vulnerabilities: resource access is scoped to the authenticated principal
- [ ] Passwords are hashed with Argon2id or bcrypt (never MD5/SHA-family)
- [ ] Session cookies use `Secure`, `HttpOnly`, and `SameSite` attributes
- [ ] JWT tokens have short expiration, validated signatures, and checked claims
- [ ] MFA is required for administrative accounts
- [ ] All SQL queries use parameterized statements (no string concatenation)
- [ ] Input validation exists at every service boundary with schema enforcement
- [ ] Output encoding is context-appropriate (HTML, JS, URL, CSS)
- [ ] No secrets are hardcoded in source code, committed env files, or container images
- [ ] Dependency scanning runs in CI with defined severity SLAs
- [ ] Lockfiles are committed and package integrity is verified
- [ ] CORS is configured with explicit origin allowlist (no wildcard for authenticated APIs)
- [ ] Security headers are set: HSTS, CSP, X-Content-Type-Options, X-Frame-Options
- [ ] CSP uses nonce-based script allowlisting (no `'unsafe-inline'`)
- [ ] SSRF protection: user-supplied URLs validated against allowlist, internal ranges blocked
- [ ] Authentication failures and authorization denials are logged for audit
- [ ] File uploads are validated for type, size, and scanned for malware
