# Doc Review Postback Protocol

How and when to post draft findings back to the live Confluence page (only relevant under `--mode confluence`). The default is dry-run; posting requires explicit approval (or `--auto`).

In `--mode local`, this file does not apply — the report is the only artifact.

## Modes

| Mode | What posts | When to use |
| --- | --- | --- |
| `dry-run` (default) | Nothing is posted; the report is shown to the user | First-pass review; user wants to inspect findings before they hit the page |
| `post` | All approved findings (inline) + footer summary comment | After the user accepts findings, or after `--auto` validates them |
| `--auto` | All validated, non-duplicate findings + footer summary, with no approval gate | Trusted batch reruns; CI-style usage |

## Pre-post gate

Before posting ANY comment to the page, ALL of these must pass (per `doc-review-validator.md`):

- Confluence MCP authenticated; page URL parses; page fetched.
- Source-of-truth read in current state (not from cache or memory).
- Reconciliation pass per `doc-comment-reconciliation.md` complete; duplicates removed.
- Every finding to be posted has evidence (doc anchor + source anchor + quoted snippet).
- Every finding to be posted is rendered with the `doc-review-comment-format.md` template.
- The auth identity has comment-write permission on the space.

If any check fails: STOP, surface what's missing, ask the user (or, under `--auto`, fix the gap and re-run the gate).

## Posting order

Post in this order so the page reads left-to-right correctly:

1. Inline comments — one per finding, anchored to a precise text snippet from the page.
2. Reconciliation replies — on existing threads, in thread-creation order.
3. Footer summary comment — posted last so it reflects the actual state after step 1-2.

## One finding = one inline comment

Never staple multiple findings into one inline comment. If two findings share a section, consolidate them per `doc-review-comment-format.md` consolidation rules into a single F-ID and post one inline comment that lists both sub-issues.

## Inline anchor selection

For each finding:

1. Pick the most specific text snippet that uniquely anchors the comment to the right spot.
2. The snippet must exist verbatim in the current page (re-fetch and verify before posting).
3. If the snippet appears multiple times on the page, narrow it to a longer snippet that includes nearby context.
4. Never anchor on a single common word; the comment will land in the wrong place.

If no stable text anchor exists (e.g., a table cell that may be edited), use a footer comment instead and reference the section by heading.

## Footer summary comment

The footer comment is the verdict + counts + Blockers/Critical lists. It MUST follow the shape from `doc-review-comment-format.md` `## Doc review summary` section.

Rules:

- Lists Blockers + Critical only by name; everything else as counts.
- Always closes with the validation block (doc fetched, source read, reconciliation done, posted counts).
- Never repeats inline-comment text.
- Posted as a regular page comment (NOT an inline comment) — it is the page-level verdict.

## Verdict rules

The summary's `Verdict` line:

| Verdict | When | Page action |
| --- | --- | --- |
| `needs-rewrite` | Multiple Blockers or fundamental structure problems; small fixes will not save it | Comment posted; the page owner is expected to invoke `adk-docs-write` for a rewrite |
| `needs-fixes` | At least one Blocker, OR multiple Criticals; targeted edits will fix the page | Comment posted; the page owner is expected to address the Blockers / Criticals |
| `ready-to-publish` | No Blockers, at most a few Should Have / Nitpick / Question | Comment posted; the page is approved for publish / external read |

NEVER edit the page content. This skill only comments. Page edits go through `quince-confluence-doc` or `adk-docs-write` + `adk-publish-confluence`.

## Re-posting safety

If the post step fails partway through (network, rate limit, permission), record what was successfully posted in the report, then offer:

- `retry-remaining` — re-post only the items that failed.
- `dry-run` — switch back to dry-run mode and show what's left.
- NEVER duplicate a successfully-posted comment.

Track posted comments by their Confluence-returned IDs in the in-session state so retries are idempotent.

## After posting

The report MUST end with:

```
## Postback summary
- Inline comments posted: <n> (IDs: <list or omitted>)
- Reconciliation replies posted: <n>
- Footer summary comment posted: <YES | N/A>
- Verdict posted: <ready-to-publish | needs-fixes | needs-rewrite>
- Failed to post (with reason): <list or none>
```

## Confluence-specific gotchas

- Confluence comments do NOT support nested admonitions / panels / status macros — keep Markdown to bold + headers + lists + fenced code + inline code.
- Inline comments require a stable text anchor; if the anchor text is edited after posting, the comment becomes "orphaned" and harder to find.
- The page owner can resolve inline comments without the reviewer's input. The reconciliation pass on the next run will catch resolved-stale cases.
- Atlassian MCP has a separate path for inline vs page-level comments — use the right tool.
