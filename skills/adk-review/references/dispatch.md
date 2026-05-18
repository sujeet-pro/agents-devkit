# adk-review — target dispatch

> Used in Phase 0. Routes by target shape. Specialized sub-flows for the two most common: PR URL and local working tree.

| Target shape | Sub-flow | Reference |
|---|---|---|
| GitHub PR URL | review-pr | `review-pr.md` (specialized — most common) |
| `.` or local path (no URL) | review-code-changes | `review-code-changes.md` (specialized) |
| `<path>.md` or markdown URL or Confluence URL | review-doc | `review-doc.md` |
| GitHub comment-thread URL (`#issuecomment-…` / `#discussion_r…`) | review-comments | `review-comments.md` |
| Path + `--audit` flag | audit-repo | `audit-repo.md` |
| PR URL + `--audit` flag | audit-pr | `audit-pr.md` |

## Ambiguity

- Mixed input (PR URL + a path) → ask which to review. The two targets are different reviews.
- Folder of markdown files → ask: review-each-as-doc or audit-repo-of-docs?
- Comment URL where the underlying PR/issue is closed → review-comments still works (read-only).
