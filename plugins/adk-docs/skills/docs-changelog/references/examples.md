# `docs-changelog` — worked examples

## Example 1 — Keep a Changelog, no breaking changes

**Range:** `v1.1.3..v1.2.0`. Commits: 12 (`feat` × 4, `fix` × 6,
`chore` × 2).

**`changelog-entry.md`:**

```markdown
## [1.2.0] - 2026-05-03

### Added
- Partial-refund support for gift orders. The refund endpoint now
  accepts a `lines` array to refund individual line items. ([#2840][])
- Export-history screen in the order-history flow, gated by
  `FEATURE_EXPORTS` (default `false`). ([#2841][])

### Changed
- Checkout's add-to-cart endpoint now clamps `quantity` to the
  current inventory snapshot and returns `{ clamped: true, actual:
  <n> }` when the clamp fires. ([#2841][], [#2845][])
- SDK retry policy upgraded to use exponential backoff with
  jitter; previously linear. ([#2838][])

### Fixed
- Race between add-to-cart and checkout that could lose one cart
  line under concurrent-tab use. ([#2791][])
- Stuck "processing" state on the payments screen when the
  provider returned a 422 without a retry header. ([#2823][])
- Intermittent 500 on `/orders/:id/refund` when the order had been
  archived. ([#2801][])

[#2840]: https://github.com/acme/checkout-api/pull/2840
[#2841]: https://github.com/acme/checkout-api/pull/2841
...
```

## Example 2 — Keep a Changelog, with a breaking change

**Range:** `v1.9.0..v2.0.0`. Commits include
`feat!: remove legacyLogin`.

**`changelog-entry.md`:**

```markdown
## [2.0.0] - 2026-05-12

### Breaking changes
- `AuthClient.legacyLogin()` is removed. Migrate to
  `AuthClient.loginWithOidc()` — see the migration guide at
  `docs/migrations/legacy-to-oidc.md`. ([#2901][])
- `POST /v1/auth/session` no longer accepts the `username` body
  field; use `email` instead. ([#2901][])

### Added
- `AuthClient.loginWithOidc()` implementing OIDC client-credentials
  against the central issuer. ([#2901][])

### Removed
- `AuthClient.legacyLogin()` (see Breaking changes above).
- `INTERNAL_API_SECRET` env var (unused as of this release).

### Fixed
- Session refresh returned a 401 when the OIDC issuer's clock was
  skewed >30s; now accepts ±120s skew per RFC 7519. ([#2928][])
```

## Example 3 — semantic-release style

**Range:** `v3.0.1..v3.1.0`. Commits: Conventional Commits;
existing changelog uses the `### Features` / `### Bug Fixes` shape.

**`changelog-entry.md`:**

```markdown
## [3.1.0](https://github.com/acme/checkout-api/compare/v3.0.1...v3.1.0) (2026-05-15)

### Features

* **orders:** partial-refund support for gift orders ([abc1234](https://github.com/acme/checkout-api/commit/abc1234))
* **ui:** export-history screen in order history, gated by
  `FEATURE_EXPORTS` ([def5678](https://github.com/acme/checkout-api/commit/def5678))

### Bug Fixes

* **checkout:** clamp add-to-cart quantity to inventory ([a1b2c3](https://github.com/acme/checkout-api/commit/a1b2c3))
* **payments:** handle 422 without retry header ([b2c3d4](https://github.com/acme/checkout-api/commit/b2c3d4))
```

## Example 4 — free-form changelog

**Existing file:** uses a single "Release YYYY-MM-DD" header per
release with bullet-point entries, no categories.

**`changelog-entry.md`:**

```markdown
## Release 2026-05-03

- Adds partial refunds for gift orders. (#2840)
- Adds export history in the order-history screen, gated behind
  `FEATURE_EXPORTS`. (#2841)
- Clamps add-to-cart quantity to current inventory. (#2841, #2845)
- Fixes a race between add-to-cart and checkout under
  concurrent-tab use. (#2791)
- Fixes stuck "processing" state on payments. (#2823)
```
