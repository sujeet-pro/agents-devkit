# `docs-publish-gdrive` — anti-patterns

## Sharing

- **Calling any `permissions.*` endpoint.** Ever. The skill doesn't
  own sharing. Not even `permissions.list` as a "convenience check"
  — rely on the file metadata for the invariant check.
- **Auto-sharing with the operator's email.** The service account
  publishes; the operator's manual "share" flow (in the UI) decides
  who sees.
- **"Making a file public."** Never.
- **Changing link-access settings.** Never.

## Idempotency

- **Duplicate-by-retry.** `foo (1).md`, `foo (2).md` — classic
  symptom of skipping the existence check.
- **Matching by name only (ignoring mime).** A `foo.md` and a
  `foo` (GDoc) can coexist — match by name AND mime AND parent.
- **Auto-picking between N>1 matches.** Stop and ask.
- **Retrying a 409 without refreshing.** Race loop.

## Conversion

- **Uploading markdown with `.gdoc` in the filename** when the user
  asked for `--format gdoc`. A GDoc isn't a file with a name; it's
  a Drive item with mime `application/vnd.google-apps.document`.
- **Losing Mermaid / code fences** when converting to GDoc. The
  conversion must produce equivalent structure (code as fixed-width,
  mermaid as a placeholder image or a rendered SVG inserted).
- **Not stripping frontmatter** when uploading `.md`. The YAML at
  the top of the file shouldn't leak into the uploaded content
  for human readers.

## Scope

- **Batch publishing multiple files in one run.** Cap = 1. Loop.
- **Moving a file between folders.** Out of scope.
- **Deleting old items.** Out of scope.
- **Converting a GDoc back to markdown** — that's a read operation;
  use the Drive connector directly.
- **Uploading to a shared drive without verifying the service
  account has access.** The preflight check catches this.

## Process

- **Running the write without the Phase 4 ask.** Even under
  `--auto`. Shared-state; confirm.
- **Skipping Phase 5.** The sharing-drift check is an invariant;
  without it, the skill could silently mis-share.
- **Silent retries on 5xx.** Surface; don't loop.
- **Treating a partial-success (file created, but sharing drifted)
  as success.** It's not; report it as a failure even though the
  content landed.
