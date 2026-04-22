# Anti-patterns for `adk-docs-review`

## Review-shape anti-patterns

- Findings without doc location anchors. Every finding cites both a doc anchor AND a source-of-truth anchor.
- Calling out "improve clarity" without a concrete suggested replacement.
- Marking nitpicks as Critical because they are visible.
- Reviewing the doc against memory instead of the source code.
- Verdict of "looks good" with zero validation runs against the source.
- Severity inflation (every finding is `Blocker`); the page owner stops trusting the verdict.
- Severity deflation (a real outdated command filed as `Suggestion`); the page goes out with a known-broken Quick Start.
- Inferring source-of-truth without saying so; treating an inference as Verified evidence.

## Reconciliation anti-patterns (Confluence mode)

- Skipping `doc-comment-reconciliation.md` and producing a "fresh" review that re-files what's already raised.
- Closing an existing thread because the page owner replied "fixed" without re-validating against the current source.
- Closing an existing thread because the section moved, without restating the concern at the new section.
- Posting a "new" finding that duplicates an existing thread.
- Pushback replies without concrete source citations; "I don't agree" is not a pushback.

## Posting anti-patterns (Confluence mode)

- Posting before the user approves (unless `--auto`).
- Stapling multiple findings into one inline comment.
- Inline anchors that match multiple places on the page; the comment lands in the wrong spot.
- Inline anchors that don't exist verbatim on the current page (smart quotes, whitespace, deleted text); the comment fails to post or orphans.
- Editing page content. This skill ONLY comments. Edits are `quince-confluence-doc` or `adk-docs-write` + `adk-publish-confluence`.
- Posting a "ready-to-publish" verdict on a page with open Blockers.

## Validator anti-patterns

- Skipping any of the four validator phases in `doc-review-validator.md`.
- Treating WARN as OK silently; WARNs must surface in the report.
- Claiming `validated` without writing the validator log to `.temp/notes/`.
- Inferred source-of-truth without surfacing the inference to the user.

## Workflow anti-patterns

- Acting outside this skill's scope; route to:
  - `adk-docs-write` for rewrites or new docs.
  - `adk-review-pr` for code review (with or without doc changes).
  - `adk-publish-confluence` for publishing a Markdown doc to Confluence.
  - `adk-audit-repo` for whole-repo audits that include docs as one dimension.
- Mode confusion: trying to post comments on a local Markdown file (`--mode local` is read-only).
- Routing to two skills at once instead of chaining.
