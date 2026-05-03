# `review-pr` — existing-comment reconciliation

How to walk and classify every existing comment / reply / resolved task on the PR before drafting new findings. The output (`reconciliation.md`) is the input to the dedupe step in Phase 4.

## Why this exists

Re-running review-pr on an evolving PR is common. The skill must:

1. Recognize comments the author already addressed → don't re-raise.
2. Recognize comments the author pushed back on → don't re-raise unless we have new evidence.
3. Recognize "resolved" threads where the underlying issue is still in code → flag.
4. Avoid drafting a new finding that duplicates an existing comment.

The reconciliation phase produces a per-existing-item classification table and uses it to dedupe the new-findings list.

## Sources walked

In Phase 2, the skill fetches:

| Source | Endpoint / command | What it contains |
| --- | --- | --- |
| Inline comments | `GET /repos/<repo>/pulls/<num>/comments` | Comments anchored to a file:line in the diff |
| Issue comments (top-level) | `GET /repos/<repo>/issues/<num>/comments` | Top-level conversation, not anchored to a line |
| Reviews | `GET /repos/<repo>/pulls/<num>/reviews` | Review summaries (Approved / Changes-Requested / Commented) and their bodies |
| Review threads (resolved state) | GraphQL `pullRequest.reviewThreads` | Thread objects with `isResolved` (REST doesn't expose this cleanly) |
| Suggestions | (subset of inline comments with `suggestion` blocks) | Reviewer-proposed code that the author may have accepted via the GitHub UI |

## Classification states

For each existing item, classify into exactly one state:

| State | Definition |
| --- | --- |
| `still-open` | Comment is still relevant against the current diff; author has NOT addressed it; no resolved-thread marker. |
| `resolved-confirmed` | Thread is marked resolved AND the underlying issue is no longer present in the current code. |
| `resolved-stale` | Thread is marked resolved BUT the underlying issue is still present in the current code (e.g. resolved by mistake; or partially addressed but the core issue remains). |
| `pushback` | Author replied disagreeing with the comment (or reviewer disagreed with author). The thread is unresolved by design. |
| `clarify` | Author asked a clarifying question that hasn't been answered. |
| `outdated` | Comment is on a line/file that no longer exists in the current diff (e.g. the diff was rebased and the line moved or was removed). |
| `meta` | Comment is procedural (e.g. "rebase on main please") and not a code finding. |

## Classification algorithm

For each existing inline comment:

```
1. Locate the target line in the current head SHA.
   - If file is gone: classify `outdated`. Skip.
   - If line is gone (diff shifted): try fuzzy re-anchor (search ±20 lines for the comment's contextual snippet).
     - If re-anchored: continue.
     - If not: classify `outdated`. Skip.

2. Read the current code at the target line.

3. Read the comment body. Extract the issue (heuristic: first sentence + any code suggestion).

4. Walk the thread:
   - If thread is `isResolved`:
     - If issue NO longer matches current code  -> `resolved-confirmed`.
     - If issue STILL matches current code      -> `resolved-stale`.
   - Else (thread is open):
     - If author replied disagreeing            -> `pushback`.
     - If author asked a question (no answer)   -> `clarify`.
     - If issue STILL matches current code      -> `still-open`.
     - If issue NO longer matches current code  -> classify `still-open` BUT note "appears addressed in code; thread should be resolved".

5. Record the classification in reconciliation.md with the comment URL, classification, and one-line reason.
```

For top-level (issue) comments and review summaries:

```
1. Read the body.
2. Classify:
   - "rebase on main", "fix CI", "add a screenshot"             -> `meta`.
   - Approval / change-request review with a body                -> `meta` (the inline comments are the actionable part).
   - General comment with a content-bearing finding              -> `still-open` (or `pushback` / `clarify` per the same rules).
3. Record.
```

## Dedupe rules

After classification, dedupe the new-findings list (Phase 3 output) against existing items:

| New finding state | Existing item state | Action |
| --- | --- | --- |
| New finding matches a `still-open` comment (same file:line range, same issue category) | `still-open` | DROP the new finding. The existing comment is enough. |
| New finding matches a `pushback` comment | `pushback` | DROP the new finding UNLESS we have a new piece of evidence (a different code path the existing comment didn't cite, or a runtime artifact like a test failure). If kept, the new finding's body explicitly engages the prior pushback. |
| New finding matches a `resolved-confirmed` comment | `resolved-confirmed` | DROP the new finding (the issue is no longer present). |
| New finding matches a `resolved-stale` comment | `resolved-stale` | KEEP the new finding; in the comment body, reference the prior comment URL. |
| New finding matches a `clarify` comment (the new finding answers the question) | `clarify` | Convert the new finding to a `Question` reply (Phase 6b) instead of a fresh inline comment. |
| New finding matches an `outdated` comment | `outdated` | KEEP the new finding (existing was on a line that no longer exists). |

## Match heuristic (when is a new finding a "match"?)

```
Match := same(file) AND
        line_range_overlap(existing.line_range, new.line_range) AND
        same_dimension(existing, new) AND
        category_match(existing.issue, new.issue)

where:
  category_match :=
    extract a category-noun from each (e.g. "auth bypass", "n+1 query", "missing test", "secret in diff")
    case-insensitive equality on the category-nouns

  line_range_overlap := the existing comment's anchor falls within ±5 lines of the new finding's anchor
                       (loose because the diff may have shifted)
```

Conservative: if the heuristic says "probably match but unclear", surface as a `requires-human-judgment` row in `reconciliation.md` and (under `-i`) ask the user.

## reconciliation.md shape

See `references/output-format.md` for the canonical shape. Summary:

```markdown
# Existing-comment reconciliation

## Summary
- Total walked: <N>
- still-open: <n>
- resolved-confirmed: <n>
- resolved-stale: <n>
- pushback: <n>
- clarify: <n>
- outdated: <n>
- meta: <n>

## Per-item table
| URL | Author | Created | State | Reason | Treatment |
| --- | --- | --- | --- | --- | --- |
| ... |

## Dedupe outcome
- Dropped <n> new findings (duplicates of still-open / pushback)
- Promoted <n> new findings to inline (no overlap)
- Converted <n> new findings to Question replies (existing was clarify)
```

## Anti-patterns

- **Skipping reconciliation.** You'll re-raise findings the author addressed (annoying) or pushed back on (worse).
- **Marking everything `still-open` without checking the code.** If the issue isn't actually present anymore, the comment is `resolved-confirmed` (or should be).
- **Treating `isResolved=true` as authoritative.** Resolved-stale exists because the resolve button is one click away from anyone with write access; don't assume the underlying code changed.
- **Re-raising a `pushback` finding without engaging.** Read the reply. If your draft would be the same again, drop it; the conversation has happened.
- **Treating top-level review bodies as findings.** Approval / change-request bodies are usually framing; the actionable content is in the inline comments.
- **Forgetting to record `outdated` items.** They belong in the reconciliation table even if the action is "skip" — the audit trail matters.
