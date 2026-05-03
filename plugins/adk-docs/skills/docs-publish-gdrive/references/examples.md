# `docs-publish-gdrive` — worked examples

## Example 1 — publish as new GDoc

**Prompt:** `/adk-docs:docs-publish-gdrive docs/design/exports-v1.md --folder 1AbCdEf --format gdoc`

**Phase 0:** source = `docs/design/exports-v1.md`. Target name =
"Exports v1 — design" (from H1). Folder id `1AbCdEf`. Format =
`gdoc`.

**Phase 1:** Google Drive workspace connector connected. Folder
exists; writable by the service account. Folder inherited
permissions snapshot: `[domain:acme.com:reader]` + the service
account.

**Phase 2:** convert markdown to GDoc ops. Headings, paragraphs, 1
code fence (rendered as fixed-width block), 1 table, 0 mermaid.

**Phase 3:** no existing item named "Exports v1 — design" in
folder. Action = `new`.

**Phase 4 ask:**

```
Publish docs/design/exports-v1.md as "Exports v1 — design"
(gdoc) into folder 1AbCdEf? Sharing will NOT be changed. [yes / no]
```

User confirms. Connector `files.create` returns item id `1XyZ123`.

**Phase 5:**
- Metadata re-fetched; matches plan.
- Permissions re-fetched: `[domain:acme.com:reader]` + service
  account. Matches pre-publish snapshot. Drift = none.

**Report:** URL `https://docs.google.com/document/d/1XyZ123/edit`.

## Example 2 — update an existing bot-authored GDoc

**Prompt:** `/adk-docs:docs-publish-gdrive docs/design/exports-v1.md --folder 1AbCdEf --format gdoc --auto`

**Phase 3:** existing GDoc "Exports v1 — design" found, id `1XyZ123`,
last editor the service account. Action = `update`.

**Phase 4 ask (even under `--auto`):**

```
Existing GDoc "Exports v1 — design" (id 1XyZ123) found in folder
1AbCdEf. Last editor: adk-service@acme.com (bot). Update?
[yes / no / diff]
```

Confirm. Connector `files.update` increments the revision.

**Phase 5:** metadata matches; permissions unchanged. OK.

## Example 3 — refuse to overwrite human-edited GDoc

**Phase 3:** found; last editor `sujeet@onequince.com` (human);
last modified 4 hours ago.

**Phase 4:**

```
Existing GDoc was last edited by sujeet@onequince.com (a human) 4
hours ago. Default: DEFER (leave as-is).

Options: yes, update | no | diff
```

Under `--auto`, the skill defaults to DEFER; "yes, update" must be
explicit from the user. Report ends with "deferred; rerun with
explicit opt-in".

## Example 4 — upload as .md

**Prompt:** `/adk-docs:docs-publish-gdrive README.md --folder 1AbCdEf --format md`

**Phase 2:** strip frontmatter; leave the rest intact.

**Phase 3:** existing `README.md` in folder? Yes, mime `text/plain`
(Drive doesn't use `text/markdown` for uploaded `.md` by default —
the connector lets the skill set mime explicitly). Action =
`update`.

Phase 4/5: standard flow.

## Example 5 — publish as PDF

**Prompt:** `/adk-docs:docs-publish-gdrive docs/design/exports-v1.md --folder 1AbCdEf --format pdf`

**Phase 1:** verify pandoc is available. If not, stop with
`brew install pandoc`.

**Phase 2:** render
`pandoc docs/design/exports-v1.md -o .temp/task-<slug>/converted.pdf
--toc`.

**Phase 3:** existing `Exports v1 — design.pdf` in folder? Check
mime `application/pdf`.

Phase 4/5: standard flow.

## Example 6 — sharing drift detected (failure case)

**Phase 5:** permissions re-fetch returns
`[domain:acme.com:reader, user:external@gmail.com:writer]`.
Pre-publish snapshot had no `external@gmail.com`.

**Response:**

```
ABORT: sharing drift detected post-publish.

The item at folder 1AbCdEf / "Exports v1 — design" has an
unexpected permission after publish:
  + user:external@gmail.com (writer)

This skill does NOT change sharing, so this permission was
introduced by something other than the publish (a concurrent
external change, or an unexpected connector behavior).

Inspect manually. The publish itself landed; the sharing invariant
did not.
```

The publish is NOT retried. The user investigates manually.
