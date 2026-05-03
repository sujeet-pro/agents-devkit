# `review-pr` — reply templates

Used in Phase 6b (own-PR path: replying to existing reviewer comments) and Phase 6c (after applying a fix from `--fix`: replying with the commit SHA).

## Five canonical templates

| Template | Use when |
| --- | --- |
| `fix-acknowledged` | The reviewer's point is valid; we'll fix it (in this PR or as a follow-up). No code change yet. |
| `fix-applied` | We've applied the fix. Quote the commit SHA + a one-line summary. |
| `pushback` | We disagree with the reviewer's point. State the reasoning concretely; offer to discuss. |
| `partial` | We've partially addressed the comment (e.g. fixed the underlying bug but not the suggested refactor). |
| `clarification` | The reviewer asked a question; we answer it (with file/line citations). |

## fix-acknowledged

```
Good point. Will address in <this PR | a follow-up — tracking at <link>>.

<optional: 1 sentence on the planned approach if it differs from what the reviewer suggested>

— /adk-review:review-pr (own-PR path)
```

### Example

```
Good point. Will address in this PR — adding the null-check + a regression test before next push.

— /adk-review:review-pr (own-PR path)
```

## fix-applied

```
Done in <commit-sha>. <one-line summary of what changed>

<optional: 1 sentence on a tradeoff if relevant — e.g. "kept the existing `processOrder` name to avoid touching 12 callers; happy to rename in a separate PR">

— /adk-review:review-pr (own-PR path)
```

### Example

```
Done in a1b2c3d. Added `RequireRole("admin")` to the route group; matches the pattern at routes/admin.go:18-31.

— /adk-review:review-pr (own-PR path)
```

### With code reference

```
Done in b2c3d4e. Switched from `db.Find` in a loop to `db.Preload("Items")` on the initial query.

`db/orders.go:117-129`

— /adk-review:review-pr (own-PR path)
```

## pushback

```
Considered this; respectfully pushing back.

Reasoning: <one or two sentences with concrete signal — name the constraint, the file/line, the trade-off, or the prior decision>.

<optional: 1 sentence offering a path forward — "happy to discuss in <Slack channel | DM | sync> if this still feels off">

— /adk-review:review-pr (own-PR path)
```

### Example

```
Considered this; respectfully pushing back.

Reasoning: extracting the helper would force every caller to wire in a context.Context (we're 14 callers deep). The current shape has tested isolation at `services/order_test.go:42-58`. Happy to revisit if we need the helper for the cart-side feature in Q3.

— /adk-review:review-pr (own-PR path)
```

### When to escalate to the in-person discussion

If the pushback would require >3 sentences to explain, or touches a fundamental architectural choice, the reply is:

```
Considered this; respectfully pushing back. The reasoning is non-trivial — would prefer to discuss in person rather than turn this thread into an essay.

Sketch: <one sentence on the gist>.

Suggesting we sync at the next platform standup, or DM me on Slack.

— /adk-review:review-pr (own-PR path)
```

## partial

```
Partially addressed in <commit-sha>: <what was fixed>.

Not addressed: <what wasn't, and why>.

<optional: link to the follow-up issue / ticket / PR>

— /adk-review:review-pr (own-PR path)
```

### Example

```
Partially addressed in c3d4e5f: fixed the underlying n+1 query as suggested.

Not addressed: the broader refactor to extract the query layer — that's a 200-line change touching 6 files; tracked separately at https://acme.atlassian.net/browse/CHK-1340.

— /adk-review:review-pr (own-PR path)
```

## clarification

```
<answer to the reviewer's question — concrete, with file/line citations>.

<optional: a follow-up code touch if the question reveals the code wasn't clear enough — e.g. add a comment, rename for clarity>

— /adk-review:review-pr (own-PR path)
```

### Example

```
Yes — the `orderMu.Lock()` at `services/order.go:102` covers this block. The lock is held for the duration of the `processOrder` call, so the read at line 117 is serialized w.r.t. concurrent updates.

Added a one-line comment at line 117 to make this obvious for future readers (commit d4e5f6g).

— /adk-review:review-pr (own-PR path)
```

## Hard rules for replies

1. **Always include the commit SHA** when the reply describes a code change. The SHA is the proof; without it, the reply is unverifiable.
2. **Always sign with the attribution line** — `— /adk-review:review-pr (own-PR path)`. Lets the reviewer (and future-self) know an automation drafted the reply, not a manual edit.
3. **Always cite file:line** when the reply references code. Don't say "the lock"; say "`services/order.go:102`".
4. **Never close a thread without a reply.** Reply first, then resolve.
5. **Never resolve a thread that contains a `pushback` reply.** Leave it open for the reviewer to either accept the pushback or counter.
6. **Match the repo's tone.** If the codebase has a casual / formal house style for review comments, match it. (`~/.config/adk/review.md.house_style` may carry an override.)
7. **No emojis.** Per the universal interaction contract.
8. **No "I" / "we" / "our" overload.** Direct voice. The reply is from the author (you), drafted by the skill — the attribution line carries the "drafted by" signal.
9. **Keep it short.** 2-5 sentences for `fix-applied` / `clarification`. 3-7 for `pushback` / `partial`. Anything longer should be a sync conversation, not a thread comment.
10. **Never silently change the meaning of the reviewer's comment when paraphrasing.** Quote ≤15 words verbatim if needed; otherwise, summarize neutrally.

## When to NOT reply (and just resolve)

| Existing comment state | Action |
| --- | --- |
| `meta` (e.g. "rebase on main please") | Resolve once the meta-action is done; no reply needed. |
| `resolved-confirmed` (already addressed) | No action — already resolved. |
| Tiny nit (e.g. "extra blank line") that we already fixed in the same diff | Optional reply; OK to just resolve with no body. |

## When NOT to draft a reply at all

| Comment | Reason |
| --- | --- |
| Comment is from a bot we configured (Dependabot, CodeRabbit, etc.) | Let the bot's own resolution mechanism handle it. |
| Comment is on a file owned by a different team per CODEOWNERS | Defer; the team owner replies. Surface in `report.md` as "deferred to <owner>". |
| Comment was posted >30 days ago and the PR has been re-opened | The reviewer's context has likely shifted; better to ping them in person. |
