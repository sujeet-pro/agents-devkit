# Artifact Format for `adk-review-pr`

The deliverable is the set of comments posted to the remote PR (in `post` mode) plus a Markdown mirror under `.temp/`. Working notes always live under `.temp/`.

## Artifact type

`pr-review-comments` — a heterogeneous artifact composed of:

- 0..N inline comments on the PR (one per finding)
- 0..N reconciliation replies on existing threads
- 0..1 summary comment at the PR level
- 0..N Bitbucket tasks (provider-conditional)
- 1 Markdown report mirrored locally

## Format per piece

| Piece | Format | Required shape |
| --- | --- | --- |
| Inline comment | Provider Markdown | `pr-review-comment-format.md` canonical template |
| Reply | Provider Markdown | `pr-reply-templates.md` per reply type |
| Summary comment | Provider Markdown | `pr-review-comment-format.md` `## Review summary` section |
| Bitbucket task | Provider task | Title = finding short title; linked to the inline comment ID |
| Local Markdown mirror | Markdown file | The full report from `pr-output-format.md` |

## Path / Location

| Artifact | Location |
| --- | --- |
| Inline + summary + tasks | The remote PR itself (no local copy of the rendered comments) |
| Full Markdown report | `.temp/reports/review-pr-<provider>-<number>.md` |
| Validator log | `.temp/notes/review-pr-<provider>-<number>-validator.md` |
| Drafts (pre-approval) | `.temp/drafts/review-pr-<provider>-<number>-drafts.md` |
| Reconciliation map | `.temp/notes/review-pr-<provider>-<number>-reconciliation.md` |
| Cloned PR repo (isolated checkout) | `.temp/reference-repos/<owner>__<repo>/pr-<n>/` (only when needed for read-only review) |

`<provider>` = `github` or `bitbucket`. `<number>` = PR number.

## .temp/ contract

All intermediate artifacts (drafts, reconciliation maps, raw notes, validator logs, cloned reference repos) MUST be written under `.temp/` in the host repo, using these subfolders:

| Path | Purpose |
| --- | --- |
| `.temp/plans/<slug>.md` | Implementation, refactor, or migration plans |
| `.temp/drafts/<slug>.md` | Prose drafts before posting |
| `.temp/reports/<slug>.md` | Reviews, audits, investigations |
| `.temp/notes/<slug>.md` | Short-lived working notes (validator log, reconciliation map) |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos for research / isolated checkouts |

`.temp/` is gitignored. Promote a file out of `.temp/` ONLY when it is the deliverable the user asked for, in the location they asked for it. For this skill, the only thing that gets promoted out of `.temp/` is the comments themselves (which post to the remote PR, not to `.temp/`).

## Promotion rule

For `adk-review-pr`, "promotion" = posting to the remote PR. The local Markdown mirror under `.temp/reports/` STAYS in `.temp/` — it is for the user's audit / replay, not a tracked deliverable.

If the user explicitly asks for a tracked review report (e.g., to commit into the repo's `docs/reviews/` folder), THEN copy the `.temp/reports/<slug>.md` to its destination. Until they ask, leave it in `.temp/`.

## Idempotency

- Re-running this skill on the same PR URL must NOT re-post already-posted comments. The reconciliation step + the per-finding stable IDs in `.temp/drafts/` are what enforce this.
- The validator's Phase 4 records provider-returned comment IDs in the validator log. A second run reads that log first to identify previously-posted findings.
