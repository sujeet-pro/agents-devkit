# `docs-publish-confluence` — anti-patterns

## Idempotency

- **Creating a duplicate page on retry.** The user reran the skill
  and got `<title> (1)`. The existence check is non-negotiable.
- **Matching by title only (no parent).** Two pages with the same
  title under different parents is common; match both dimensions.
- **Ignoring the `last-editor` field.** A human edited the page;
  overwriting silently is a trust violation.
- **Retrying on a 409 without refreshing existence.** You'll race
  with the other editor in a loop.

## Conversion

- **Pasting raw markdown as storage format.** Some renderers
  tolerate it; Confluence's storage format is XHTML, and raw
  markdown produces noisy output (especially for code fences and
  tables).
- **Losing Mermaid code fences.** Without the macro wrapping,
  Confluence renders Mermaid as plain code; the
  `ac:structured-macro` wrapper is required.
- **Rendering relative links verbatim.** A markdown link
  `[Foo](../bar.md)` doesn't resolve on Confluence; rewrite to
  absolute repo URLs or to Confluence page links if the target is
  also published.
- **Flattening admonitions.** GitHub's `> [!NOTE]` syntax → Confluence
  `ac:structured-macro` info/warning/tip panel. Don't lose the
  visual signal.

## Labels

- **Clobbering existing labels.** Union instead; preserve editor-
  applied labels.
- **Auto-adding loud labels.** Default `adk-published` is fine;
  avoid adding 10 labels per page.

## Restrictions / sharing

- **Setting restrictions automatically.** Out of scope entirely.
- **"Making the page public" automatically.** Never.
- **"Locking the page" automatically.** Never.

## Scope

- **Publishing multiple pages in one run.** Cap = 1 per invocation.
  Batches loop through the skill.
- **Deleting old pages after publishing a new one.** Deletion is
  out of scope.
- **Moving pages between parents.** Only when `--parent` changes and
  the user confirms; even then, the skill prefers to update in place
  rather than move.
- **Touching unrelated pages in the space.** Never.

## Verification

- **Claiming success without re-fetching.** Post-publish verify is
  a gate.
- **Tolerating a silent conversion drift.** If the re-fetched
  storage doesn't match, surface the diff; don't retry.
