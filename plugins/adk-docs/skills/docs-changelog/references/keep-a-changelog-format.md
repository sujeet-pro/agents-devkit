# Keep a Changelog format

The default structure `docs-changelog` uses when no existing style is
detected, and the style detector's reference point.

## Top-of-file preamble (typical)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).
```

## "Unreleased" section

Optional, but canonical. Sits above all released versions.

```markdown
## [Unreleased]

### Added
- (work-in-progress items)

### Fixed
- (work-in-progress items)
```

When the user tags a release, the `docs-changelog` skill usually
renames the `Unreleased` header to `[VERSION] - YYYY-MM-DD` and
creates a new empty `Unreleased` block above it. The skill does NOT
do this promotion automatically — it's a release-management
decision. Surface it as a follow-up in the report.

## Release header format

```
## [VERSION] - YYYY-MM-DD
```

- `VERSION` — SemVer-shaped: `MAJOR.MINOR.PATCH` (no `v` prefix
  inside the brackets by Keep-a-Changelog convention; the footnote
  link at the bottom does include `v`).
- `YYYY-MM-DD` — ISO date. Today (or the release date) in UTC.

## Section headers (ordered)

1. `### Breaking changes` — if any commits are breaking. (Not
   standard Keep a Changelog, but the adk convention elevates
   breaks — see `references/breaking-change-callout.md`.)
2. `### Added`
3. `### Changed`
4. `### Deprecated`
5. `### Removed`
6. `### Fixed`
7. `### Security`

Empty sections are omitted.

## Entry shape

```
- <Imperative-starting sentence, ending with a period>. ([#NNNN][])
```

- Starts with an imperative verb (`Adds`, `Fixes`, `Removes`).
- One sentence. Multi-sentence entries get split into a short lead
  + a nested bullet:

  ```
  - Adds export history, gated by `FEATURE_EXPORTS`.
    - The history screen shows the last 30 days of exports.
    - Downloading a CSV uses the existing pre-signed URL flow.
    ([#2841][])
  ```

- PR footnote link at the end:

  ```
  [#2841]: https://github.com/acme/checkout-api/pull/2841
  ```

  Footnote definitions accumulate at the bottom of the file; the
  skill appends new ones on write.

## Footer links (bottom of file)

```
[1.2.0]: https://github.com/acme/checkout-api/compare/v1.1.3...v1.2.0
[#2841]: https://github.com/acme/checkout-api/pull/2841
```

The skill adds these link definitions at the bottom of the file
(just before any existing footer matter).

## Detection rule

A file is "Keep a Changelog" style when:

1. Top-of-file preamble references `keepachangelog.com` OR
2. At least 70% of the existing version blocks use the exact
   header format `## [VERSION] - YYYY-MM-DD` AND at least one of
   `### Added` / `### Fixed` section headers is present.

Record detection rationale in `detected-style.txt`.

## Migration from semantic-release output

If the file has inline commit links `([abc1234](<url>))` and
section headers `### Features` / `### Bug Fixes`, the repo uses
semantic-release. The skill follows `references/output-format.md`
for that variant — don't force-convert to Keep a Changelog.
