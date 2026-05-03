# `docs-review` — worked examples

## Example 1 — review a README

**Prompt:** `/adk-docs:docs-review README.md --auto`

**Phase 2 claim table (excerpt):**

| Claim (doc) | Code source | Status |
| --- | --- | --- |
| "Run `npm install`" | `package.json:5` has `"packageManager": "pnpm@9.0.0"`; `pnpm-lock.yaml` exists | wrong |
| "Runs on Node 18" | `package.json:engines.node: ">=20"`, `.nvmrc: 20.11.0` | wrong |
| "Requires Postgres" | `docker-compose.yml:22-30` uses `postgres:15-alpine` | OK |
| "Deploys via GitHub Actions" | `.github/workflows/deploy.yml` exists | OK |

**Phase 4 findings (excerpt):**

```markdown
### 1. [Blocker] Install command is wrong
- **Doc**: `README.md:22` — "Run `npm install`"
- **Code**: `package.json:5` declares `"packageManager": "pnpm@9.0.0"`;
  `pnpm-lock.yaml` is present, `package-lock.json` is not.
- **Evidence**: `ls pnpm-lock.yaml package-lock.json 2>&1`.
- **Fix (under --fix)**: replace `npm install` with `pnpm install`.

### 2. [Blocker] Node version is wrong
- **Doc**: `README.md:18` — "Requires Node 18"
- **Code**: `package.json:engines.node: ">=20"`, `.nvmrc: 20.11.0`.
- **Fix**: replace "Node 18" with "Node 20 (matches `.nvmrc`)".
```

## Example 2 — review a runbook with a stale rollback step

**Prompt:** `/adk-docs:docs-review docs/runbooks/oncall.md -i`

**Phase 2:** Runbook references `kubectl -n prod rollout undo
deploy/checkout-api`. Check: `kubectl get deploy -n prod` shows
`deploy/checkout` (no `-api` suffix anymore — renamed in commit
`9abc123` three weeks ago).

**Phase 4 finding:**

```markdown
### 1. [Critical] Rollback command uses old deployment name
- **Doc**: `docs/runbooks/oncall.md:42` — `kubectl -n prod rollout
  undo deploy/checkout-api`
- **Code**: `k8s/checkout/deployment.yaml:4` — `name: checkout` (the
  `-api` suffix was removed in `9abc123` on 2026-04-14).
- **Severity**: Critical — on-call uses this in an incident. Wrong
  command => extends incident.
- **Fix**: replace `checkout-api` with `checkout` on line 42.
```

Under `-i`, user approves; under `--fix`, the correction lands
locally and the diff is captured in `fixes-applied.md`.

## Example 3 — review a Confluence page

**Prompt:** `/adk-docs:docs-review "https://acme.atlassian.net/wiki/spaces/ENG/pages/42/Authentication+Overview" --auto`

**Phase 1:** Workspace Atlassian connector is connected. Page
metadata shows last-editor = `sujeet@acme.com` (a human, not a bot),
last-modified 2025-11-02.

**Phase 2:** Verifies claims against `services/auth-svc/` code paths.
Finds 1 Blocker (doc claims OIDC but code still uses static keys;
ADR-0007 scheduled but not yet implemented).

**Phase 4 report:**

```markdown
### 1. [Blocker] Page claims OIDC; service still uses static keys
- **Doc**: "Authentication Overview § Service-to-Service" —
  "Services authenticate to each other via OIDC client-credentials"
- **Code**: `services/auth-svc/internal/auth.kt:24-40` — uses
  `SharedSecretAuth(env: INTERNAL_API_SECRET)`.
- **Evidence**: ADR-0007 is in status `Proposed`, not `Accepted`;
  migration not complete.
- **Severity**: Blocker — readers rely on this for architectural
  decisions.
- **Note**: page last edited by a human on 2025-11-02. Under
  `--fix`, opt-in required.
```

## Example 4 — review a Google Doc

**Prompt:** `/adk-docs:docs-review "https://docs.google.com/document/d/ABC123/edit" -i`

Target is a design doc. `Phase 1` confirms Google Drive workspace
connector is connected. The doc references `pricing-api` and
`storefront`, both in `repos.md`.

**Phase 2–4:** 0 Blockers, 2 Should-Haves (no rollback plan; no
dependency graph), 3 May-Haves (vocabulary drift against ADR-0004).

**Phase 5:** Under `-i --fix`, the user declines auto-fix because the
doc is circulated externally and they want to apply changes
manually. All findings land in `fixes-deferred.md`.
