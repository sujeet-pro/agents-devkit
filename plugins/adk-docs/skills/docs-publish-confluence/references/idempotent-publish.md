# Idempotent publish protocol

The match-by-title-and-parent contract that keeps
`docs-publish-confluence` from generating duplicate pages on retry.

## The core guarantee

For any fixed `<md-file>` + `--space` + `--parent`, the skill
converges to **exactly one** Confluence page. Rerunning the skill
on the same inputs produces the same page, version-incremented if
content changed.

## Match query

The existence check queries the Atlassian connector for:

```
space = <space>
parent.title = <parent>
title = <title>
```

The title is resolved in this order:

1. Markdown frontmatter `title:` (if present).
2. First H1 in the markdown (`# ...`).
3. Filename basename (kebab → title-cased).

## Match outcomes

### 0 results → `new`

Create a page. Parent resolved to page id (single query against
the connector).

### 1 result → `update` or `defer`

Capture:

- `page_id`
- `version` (for optimistic concurrency)
- `last_editor` (user account)
- `last_updated` (ISO)
- `existing_labels` (array)

Classify `last_editor`:

- Bot:
  - Account ids matching `adk-*` (the adk service accounts).
  - Account ids matching `atlassian-user-*` (Atlassian's generated
    bot accounts for connectors).
  - The operator's OAuth-attached bot identity, if `docs.md`
    declares a `bot_user_id` field.
- Human: anyone else.

For bot → `update` default.
For human → `defer` default; requires explicit opt-in.

### N>1 results → STOP

The match is ambiguous. Surface all matching page ids + URLs. The
user picks which to update (or creates a new one with a disambiguated
title).

## Update flow

1. Pass `expected_version = <captured version>` to the connector's
   update call. If the version changed (409), re-run Phase 3 and
   re-ask.
2. Submit the new `storage.xhtml` as body.
3. Submit the label set as `existing_labels ∪ requested_labels`
   (union — never clobber existing labels).
4. Do NOT change:
   - `restrictions` — not touched.
   - `author` — not touched (page keeps its original author).
   - `creator` — not touched.
   - `parent` — only if `--parent` was explicitly changed.
   - `position` — not touched.

## New-page flow

1. Pass `parent_id = <parent resolved in Phase 1>`, `title =
   <title>`, `body = <storage.xhtml>`, `labels = <requested>`.
2. Do NOT set `restrictions` — inherits from parent (Confluence
   default).
3. Do NOT set `creator` explicitly — the connector's service
   account is the creator.

## Post-publish verification

Re-fetch the page by id. Compare:

- `body.storage.value` to local `storage.xhtml`.
- Expected diff = 0 bytes, modulo:
  - Macro `ac:macro-id` attributes that Confluence adds on save.
  - Trailing whitespace normalization.
  - Auto-generated anchor `id` attributes on headings.

If the diff exceeds the allowed differences, surface:

```
Storage drift detected after publish. See .temp/task-<slug>/drift.txt.
Do NOT automatically retry; inspect the drift and rerun if
appropriate.
```

## Labels idempotency

The label-update flow is:

1. Read existing labels (from the existence check).
2. Compute the union with requested labels.
3. Submit the union.
4. Confirm post-publish: set match.

Never remove a label. Label removal is out of scope.

## Retry policy

- On 5xx from the connector: no auto-retry. Surface.
- On 409 version conflict: refresh existence check + re-ask (user
  decides).
- On 404 for parent: stop with a clear "parent was deleted" message.
- On 403 (permission): stop with a clear "skill account lacks
  write permission on space/parent" message.

## When NOT to use this skill

- Creating a space or parent page for the first time: out of
  scope. The parent must already exist.
- Deleting or archiving a page: out of scope.
- Moving a page to a different parent: only via `--parent` change
  + explicit confirmation; the skill prefers an in-place update.
- Changing restrictions or sharing: out of scope, period.
