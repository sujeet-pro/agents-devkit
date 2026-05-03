# `docs-changelog` — anti-patterns

## Content

- **Git-log paste as entries.** "feat(orders): partial-refund hook"
  is a commit subject, not a changelog entry. The reader isn't the
  author.
- **Missing breaking-changes section** when the release has breaking
  commits. Downstream integrators rely on this section to know what
  to update.
- **One giant "Other" bucket** swallowing every non-feature change.
  Use the detected style's categories.
- **Inventing items** that aren't in the commit range — to "round
  out" the release or make it look fuller.
- **Sub-entries that are too technical.** "Refactored
  `CartService.addLine` to use `clampToInventory`" — the user
  cares that quantities are now clamped, not about the internal
  method rename.
- **Marketing phrases.** "Massive performance improvements" without
  a number. If you have a number, state it.

## Structure

- **Wrong group order.** Keep a Changelog orders
  Added / Changed / Deprecated / Removed / Fixed / Security.
  Don't reshuffle.
- **Mixing styles in one version block.** If the rest of the file
  uses Keep a Changelog, don't suddenly write a semantic-release
  block.
- **Missing the release date.** Keep a Changelog requires
  `## [VERSION] - YYYY-MM-DD`.
- **Un-linked PR / commit references.** A reader can't navigate to
  the source of a claim. Link to the PR.

## Process

- **Auto-committing CHANGELOG.md.** Out of scope. Stage and stop.
- **Overwriting a previously-published version block** without user
  opt-in. The PR that shipped the release likely referenced the
  changelog text — rewriting it desynchronizes.
- **Promoting the "Unreleased" section to a versioned block** without
  explicit user confirmation. That's a release-management decision.
- **Running `git tag` or `git push`.** Out of scope.

## Scope

- **Summarizing 300 commits into a "big release" changelog.** The
  skill will do it, but the output is degraded. Recommend cutting
  intermediate releases next time.
- **Turning a changelog into release-marketing copy.** The changelog
  is a technical record. Marketing copy is a separate artifact
  (`docs-write` with a launch-post template).

## Breaking changes

- **Silent breaking changes.** If a commit has `!` or
  `BREAKING CHANGE:`, it MUST surface in a dedicated callout.
- **Breaking change buried mid-list.** Top of the version block,
  dedicated header, per `references/breaking-change-callout.md`.
- **Vague breaking-change descriptions.** "Auth changed" — name
  the removed symbol, the renamed endpoint, the changed default.
