# comment-resolution — handling pre-existing PR comments

Every PR review begins by reading every existing review comment thread (`pr-comments.json`). The reviewer's job for each thread is to **classify and act**, then declare the action in `existing_comment_actions[]`.

## The four classifications

| Class | Definition | Action |
|---|---|---|
| **fixed** | The code at the thread's `path:line` now satisfies the comment's ask. Evidence: the relevant lines were changed in this push, or moved, or the surrounding behavior changed in a way that addresses the concern. | `decision: resolve` (only if the thread is currently OPEN) |
| **unfixed** | The code still has the issue the comment named. The diff did not address it. | `decision: reopen` (only if the thread is currently RESOLVED — i.e. the author / a prior reviewer marked it resolved without fixing) |
| **offline-aligned** | A reply in the thread indicates the discussion moved off-platform: "agreed offline", "discussed in standup", "we'll handle this in a follow-up PR", "out of scope per <person>", "talked about this and decided X". | `decision: leave-as-is` regardless of current state; record `offline_alignment_detected: true` |
| **ambiguous** | Insufficient evidence to classify. The comment may or may not be addressed; the discussion may or may not be aligned. | `decision: leave-as-is`; record reason as `"ambiguous — needs human"` |

## State transitions (the rule)

The skill applies these transitions on the host PR:

| Current host state | Class | Final host state |
|---|---|---|
| OPEN | fixed | RESOLVED (skill resolves) |
| OPEN | unfixed | OPEN (no-op; the new finding may re-raise — see anti-pattern below) |
| OPEN | offline-aligned | OPEN (leave-as-is) |
| OPEN | ambiguous | OPEN (leave-as-is) |
| RESOLVED | fixed | RESOLVED (leave-as-is) |
| RESOLVED | unfixed | OPEN (skill reopens) |
| RESOLVED | offline-aligned | RESOLVED (leave-as-is) — the offline alignment IS the justification for closing |
| RESOLVED | ambiguous | RESOLVED (leave-as-is) |

The user's intent: "if its marked resolved, leave it, if not marked resolved, leave is" applies specifically to **offline-aligned** threads — the alignment overrides the resolved/open bit. For fixed/unfixed threads, the skill makes the state match the reality of the code.

## Offline-alignment detection heuristics

Match the last non-author reply (or any reply) against these patterns (case-insensitive):

```
- /\b(agreed|aligned|sync'd|synced|discussed)\s+(offline|in (the )?meeting|in (the )?call|on slack|on discord)\b/
- /\b(offline|out of band)\s+(agreement|alignment|conversation)\b/
- /\b(we'?ll|will)\s+(handle|address|fix)\s+(this|it)\s+(in|via|with)\s+(a\s+)?(follow-up|follow up|separate)\s+PR\b/
- /\bout of scope\b/
- /\bskip(ping)?\s+for now\b/
- /\bdeferred\b/
- /\b(per|spoke (to|with))\s+@?<known reviewer or human>\b/
- /\b(thanks|sounds good)[,!]?\s+(closing|resolving)\b/
```

Negative matchers (block offline-alignment if these appear in the SAME reply):

```
- /\b(but|however|except|unless)\b/  — qualifier; the alignment isn't clean
- /\?\s*$/                            — the reply ends in a question; nothing was decided
```

Apply the heuristic conservatively: a single matching pattern in a non-author reply, no negative matcher in the same reply, marks the thread `offline_alignment_detected: true`. Multiple matches strengthen confidence but don't change the action.

## Verifying a "fixed" classification

To claim **fixed** for a thread, the reviewer must have evidence at least one of:

1. The exact lines the comment was anchored to were modified by this PR's diff (`git blame -L <range> <head>` shows the most recent commit is in this PR).
2. The function / class containing the anchored lines was renamed or moved; the new location addresses the concern (cite the new `path:line`).
3. The behavior the comment named is now produced by surrounding code — supply a `evidence_ref` to the file:line that establishes this.

If none of (1)–(3) hold, the classification is **ambiguous**, not fixed.

## Verifying an "unfixed" classification

To claim **unfixed** for a thread currently marked RESOLVED:

1. The exact lines the comment was anchored to are unchanged AND there is no offline-alignment in the thread's replies.
2. OR the change made (per diff) does not address the comment's specific ask (cite the diff + quote the ask in ≤ 15 words).

Reopening a thread that was resolved with an offline-alignment marker is forbidden — it would re-litigate a closed decision.

## Anti-pattern: re-raising in the new findings

If a thread is `unfixed`, the new findings array **may** include a finding at the same `path:line` only if:

- The finding's body says explicitly: "Re-raising prior comment thread `<id>` because the diff did not address it."
- The finding's confidence is `high` (you read the code and verified).
- The finding's severity is `blocker` or `critical` (re-raising shouldn't happen for nits — those auto-resolve in human review).

Otherwise: a `decision: reopen` action on the existing thread is sufficient, with no duplicate finding in `findings[]`.

## Posting mechanics

- **GitHub**: `resolveReviewThread` / `unresolveReviewThread` via GraphQL (the REST API doesn't support it). The script falls back to a status comment ("Resolving this thread: the diff at `path:line` addresses the concern.") if the token can't access GraphQL.
- **Bitbucket Cloud**: `resolveComment` / `reopenComment` via the MCP. Both supported on the standard token.

All resolve / reopen actions are reported in `report.md` with the comment ID and the reason.

## Edge cases

- **Outdated thread (anchor lines no longer exist)**: classify as `ambiguous`, leave-as-is. GitHub's UI shows these as "Outdated" already.
- **Thread on a file deleted in this PR**: classify as `fixed` only if the deletion was the intended fix (cite the diff's `--- a/path` line). Otherwise `ambiguous`.
- **Thread by the author themselves (self-comment / TODO)**: classify normally; the author can still mean "this is unaddressed".
- **Bot comments (CI, CodeRabbit, Greptile, etc.)**: skip — `decision: leave-as-is` with `reason: "bot comment, skipped"`. Bot threads aren't human discussion; the skill doesn't decide for them.
