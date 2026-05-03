# `docs-publish-confluence` — workflow detail

## Phase 0 — prompt expansion

1. Read `<md-file>`. If missing, stop with "file not found".
2. Extract the title:
   - If the file has frontmatter `title:`, use it.
   - Else, use the first top-level H1 (`# ...`) in the file.
   - Else, derive from the filename basename.
3. Resolve space: CLI `--space` → `docs.md.default_confluence_space`.
4. Resolve parent: CLI `--parent` →
   `docs.md.default_confluence_parent`.
5. Pick slug: `publish-conf-<filename-basename>`. Create
   `.temp/task-<slug>/`.

## Phase 1 — preflight

1. `bin/adk-info --check` (at least `docs` topic must parse).
2. Check the workspace Atlassian connector:
   - Run `claude mcp list` (or the adk equivalent).
   - Confirm the connector is `connected`.
3. Query the connector to confirm the target space exists.
4. Query the connector to confirm the parent page exists in the
   space. If not, stop with the create-parent hint.

## Phase 2 — convert

1. Apply `references/markdown-to-confluence.md`:
   - Standard markdown → XHTML storage format.
   - Mermaid code fences → `<ac:structured-macro ac:name="mermaid">`.
   - Syntax-highlighted code fences → `<ac:structured-macro ac:name="code">`
     with the right language parameter.
   - Tables → `<table>`, `<tr>`, `<td>` (Confluence accepts raw
     HTML tables in storage format).
2. Extract labels:
   - If the markdown has frontmatter `labels: [..., ...]`, use those.
   - Else, apply the default `adk-published`.
   - Always keep existing labels on the page (union).
3. Write `.temp/task-<slug>/storage.xhtml`.

## Phase 3 — existence check (idempotency)

Per `references/idempotent-publish.md`:

1. Query: "space=<space>, parent=<parent>, title=<title>".
2. Record in `.temp/task-<slug>/existence-check.md`:
   - `found: true/false`.
   - If found: `page_id`, `version`, `last_editor`, `last_updated`,
     `existing_labels`.
3. Classify:
   - Not found → action = `new`.
   - Found, last-editor is bot → action = `update`.
   - Found, last-editor is human → action = `defer` (requires
     explicit opt-in).

## Phase 4 — publish (ask-once gate)

1. Write `.temp/task-<slug>/publish-plan.md` summarizing the plan
   (action, target page id if any, labels, one-line diff between
   existing storage and new storage for updates).
2. Ask the user once (even under `--auto`):
   ```
   Publish <md-file> (<title>) to space=<space>, parent="<parent>"?
   Action: <new | update | defer>
   [yes / no / diff (show)]
   ```
3. On `yes`:
   - `new` → connector `create-page` with parent id, title, body
     (storage.xhtml), labels.
   - `update` → connector `update-page` with page id, expected
     version (for optimistic concurrency), body, labels.
4. On `diff`: show a unified diff of existing storage vs new;
   re-ask.
5. On `no` / `defer`:
   - Leave `.temp/task-<slug>/publish-plan.md` in place.
   - Report ends with "not published; re-run when ready".

## Phase 5 — verify

1. Re-fetch the page by id (or by title+parent for new pages).
2. Compare: the returned storage format should byte-match
   `storage.xhtml` modulo:
   - Confluence inserting internal IDs on macro elements.
   - Whitespace normalization.
   - Auto-generated anchors.
3. Confirm the label set matches the union (existing + requested).
4. Write `.temp/task-<slug>/published.md`:
   ```
   page_id: 12345
   version: 7
   url: https://acme.atlassian.net/wiki/spaces/ENG/pages/12345/...
   labels: [runbook, platform, adk-published]
   verified_at: <ISO ts>
   ```
5. Write final report.

## Loop control

- If existence check returns multiple matches (same title + parent,
  different page ids), stop with the list. Not idempotent — user
  picks.
- If post-publish verification fails (the fetched storage doesn't
  match), **do not** retry silently. Capture the diff; surface.
- If the connector returns a 409 on update (version conflict), the
  page was updated between Phase 3 and Phase 4. Refresh existence
  check; re-ask.
