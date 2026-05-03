# `docs-write` — worked examples

## Example 1 — README for a Kotlin service

**Prompt:** `/adk-docs:docs-write "README for checkout-api" --auto`

**Phase 0:** doc-type = README. Repo = `acme/checkout-api` (from
`repos.md`). Slug = `checkout-api-readme`.

**Phase 2 evidence map (excerpt):**

```
claim: runs on Spring Boot 3.2
file: build.gradle.kts
lines: 14-18
evidence: |
  id("org.springframework.boot") version "3.2.3"

claim: local run command is `./gradlew :app:bootRun`
file: README (existing), repos.md
lines: n/a
evidence: |
  `repos.md` notes: "Use ./gradlew :app:bootRun for local."
```

**Phase 3 draft (excerpt):**

```markdown
# checkout-api

> Handles cart + order state for acme storefront. Kotlin / Spring Boot
> 3.2 on JVM 21. Owned by the platform team.

## Install

Requires JDK 21 (Temurin) and a local Postgres 15. See
`docker-compose.yml` for the exact service set.

```bash
./gradlew :app:bootRun
```

The service binds to `:8080` by default; override with `SERVER_PORT`.

## Configuration

| Env var | Required | Default | Source |
| --- | --- | --- | --- |
| `CHECKOUT_DB_URL` | yes | — | `application.yml:12` |
| `CHECKOUT_DB_USER` | yes | — | `application.yml:13` |
| `FEATURE_CHECKOUT_REDESIGN` | no | `false` | `application.yml:28` |
```

Every table row cites the exact file + line number. No placeholders.

## Example 2 — ADR for an auth migration

**Prompt:** `/adk-docs:docs-write "ADR for moving to OIDC for service-to-service auth"`

**Phase 0:** doc-type = `adr`. Next free number under `docs/adr/` is
`0007`. Slug = `adr-0007-oidc-service-to-service`.

**Phase 3 draft (excerpt):**

```markdown
# ADR-0007: OIDC for service-to-service auth

- **Status:** Proposed
- **Date:** 2026-05-03
- **Authors:** @sujeet

## Context

Internal services currently authenticate with a shared static
symmetric key (`INTERNAL_API_SECRET`) rotated quarterly. Secret
rotation has caused 3 incidents in the last 12 months
(cross-reference `docs/postmortems/2025-Q4-auth-*.md`).

## Decision

Adopt OIDC client-credentials flow with a central issuer
(`auth.internal.acme`). Every service becomes an OIDC client; tokens
are JWT, short-lived (5 min), audience-bound to the target service.

## Consequences

**Positive:**
- Rotations become per-client, not global.
- Token introspection surfaces which client called which endpoint
  (visible in DD `peer.service` tag).

**Negative:**
- Every service must integrate an OIDC client library. See
  §"Implementation" for the list of impacted repos.
- Initial rollout requires dual-stack (static key + OIDC) for 4 weeks.

## Alternatives considered

- **mTLS via internal CA.** Rejected: operational overhead of CA
  rotation; less observable than JWT claims.
- **Rotating symmetric keys more aggressively.** Rejected: addresses
  symptom, not root cause (any symmetric rotation can cause the same
  incident class).
```

## Example 3 — runbook for on-call rotation

**Prompt:** `/adk-docs:docs-write "runbook for on-call rotation" --audience mixed`

**Phase 3 draft (excerpt):**

```markdown
# Runbook: Platform on-call rotation

> **TL;DR (pm/em):** 1-week rotation across 6 engineers. Primary takes
> all alerts; secondary is fallback. Handoff is Monday 10:00 UTC.
> Escalation path below.

## Purpose

Keep the platform services (checkout-api, order-service, inventory)
above their SLOs (p99 < 500ms for checkout; error rate < 0.1%) during
the rotation window.

## Preconditions

- PagerDuty schedule configured (schedule id: `P1B2C3D`).
- `#platform-oncall` Slack channel membership current.
- Laptop battery > 50%; VPN working.

## Steps

### When a page fires

1. Open the DD alert link from the page. Identify service + SLO.
2. Post `ack` in `#platform-oncall` within 5 minutes.
3. Check the Production Overview dashboard:
   https://app.datadoghq.com/dashboard/abc-123-xyz (from `datadog.md`).
4. Run `adk-investigate:investigate-incident <alert-url>` to
   cross-reference recent deploys.
```

## Example 4 — migration guide

**Prompt:** `/adk-docs:docs-write "migration guide for moving to OIDC"
--fix`

Phase 2 reads: the new auth library version, `CHANGELOG.md` for
breaking changes, the upstream OIDC docs (WebFetch, ≤15-word quotes).

Phase 3 draft promoted to `docs/migrations/static-key-to-oidc.md`
with sections: Before you start, Step-by-step, Rollback plan,
Verification checklist, FAQ. Every step cites the exact command or
config change.
