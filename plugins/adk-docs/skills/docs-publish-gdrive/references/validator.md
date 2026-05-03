# `docs-publish-gdrive` — per-phase validator

Logged to `.temp/task-<slug>/validation/docs-publish-gdrive.md`.

## Phase 0

- [ ] `<md-file>` exists and is readable.
- [ ] `<folder-id>` resolved from CLI or `docs.md` default.
- [ ] Format resolved (`gdoc` | `md` | `pdf`).
- [ ] `.temp/task-<slug>/` exists, gitignored.
- [ ] `source.md` written.

## Phase 1

- [ ] `bin/adk-info --check` == 0.
- [ ] Workspace Google Drive connector `connected`.
- [ ] Folder exists (connector `files.get`).
- [ ] Folder writable by the service account.
- [ ] Folder permissions snapshot captured.
- [ ] If format=pdf: pandoc available.

## Phase 2

- [ ] Converted artifact exists at the canonical path.
- [ ] For gdoc: ops body is valid JSON.
- [ ] For md: frontmatter stripped; file non-empty.
- [ ] For pdf: file non-empty; pandoc exit 0.

## Phase 3

- [ ] `existence-check.md` captured query + result.
- [ ] If N>1, stopped and surfaced.
- [ ] Action decided (`new` | `update` | `defer`).

## Phase 4

- [ ] `publish-plan.md` matches connector call.
- [ ] `publish-plan.md` contains the "Sharing: will NOT be changed"
      line verbatim.
- [ ] No `permissions.*` call was prepared or made.
- [ ] User confirmed ask-once.
- [ ] Connector returned 2xx.

## Phase 5 — sharing-policy invariant

- [ ] Re-fetched item metadata.
- [ ] `name` / `mime` / `parents` match plan.
- [ ] Re-fetched permissions.
- [ ] `sharing-snapshot.md` written with pre + post.
- [ ] Diff between pre and post is empty (modulo the connector's
      service account identity).
- [ ] If diff exists: **STOP** — mark as failure; do not report
      success.

## Content guardrails

- [ ] No duplicate item created.
- [ ] No human-authored overwrite without explicit opt-in.
- [ ] No sharing change attempted.
- [ ] No move between folders.
- [ ] No delete call.

## On failure

- Log + block next phase.
- Sharing drift = final failure; do not retry.
- After 3 same-kind failures (other than sharing drift), stop and
  surface.
