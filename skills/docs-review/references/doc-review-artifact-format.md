# Artifact Format for `adk-docs-review`

The deliverable depends on mode:

- `--mode local`: a Markdown report under `.temp/reports/`.
- `--mode confluence`: inline + footer comments on the live Confluence page, plus a Markdown mirror under `.temp/`.

Working notes always live under `.temp/`.

## Artifact type

`doc-review-report` (local mode) OR `doc-review-comments` (confluence mode).

## Format per piece

| Piece | Format | Required shape |
| --- | --- | --- |
| Markdown report | Markdown file | `doc-review-output-format.md` shape |
| Inline comment (Confluence) | Confluence wiki Markdown | `doc-review-comment-format.md` canonical template, anchored to a verbatim text snippet |
| Footer comment (Confluence) | Confluence wiki Markdown | `doc-review-comment-format.md` `## Doc review summary` section |
| Reply (Confluence) | Confluence wiki Markdown | `doc-reply-templates.md` per reply type |

## Path / Location

| Artifact | Location |
| --- | --- |
| Markdown report | `.temp/reports/doc-review-<slug>.md` |
| Validator log | `.temp/notes/doc-review-<slug>-validator.md` |
| Drafts (pre-approval) | `.temp/drafts/doc-review-<slug>-drafts.md` |
| Reconciliation map (Confluence) | `.temp/notes/doc-review-<slug>-reconciliation.md` |
| Fetched page snapshot (Confluence) | `.temp/notes/doc-review-<slug>-page-snapshot.html` |
| Cloned source-of-truth repo | `.temp/reference-repos/<owner>__<repo>/` |
| Inline + footer comments (Confluence) | The Confluence page itself (no local copy of the rendered comments) |

`<slug>` = either the doc filename (local) or the Confluence page ID + slug (e.g., `confluence-12345-system-design`).

## .temp/ contract

All intermediate artifacts (drafts, reconciliation maps, raw notes, validator logs, fetched HTML, cloned reference repos) MUST be written under `.temp/` in the host repo, using these subfolders:

| Path | Purpose |
| --- | --- |
| `.temp/plans/<slug>.md` | Implementation, refactor, or migration plans |
| `.temp/drafts/<slug>.md` | Prose drafts before posting |
| `.temp/reports/<slug>.md` | Reviews, audits, investigations |
| `.temp/notes/<slug>.md` | Short-lived working notes (validator log, reconciliation map, fetched snapshot) |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos for cross-repo source-of-truth reads |

`.temp/` is gitignored. Promote a file out of `.temp/` ONLY when it is the deliverable the user asked for, in the location they asked for it.

## Promotion rule

Local mode: the `.temp/reports/doc-review-<slug>.md` STAYS in `.temp/` unless the user explicitly asks to commit it to the repo (e.g., into `docs/reviews/`).

Confluence mode: "promotion" = posting to the live page. The local Markdown mirror under `.temp/reports/` STAYS in `.temp/` — it is for the user's audit / replay, not a tracked deliverable.

## Idempotency (Confluence mode)

- Re-running on the same page must NOT re-post already-posted comments. The reconciliation step + the per-finding stable IDs in `.temp/drafts/` are what enforce this.
- The validator's Phase 4 records Confluence-returned comment IDs in the validator log. A second run reads that log first to identify previously-posted findings.

## Local mode is a one-way read

In `--mode local`, the skill never touches the doc file itself. It produces the report and stops. If the user wants the findings applied to the doc, that is a separate `adk-docs-write` invocation.
