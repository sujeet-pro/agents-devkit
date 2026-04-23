# Feature flag lifecycle

Feature flags are not free. Every flag is **live config** that adds a branch in the codebase, an entry in the flag store, and a permanent risk of "what does this flag actually do today?" if left around.

## Flag states

```
created (off in prod) ── targeting (team) ── canary (1%/10%) ── ramp (50%) ── full (100%) ── cleanup (removed)
       │                       │                      │                    │              │             │
       │ default OFF           │ employees only       │ random %           │ random %     │ all users   │ flag check + flag store entry deleted
       └ deploy-only           └ smoke / dogfood      └ gate signals       └ gate signals └ stable      └ within ≤ 2 weeks of full
```

## Naming

- One name per flag, lowercase snake or kebab — match repo convention.
- Prefix by domain: `checkout_new_summary`, `auth_passkey_login`, `search_v2_reranker`.
- NEVER reuse a flag name for an unrelated feature.
- NEVER use `enable_x` then `disable_x` for the inverse — pick one polarity (positive: `is_new_x_enabled`).

## Defaults

- **Prod default: OFF.** Always.
- **Dev/test default: ON** (so the new path is exercised in CI).
- **Staging default: ON** (so QA sees the new path).
- **Documented default in code:** the fallback when the flag store is unreachable. Choose conservatively — usually OFF.

## Targeting

- Internal employees first (`@yourcompany.com` / explicit user ID list).
- Then a small random %.
- Then a larger random %.
- Then 100%.
- For partner-affecting changes: target by partner ID, not random %.

## Cleanup ticket

Filed at the SAME TIME the flag is created. Linked to the original change. Target: ≤ 2 weeks after Stage 5 (100%). Contents:

- Flag name.
- Date created + owner.
- Date hit 100%.
- Removal target date.
- Removal PR link (filled when done).

## Anti-patterns

- "Permanent" flags that gate two divergent code paths forever — if it's permanent, it's not a flag, it's config.
- Nested flags (flag-A AND flag-B) — combinatorial explosion of code paths.
- Flag check inside hot loops — push the check up to a one-time read at request boundary.
- Flag removed from code but left in the flag store (or vice versa) — both must go together.
- Flag default ON in prod "to make the migration easier" — defeats the purpose; you can't roll back.
- Long-lived "kill switches" disguised as feature flags — kill switches are operational config, not feature flags; document them as such.

## When NOT to use a feature flag

- Doc-only / config-only changes with no runtime branch.
- Truly trivial UI tweaks (one-line copy change). Even then, lean toward a flag if customer impact is non-zero.
- Internal-only refactors with no observable behavior change (use `@adk:build-refactor`).
- Hotfix during incident — fix forward, don't add complexity.
