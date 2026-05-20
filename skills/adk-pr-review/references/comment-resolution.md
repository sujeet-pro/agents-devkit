# comment-resolution — handling pre-existing PR comments

Every PR review begins by reading every existing review comment thread (`pr-comments.json`). The reviewer's job for each thread is to **classify and act**, then declare the action in `existing_comment_actions[]`.

**MANDATORY: every thread MUST appear in `existing_comment_actions[]`.** A thread without a decision is treated as a verifier issue. If you're genuinely unsure, emit `decision: "leave-as-is"` with `reason: "ambiguous — needs human"`. Threads the AI doesn't address are auto-classified by `comment_resolver.py` (using the same rules) and flagged with `auto_classified: true` so the report can show them — but if you found a thread worth fixing, propose it explicitly.

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

## Acceptable-reply detection (broader than offline-alignment)

A thread with an *acceptable reply* is left alone regardless of its current state — the reply IS the disposition. Three flavors of acceptable reply:

### 1. Offline-alignment

The discussion moved off-platform: "agreed offline", "discussed in standup", "we'll handle this in a follow-up PR", "out of scope per <person>", "talked about this and decided X". See patterns below.

### 2. Jira (or similar) ticket reference

The concern was tracked in another ticket: "tracked in PROJ-1234", "moved to INFRA-42", "filed JIRA-5678 for next sprint", "follow-up in BACK-99". Pattern: a key matching `[A-Z][A-Z0-9]{1,9}-\d+` adjacent to a tracking verb (tracked, filed, logged, opened, created, moved, migrated, follow-up).

When this matches, the thread is left in whatever state it's in, and the Jira key is recorded in `comment-actions.json[].valid_reply.detail` so the report shows the tracking handoff.

### 3. "Synced with @person"

The reviewer / author named a human they aligned with: "synced with @alice", "spoke to @bob", "per chat with @carol", "as per @dave". Same effect — leave alone, record the handle.

In all three cases the verifier sets `valid_reply: {kind, detail}` on the action; the report renders this so a human can trace why a thread was left alone.

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

The post step is **MCP-first**. `post_comments.py` always writes `posting-plan.json` listing each step with its `mcp_tool` + `mcp_args`. Under `--use-mcp` (the recommended path when the host agent has MCP access), the script emits the plan and exits; the agent dispatches each call via the named tool. Direct-API stays only as the headless fallback for CI / rehearsal runs.

Per-platform tool table: see `references/platform-mcp.md`. Highlights:

- **GitHub**: review summary + inline comments + APPROVE event ship in one MCP call (`pull_request_review_write`). Resolve / reopen go through a textual reply via `add_reply_to_pull_request_comment` because REST + most token scopes cannot flip the resolved state directly; the team can flip the actual state from the UI afterward (or via GraphQL).
- **Bitbucket Cloud**: each comment is its own POST (or pending-comment + final publish). Resolve / reopen are first-class — `resolveComment` / `reopenComment`. Approve is its own endpoint — `approvePullRequest`.

**No merge step, ever.** `posting-plan.json.never_merge` is always `true`. Reviewing approves; humans merge.

All resolve / reopen / approve actions are reported in `report.md` with the comment ID, the reason, and (when applicable) the `valid_reply.kind/detail` that justified the disposition.

## Edge cases

- **Outdated thread (anchor lines no longer exist)**: classify as `ambiguous`, leave-as-is. GitHub's UI shows these as "Outdated" already.
- **Thread on a file deleted in this PR**: classify as `fixed` only if the deletion was the intended fix (cite the diff's `--- a/path` line). Otherwise `ambiguous`.
- **Thread by the author themselves (self-comment / TODO)**: classify normally; the author can still mean "this is unaddressed".
- **Bot comments (CI, CodeRabbit, Greptile, etc.)**: skip — `decision: leave-as-is` with `reason: "bot comment, skipped"`. Bot threads aren't human discussion; the skill doesn't decide for them.
