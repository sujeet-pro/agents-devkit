# Changelog & Release Notes Guidelines

Guidelines for writing and reviewing changelogs and release notes. A changelog is the historical record of what changed in a project. Release notes are the curated summary of what matters to users in a specific release. Both must be accurate, complete, and useful.

**Audience**: Engineers consuming the library/service (changelog) and product stakeholders, developer relations, and end users (release notes).

**Reference**: Based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning 2.0.0](https://semver.org/adk-spec/v2.0.0.html).

---

## 1. Changelog vs Release Notes

These are related but distinct documents:

| Aspect | Changelog | Release Notes |
|--------|-----------|---------------|
| Audience | Engineers consuming the project | Broader audience including product, support, users |
| Scope | Every notable change, exhaustive | Key changes, curated highlights |
| Format | Structured list grouped by category | Narrative with highlights, migration guide |
| Location | `CHANGELOG.md` in repo root | GitHub release, blog post, documentation site |
| Granularity | Individual changes with PR/commit links | Features and breaking changes, grouped by theme |

Both should exist. The changelog is the source of truth; release notes are derived from it.

---

## 2. Changelog Format

Follow the [Keep a Changelog](https://keepachangelog.com/) format strictly.

### File Structure

```markdown
# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/adk-spec/v2.0.0.html).

## [Unreleased]

### Added
- New endpoint for bulk user import (`POST /v1/users/bulk`). (#423, @engineer-a)

### Fixed
- Race condition in connection pool under high concurrency. (#419, @engineer-b)

## [2.1.0] - 2024-09-15

### Added
- OAuth 2.0 PKCE flow support for mobile clients. (#401, @engineer-c)
- Rate limit headers on all API responses. (#405, @engineer-a)

### Changed
- Default pagination size from 100 to 50 for List endpoints. (#410, @engineer-d)

### Deprecated
- API key authentication for user-facing endpoints. Use OAuth 2.0 instead. Will be removed in v3.0.0. (#412, @engineer-a)

### Fixed
- Incorrect timezone handling in `created_at` timestamps for AU region. (#408, @engineer-b)

## [2.0.0] - 2024-08-01

### Added
- Webhook signature verification using HMAC-SHA256. (#380, @engineer-c)

### Changed
- **BREAKING**: Error response format changed from flat object to nested `error` object. See [migration guide](docs/migration-v2.md). (#375, @engineer-a)
- **BREAKING**: All timestamps now use ISO 8601 with UTC timezone. (#378, @engineer-d)

### Removed
- **BREAKING**: Removed deprecated `/v1/legacy-auth` endpoint. (#382, @engineer-b)

### Security
- Upgraded TLS minimum version from 1.2 to 1.3. (#385, @engineer-c)

[Unreleased]: https://github.com/example/adk-project/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/example/adk-project/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/example/adk-project/releases/tag/v2.0.0
```

### Categories

Use these categories in this order. Omit empty categories.

| Category | What Goes Here |
|----------|---------------|
| **Added** | New features, new endpoints, new capabilities |
| **Changed** | Changes to existing functionality (behavior, defaults, performance) |
| **Deprecated** | Features that will be removed in a future release |
| **Removed** | Features removed in this release |
| **Fixed** | Bug fixes |
| **Security** | Vulnerability patches, security improvements |

### Entry Format

Each entry must include:
- A brief, imperative description of the change (what was done, not what was wrong).
  - **Wrong**: "There was a bug where users could not log in after password reset."
  - **Right**: "Fix login failure after password reset when MFA is enabled."
- A PR or commit reference in parentheses: `(#423)` or `(abc1234)`.
- Author attribution: `@username`.
- For breaking changes: prefix with `**BREAKING**:` and include a link to the migration guide.

### Date Format

- Use ISO 8601: `YYYY-MM-DD`.
- Always UTC. Do not use localized dates.
- The date represents when the version was released, not when changes were merged.

### Comparison Links

- Every version heading must link to a diff comparison at the bottom of the file.
- `[Unreleased]` links to `compare/vCURRENT...HEAD`.
- Each version links to `compare/vPREVIOUS...vCURRENT`.

---

## 3. Semantic Versioning

Follow [Semantic Versioning 2.0.0](https://semver.org/) for version numbers: `MAJOR.MINOR.PATCH`.

| Component | When to Increment | Example |
|-----------|-------------------|---------|
| **MAJOR** | Breaking changes to the public API | Removing an endpoint, changing response format, changing authentication |
| **MINOR** | New functionality that is backward-compatible | New endpoint, new optional parameter, new webhook event |
| **PATCH** | Backward-compatible bug fixes | Fix incorrect validation, fix race condition, fix typo in error message |

Additional rules:
- Pre-release versions: `1.0.0-alpha.1`, `1.0.0-beta.2`, `1.0.0-rc.1`.
- Build metadata: `1.0.0+build.123` (does not affect version precedence).
- Version `0.x.y` signals instability: breaking changes may occur in MINOR increments.
- Once `1.0.0` is released, the public API is defined, and semver rules are strictly enforced.

### What Constitutes a Breaking Change

A breaking change is any change that can cause existing consumers to fail without modification:
- Removing a field from a response body.
- Renaming a field or changing its type.
- Changing the meaning of a field value.
- Removing an endpoint or HTTP method.
- Changing the authentication mechanism.
- Changing the error response format.
- Tightening input validation that previously accepted a broader range of values.
- Changing a default value that consumers may depend on.

The following are NOT breaking changes:
- Adding a new optional field to a request body.
- Adding a new field to a response body (consumers should ignore unknown fields).
- Adding a new endpoint.
- Adding a new error code for a case that previously returned a generic error.
- Relaxing input validation to accept a broader range of values.

> **Reference**: [Semantic Versioning 2.0.0](https://semver.org/adk-spec/v2.0.0.html),
> [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)

---

## 4. Release Notes

Release notes are the user-facing narrative derived from the changelog. They highlight what matters and provide context.

### Structure

```markdown
# Release v2.1.0

**Release date**: 2024-09-15

## Highlights

### OAuth 2.0 PKCE Support
Mobile clients can now use the Authorization Code flow with PKCE,
eliminating the need for a client secret on device. This follows
RFC 7636 and is recommended for all public client implementations.

See the [OAuth PKCE guide](docs/oauth-pkce.md) for integration instructions.

### Rate Limit Transparency
All API responses now include `X-RateLimit-*` headers so clients can
proactively manage their request budget instead of discovering limits
via 429 responses.

## Deprecation Notice

API key authentication for user-facing endpoints is deprecated and will
be removed in v3.0.0 (estimated Q1 2025). Migrate to OAuth 2.0 before
then. See the [migration guide](docs/migrate-to-oauth.md).

## All Changes

See the [full changelog](CHANGELOG.md#210---2024-09-15) for the complete
list of changes in this release.
```

### Release Notes Principles

- **Highlights over exhaustive lists**: Pick the 2-5 most impactful changes and explain them with context. Link to the full changelog for everything else.
- **Breaking changes get their own section**: If any breaking change exists, it must be the first thing the reader sees, with migration instructions.
- **Deprecation notices**: State what is deprecated, when it will be removed, and what to use instead.
- **Link to guides**: Do not explain complex migration steps in the release notes. Link to a dedicated migration guide.
- **Context over description**: "OAuth PKCE support" is a description. "Mobile clients no longer need to embed client secrets" is context that helps the reader evaluate impact.

---

## 5. Breaking Changes

Breaking changes require special treatment in both the changelog and release notes.

### In the Changelog
- Prefix with `**BREAKING**:`.
- Include a link to the migration guide.
- Appear in the `Changed` or `Removed` category (not `Added`).

### In Release Notes
- Dedicate a prominent section titled "Breaking Changes" at the top.
- For each breaking change, document:
  1. What changed.
  2. Why it changed.
  3. What breaks (which clients/integrations are affected).
  4. How to migrate (step-by-step or link to migration guide).
  5. Timeline: when support for the old behavior ends.

### Migration Guide
- Create a separate document (`docs/migration-vN.md`) for non-trivial migrations.
- Include before/after code examples:
  ```markdown
  ### Error Response Format

  **Before (v1)**:
  ```json
  { "code": "invalid_amount", "message": "Amount must be positive" }
  ```

  **After (v2)**:
  ```json
  {
      "error": {
          "type": "invalid_request_error",
          "code": "invalid_amount",
          "message": "Amount must be a positive integer greater than zero.",
          "param": "amount"
      }
  }
  ```

  **What to change**: Update your error parsing to read from `response.error.code`
  instead of `response.code`.
  ```
- Provide a deprecation period: old behavior still works for X releases/months.

---

## 6. Common Issues

- **Missing PR/commit links**: Entries without traceability. Every change must link to the code change.
- **Missing author attribution**: Not crediting the engineer who made the change.
- **Vague descriptions**: "Various bug fixes" or "Performance improvements." Be specific about what was fixed and what improved.
- **Wrong category**: A bug fix listed under "Changed" or a new feature under "Fixed." Use the correct category.
- **No Unreleased section**: Changes merged to main that are not yet in the Unreleased section. Update the changelog as part of the PR, not at release time.
- **Stale comparison links**: Version links at the bottom of the file that point to the wrong tags.
- **Breaking changes buried**: A breaking change listed as a regular entry without the `**BREAKING**` prefix or migration guide.
- **Changelog updated at release time**: The changelog should be updated in every PR. Batch-writing changelog entries at release time leads to missed items and vague descriptions.
- **Missing dates**: Versions without release dates, making it impossible to correlate changes with incidents or deployments.
- **Inconsistent versioning**: Not following SemVer rules (e.g., adding breaking changes in a PATCH release).

---

## 7. Process

1. **Every PR updates the changelog**: Add an entry under `[Unreleased]` in the appropriate category as part of the PR. This is a merge requirement.
2. **At release time**:
   - Move `[Unreleased]` entries to a new version heading with the release date.
   - Add a new empty `[Unreleased]` section at the top.
   - Update the comparison links at the bottom.
   - Write release notes derived from the changelog entries.
   - Tag the release with the version number.
3. **After release**:
   - Publish release notes to GitHub Releases, documentation site, or blog.
   - Notify consumers through appropriate channels (email, Slack, RSS).
   - For breaking changes, proactively contact known consumers with the migration guide.

---

## 8. Review Checklist

- [ ] Changelog follows Keep a Changelog format
- [ ] Entries are in the correct category (Added, Changed, Deprecated, Removed, Fixed, Security)
- [ ] Each entry has a brief imperative description
- [ ] Each entry has a PR/commit link and author attribution
- [ ] Breaking changes are prefixed with `**BREAKING**:` and link to a migration guide
- [ ] Deprecated items state what to use instead and when removal will occur
- [ ] Dates use ISO 8601 format (YYYY-MM-DD)
- [ ] Version numbers follow Semantic Versioning
- [ ] Version increment matches the nature of the changes (MAJOR for breaking, MINOR for features, PATCH for fixes)
- [ ] Comparison links at the bottom of the file are correct
- [ ] `[Unreleased]` section exists and is up to date
- [ ] Release notes highlight 2-5 key changes with context, not just a list
- [ ] Release notes have a breaking changes section if any exist
- [ ] Migration guide exists for non-trivial breaking changes with before/after examples
- [ ] No TODO/TBD placeholders remain
