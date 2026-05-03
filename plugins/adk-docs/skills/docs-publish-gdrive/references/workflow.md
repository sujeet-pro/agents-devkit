# `docs-publish-gdrive` — workflow detail

## Phase 0 — prompt expansion

1. Read `<md-file>`; verify it exists.
2. Resolve folder id:
   - CLI `--folder` → `docs.md.default_gdrive_folder_id`.
3. Resolve format:
   - CLI `--format` → default `gdoc`.
4. Pick slug: `publish-gdrive-<basename>`. Create `.temp/task-<slug>/`.
5. Copy source to `source.md` (audit).

## Phase 1 — preflight

1. `bin/adk-info --check`.
2. Verify the workspace Google Drive connector is connected.
3. Get folder metadata:
   - Exists?
   - Writable by the connector's service account?
   - Snapshot the folder's sharing state to confirm later (read-only
     snapshot; never modifies).
4. If `--format pdf`: check local `pandoc` or diagramkit's PDF mode
   is available. If not, stop with the install hint.

## Phase 2 — convert

Branch by format (per `references/markdown-to-gdoc.md`):

- **`gdoc`**: convert markdown to GDoc ops (structured document
  model Google Drive accepts). Write to
  `.temp/task-<slug>/converted.gdoc.json`.
- **`md`**: strip frontmatter only. Write to
  `.temp/task-<slug>/converted.md`.
- **`pdf`**: render via `pandoc <source> -o converted.pdf` with the
  `--toc` flag when the source has >3 headings. Write to
  `.temp/task-<slug>/converted.pdf`.

## Phase 3 — idempotent existence check

Per `references/sharing-policy.md` + matching rules:

1. Query: item in folder `<folder-id>` with name `<target-name>`
   and mime matching the format:
   - `gdoc` → `application/vnd.google-apps.document`.
   - `md`   → `text/markdown` or `text/plain`.
   - `pdf`  → `application/pdf`.
2. Record in `existence-check.md`:
   - `found`, `item_id`, `revision`, `last_editor`, `last_modified`.
3. Classify as in `docs-publish-confluence`:
   - 0 → `new`.
   - 1 bot → `update`.
   - 1 human → `defer`.
   - N>1 → STOP (ambiguous).

## Phase 4 — publish (ask-once gate)

1. Write `publish-plan.md`.
2. Ask once:
   ```
   Publish <source.md> as <target-name> (<format>) into folder
   <folder-id>? Action: <new | update | defer>. Sharing will NOT
   be changed. [yes / no / diff]
   ```
3. On `yes`:
   - `new` → connector `files.create` with
     `name`, `mimeType`, `parents`, `media` body.
   - `update` → connector `files.update` with `item_id`, same body.
   - Explicitly do NOT pass any `permissions` field.
4. On `no` / `defer`: leave plan, report.

## Phase 5 — verify + sharing-policy enforcement

1. Re-fetch item metadata by id.
2. Verify:
   - `name` matches target.
   - `mimeType` matches format.
   - `parents` includes the requested folder id.
   - `size` ≈ converted artifact size.
3. Re-fetch permissions:
   - Compare pre-publish (from folder snapshot + item inherited
     permissions) to post-publish.
   - Expected: identical (modulo the connector's own service
     account which is always present).
   - Any drift → surface loudly; NOT considered success.
4. Write `sharing-snapshot.md`:
   ```
   pre_publish_permissions:  [folder inherited + service account]
   post_publish_permissions: [same]
   drift: none
   ```
5. Write `published.md` + final report.

## Loop control

- 5xx from the connector: no retry; surface.
- 409 (version conflict): refresh existence check; re-ask.
- 403 (permission): stop with "connector service account lacks
  write on folder".
- If sharing drift detected post-publish: STOP. The skill failed
  its invariant; the user must investigate.
