# Breaking-change callout

How `docs-changelog` surfaces breaking changes in the version block.

## Detection

A commit is "breaking" if ANY of:

- Subject has `!` after the type/scope:
  `feat(auth)!: migrate to OIDC`.
- Body has a `BREAKING CHANGE:` footer (Conventional Commits spec).
- Body has a `BREAKING-CHANGE:` footer (alternate spelling some
  repos use).
- Diff removes a public symbol, a public endpoint, a published env
  var, or a published config key (heuristic; flag under `-i`).

## Placement

Breaking changes go FIRST in the version block, under a dedicated
`### Breaking changes` header, above all other categories.

Rationale: a reader checking "can I upgrade to this version?" looks
at the top of the version block. Burying breaks in the middle of
the "Changed" section risks silent upgrades followed by on-call
pages.

## Entry shape

Each breaking change is one sentence that:

1. Names the removed / renamed / changed symbol (or endpoint, or
   env var, or default) explicitly.
2. Points to the migration path:
   - Replacement method / endpoint / env var.
   - Migration guide path (`docs/migrations/<name>.md`).
   - PR reference for detail.

Examples:

```markdown
### Breaking changes
- `AuthClient.legacyLogin()` is removed. Migrate to
  `AuthClient.loginWithOidc()` — see `docs/migrations/legacy-to-oidc.md`.
  ([#2901][])
- `POST /v1/auth/session` no longer accepts the `username` body
  field; use `email` instead. ([#2901][])
- `INTERNAL_API_SECRET` env var is removed. Set
  `OIDC_CLIENT_SECRET` instead. ([#2901][])
- Default retry policy changed from linear to exponential-with-jitter;
  previously-hardcoded `retries: 3` is now a minimum, not a maximum.
  ([#2838][])
```

## When no migration path exists

Explicitly say so and link to the supporting issue:

```markdown
- Removed `legacyExport` endpoint. No replacement — downstream
  consumers should migrate to `/exports` (async job model). If you
  need a synchronous export, open an issue
  (https://github.com/acme/checkout-api/issues/new).
  ([#2850][])
```

## SemVer implications

A release with at least one breaking change SHOULD be a major
version bump. The skill flags a minor / patch release with breaking
changes as an inconsistency and surfaces it in the report:

```
WARN: v1.9.1 contains 2 breaking changes but is a PATCH bump per
SemVer. Recommend re-releasing as v2.0.0.
```

It does not block; release-versioning is the user's decision.

## Adjacent to existing breaking-change sections

If the file already uses a different header (e.g. semantic-release's
`### ⚠ BREAKING CHANGES`), match the existing exact spelling
(including the emoji / symbol) instead of imposing
`### Breaking changes`. Consistency within the file wins.

## Hard rules

1. **Never silently demote a breaking change** to `Changed` or
   `Removed`.
2. **Always place Breaking changes first** in the version block.
3. **Always name the affected symbol** (method / endpoint / env
   var / config key).
4. **Always link to the migration path** if one exists.
5. **Never invent a breaking change** that isn't signaled by `!`,
   `BREAKING CHANGE:`, or a public-surface removal in the diff.
6. **Never minimize** a breaking change to make a release look
   smoother ("minor cleanup" when it's actually an API removal).
