# `review-feedback` — worked examples

## Example 1 — `--auto --fix` on 6 reviewer comments, all addressed

**Prompt:** `/adk-review:review-feedback acme/checkout-api#2841 --fix`

**Phase 0:** PR `acme/checkout-api#2841`. Slug: `feedback-checkout-pr-2841`. Mode: `--auto --fix`. Local checkout: `~/code/acme/checkout-api`.

**Phase 1:** preflight green. `gh` chosen. Working tree clean. Push permission confirmed.

**Phase 2 — fetch:**
- 6 inline comments (all open, all on the same PR head).
- 1 review summary ("Looks good overall, a few inline comments").
- 0 issue comments.

**Phase 3 — classify** (per `references/classification.md`):
- Comment 1 (line 42, "missing role check") → **apply-as-stated**.
- Comment 2 (line 88, "consider extracting helper") → **apply-with-modification** (we agree; better fix is renaming, not extracting).
- Comment 3 (line 117, "n+1 query") → **apply-as-stated** (suggestion is correct).
- Comment 4 (line 12, "typo `recieve` → `receive`") → **apply-as-stated**.
- Comment 5 (line 200, "should this be tested?") → **apply-as-stated** (add test).
- Comment 6 (line 250, "this is the wrong abstraction") → **discuss-not-fix** (architectural; sync conversation).

Counts: A4 / M1 / D1 / W0 / R0.

Grouping: comments 1, 5 (related to admin endpoint security) → group into 1 fix; comments 2, 3 (both in `db/orders.go`) → 2 separate fixes (different lines, different intents); comment 4 → 1 trivial fix.

**Phase 4 — propose:** classifications kept under `--auto`.

**Phase 5a — draft:**
- Comments 1+5: `apply-stated` template (will be filled with same SHA).
- Comment 2: `apply-modified` template (rename instead of extract; reasoning).
- Comment 3: `apply-stated` template.
- Comment 4: `apply-stated` template.
- Comment 6: `discuss` template + link to a Jira ticket (or "let's sync; DM me").

**Phase 5b — apply:**
- Fix 1 (comments 1+5: admin role check + test): non-trivial → delegate to `/adk-code:code-bugfix`. Returns 2 commits: `abc1234` (the fix), `def5678` (the test). Validation: `go test ./routes/...` PASS.
- Fix 2 (comment 2: rename `processOrder`): trivial → inline. Commit: `ghi9012`. Validation: `go build ./...` PASS, `golangci-lint run` PASS.
- Fix 3 (comment 3: n+1 query): non-trivial → delegate. Commit: `jkl3456`. Validation: `go test ./db/...` PASS, benchmark improvement noted.
- Fix 4 (comment 4: typo): trivial → inline. Commit: `mno7890`. Validation: `go build` PASS.

**Phase 5c — push:**
- PUSH-GATE: "push 5 commits to acme/checkout-api/pr-2841-feedback-fixes? [y/N]". User: y.
- Pushed.

**Phase 5d — post replies:**
- 5 replies posted (one per addressed comment + one for the discuss thread).
- Receipts captured.
- Wait 5s → re-fetch → 5/5 confirmed.
- Resolve apply-* threads (1, 2, 3, 4, 5). Comment 6 (`discuss`) stays open.

**Phase 6 — report:**

```
Result: 5 commits pushed; 6 reviews comments addressed (4 apply-as-stated, 1 apply-with-modification, 1 discuss-not-fix). 5 threads resolved; 1 left open for discussion.

Classification: A4/M1/D1/W0/R0
Pushed: <branch> (5 commits, no force, no protected)
Posted: 6 replies, 6/6 confirmed (all at 5s)
Resolved: 5 of 6 (discuss-not-fix #6 stays open by design)
Residual: comment #6 needs sync; suggested DM @reviewer-name.
```

---

## Example 2 — `--auto --fix` with a `wont-fix`

**Same PR but comment #2 is "I think this whole abstraction is wrong, please extract a Repository pattern".**

**Phase 3 classify:**
- Comment 2 → **wont-fix** (we genuinely disagree; the "Repository pattern" is over-engineering for our scale; we have prior team discussion supporting this).

**Phase 5a — draft `wont-fix`:**

```
Considered this; respectfully pushing back.

Reasoning: introducing a Repository abstraction would force every caller to wire in a context.Context (we're 14 callers deep) and add an interface layer for one concrete type. The current shape has tested isolation at `db/orders_test.go:42-58`. We discussed this pattern in the platform sync on 2026-04-15 and decided to defer until we have a second backend (currently 1 SQL backend, no NoSQL on the roadmap).

Happy to revisit at next platform sync if this still feels off.

— /adk-review:review-feedback
```

The reply is posted; the thread is NOT resolved (let the reviewer accept or counter).

---

## Example 3 — interactive (`-i`) walks each classification

**Prompt:** `/adk-review:review-feedback acme/storefront#103 -i`

**Phase 4 — propose (interactive):**

```
6 comments classified. Walking each.

[1/6] Comment at components/ProductCard.tsx:48 by @bob:
> "use {product.name} instead of dangerouslySetInnerHTML — XSS risk"

Classification: apply-as-stated
Suggested fix: replace `<div dangerouslySetInnerHTML={{__html: product.name}} />` with `<div>{product.name}</div>`

[a]ccept | [r]e-classify | [s]kip
> a

[2/6] Comment at components/ProductCard.tsx:120 by @carol:
> "consider memoizing this component"

Classification: apply-with-modification
Reasoning: agree with the goal but the suggested `React.memo` won't help because the prop is a fresh object each render. Modification: useMemo on the inner data + still apply React.memo.

[a]ccept | [r]e-classify | [s]kip
> r

Re-classify to: discuss-not-fix
> r

Reason for discuss-not-fix?
> "memoization changes the ref-equality contract for downstream; want to think about it"

OK, classified as discuss-not-fix.

...
```

User walks each.

---

## Example 4 — `--auto` (no `--fix`): triage only, no apply

**Prompt:** `/adk-review:review-feedback acme/storefront#99 --auto`

(No `--fix`.)

**Phase 0–4:** classify 6 comments → A3/M1/D1/W1/R0.

**Phase 5a:** drafts 6 replies (with `<commit-sha>` placeholders for the apply-* ones).

**STOP.** No apply, no push, no post.

**Phase 6 — report:**

```
Result: classified 6 comments (A3/M1/D1/W1/R0); drafts in replies-draft.md. NOT applied; NOT pushed; NOT posted (--fix not set).

Next: re-run with --fix to apply, OR review the drafts at <path> and apply manually.
```

---

## Example 5 — `--auto --fix` with one fix's validation failing

**Phase 5b:**
- Fix 1: applied + validated PASS.
- Fix 2: applied + validated PASS.
- Fix 3: applied + validated FAIL (`go test ./db/...` fails: `TestOrderItemPreload — expected 100 items, got 0`).

**STOP.** Surface:

```
Validation failed after applying fix 3 (comment #3 at db/orders.go:117).

Command: go test ./db/...
Failure: TestOrderItemPreload — expected 100 items, got 0
Likely cause: the suggested `Preload("Items")` requires the Items relation to be defined on the Order struct; it isn't.

Options:
  [a]bort the queue (commits 1+2 stay; fix 3 reverted)
  [s]kip fix 3 and continue with fix 4+
  [d]elegate fix 3 to /adk-code:code-bugfix for a real solution
> d
```

The user picks delegate; `/adk-code:code-bugfix` is invoked with the failing test as the brief. Returns the proper fix (define the Items relation + Preload). Validation now PASS. Queue continues.

---

## Example 6 — comment-grouping (1 fix addresses 4 related comments)

**6 inline comments:**
- 4 of them flag the same root: "this endpoint is missing input validation" (across 4 different POST handlers in `routes/api.go`).
- 2 of them are unrelated.

**Phase 3 — classify:** all 4 grouped → 1 logical fix (add a shared validator and apply across the 4 handlers).

**Phase 5b — apply:** 1 commit (`xyz1234`) addresses all 4. Validation PASS.

**Phase 5d — post replies:** 4 separate replies, each quoting the same SHA but with a per-handler one-liner:

> Done in xyz1234. Added shared `validateProduct` validator and applied to `POST /products` (this handler at line 42).

> Done in xyz1234. Same shared `validateProduct` applied to `POST /products/bulk` (this handler at line 78).

> ...

All 4 threads resolve after the 4 replies post-confirm.

---

## Example 7 — already-resolved

**Comment posted 2 days ago:** "missing null check on `user.email`".

**Current code (after intervening commits):** the null check IS now present.

**Phase 3 — classify:** `already-resolved`.

**Phase 5a — draft `already-resolved`:**

```
Looks like this was addressed in commit <intervening-sha> (added the null check at user.go:42). Marking the thread to resolved.

— /adk-review:review-feedback
```

Reply posted. Thread NOT auto-resolved (because the resolution is the reviewer's confirmation; we don't want to silently resolve someone else's thread). The reply text says "marking to resolved" as a signal — the user can click resolve, or let the reviewer.
