# `review-pr` — worked examples

## Example 1 — peer's PR, default `--auto`, 1 Blocker + 3 Nitpicks

**Prompt:** `/adk-review:review-pr https://github.com/acme/checkout-api/pull/2841`

**Phase 0:**
- Slug: `checkout-api-pr-2841`.
- PR: `acme/checkout-api#2841`. Head SHA: `a1b2c3d`.
- Author: `@alice`. Local identity: `sujeet@onequince.com`. **Ownership: `peer`.**
- Mode: `--auto` (default).

**Phase 1:** preflight green. `gh` authed. `repos.md` has the local checkout. `~/.config/adk/review.md` says `severity_bar.blocker += [n_plus_one_in_loop]` for this org.

**Phase 2:** fetched PR metadata, diff (47 files, +1240/-180), 12 existing comments (8 still-open, 3 resolved-confirmed, 1 pushback). Author's last 5 PRs: similar style. CODEOWNERS: payments team.

**Phase 3:** parallel dimension passes:
- `correctness`: 0 findings.
- `security`: 1 Blocker (`auth_bypass`: new admin endpoint missing role check at `routes/admin.go:42`).
- `performance`: 1 Critical (n+1 query at `db/orders.go:117`, in a loop over 1000+ rows).
- `tests`: 2 Should-Have (no test for the new admin endpoint; no test for the n+1 path).
- `docs`: 1 Nitpick (CHANGELOG.md not updated).
- `style`: 0 findings (lint silent).

**Phase 4 — reconcile:**
- 8 still-open: 5 are about pre-existing concerns we'd raise too — drop our duplicates; defer to author's existing thread. 3 are about minor style the author defers to lint.
- 1 pushback: author disagrees with `@bob`'s suggestion to extract a helper. Our own scan didn't suggest extraction; no conflict.
- 3 resolved-confirmed: verified addressed in the diff.
- Final new findings: 1 Blocker, 1 Critical, 2 Should-Have, 1 Nitpick.

**Phase 5 — propose:** sorted; under `--auto`, all kept.

**Phase 6a — post:**
- Re-validated line anchors (head SHA still `a1b2c3d`, no shift).
- Flipped `GITHUB_READ_ONLY=0`. Posted as one consolidated `gh pr review --comment -F` with 5 inline annotations.
- Captured 5 receipt IDs.
- Wait 5s → re-fetch → 5/5 confirmed.
- Restored `GITHUB_READ_ONLY=1`.

**Phase 7 — report:**
- `findings.md` with 5 findings.
- `postback.md` with 5/5 receipts confirmed (URLs included).
- `reconciliation.md` with 12 existing comments classified.
- Final: "Posted 5 findings (1 Blocker, 1 Critical, 2 Should-Have, 1 Nitpick) to PR #2841. No merges, no force-pushes."

---

## Example 2 — your own PR, `--auto`, drafts replies + posts

**Prompt:** `/adk-review:review-pr https://github.com/acme/storefront/pull/99`

**Phase 0:**
- Slug: `storefront-pr-99`.
- Author: `sujeet-pro` (== `git config user.email` resolves to same user). **Ownership: `own`.**
- Mode: `--auto` (default).

**Phase 1:** preflight green. Note: own PR with `--auto` (no `--fix`) → drafts replies + does the self-review pass.

**Phase 3:** review pass: 1 Should-Have (missing test for new boundary) + 2 Nitpicks.

**Phase 4 — reconcile** with 6 existing reviewer comments:
- `still-open` (4): 2 valid + addressed in our latest commit but not yet replied to. 1 valid, not addressed yet. 1 misunderstanding (we read the code, the reviewer is wrong).
- `pushback` (1): we initially pushed back; on re-read, reviewer is right.
- `clarify` (1): reviewer asked a question.

**Phase 5 — propose:** 3 self-findings + 6 reply drafts. Under `--auto`, kept.

**Phase 6b — validate + reply:**
- Drafted replies per `pr-reply-templates.md`:
  - 2 `fix-applied` (with the commit SHA where the fix landed).
  - 1 `fix-acknowledged` (we'll fix in the next push).
  - 1 `pushback` (with reasoning + request to discuss in person).
  - 1 `fix-applied` (we changed our mind on the original pushback).
  - 1 `clarification` (answered the question).
- Posted as 6 individual replies (one per thread). 6 receipts. Re-fetch confirmed 6/6.

**Phase 7 — report:** "Self-review found 3 follow-ups; replied to 6 reviewer comments; addressed 4, pushed back on 1 (politely, with offer to discuss), clarified 1."

---

## Example 3 — `--auto --fix` on a peer's PR, fixes applied + push

**Prompt:** `/adk-review:review-pr acme/checkout-api#2841 --fix`

**Phase 0–5:** same as Example 1. 5 findings.

**Phase 6c — fix:**
- Build the fix queue. The Blocker (auth bypass) and the Critical (n+1) are non-trivial → delegate each to `/adk-code:code-bugfix`. The 2 Should-Have (missing tests) and the 1 Nitpick (CHANGELOG) are trivial → inline edits.
- Validate after each: `go test ./...` (from `repos[acme/checkout-api].notes`), `golangci-lint run`, `go vet ./...`. All green after each fix.
- Commits: 5 separate commits (one per finding) + 1 CHANGELOG commit, all on branch `pr-2841-review-fixes-from-sujeet`.
- **PUSH-GATE:** asked: "Push 6 commits to `acme/checkout-api/pr-2841-review-fixes-from-sujeet`? [y/N]". User said `y`.
- Pushed.
- Replied to each addressed comment with `fix-applied` template, quoting the commit SHA.
- Resolved each comment (after reply post-confirmation).

**Phase 7 — report:**
- `fix-log.md` with 6 commits + per-fix validation evidence.
- "5 findings posted, 5 fixes pushed (1 Blocker + 1 Critical + 2 Should-Have + 1 Nitpick), 0 merges (per policy), no force-pushes. Author can squash + merge."

---

## Example 4 — `-i` interactive on a controversial PR, walks each finding

**Prompt:** `/adk-review:review-pr acme/storefront#103 -i`

**Phase 0:** `-i` mode. Ownership: `peer`.

**Phase 3:** dimension passes produce 11 findings.

**Phase 4:** reconcile against 18 existing comments. Drops 4 duplicates → 7 remaining new findings.

**Phase 5 — propose (interactive):**

```
[adk-review:review-pr] task=storefront-pr-103 pr=acme/storefront#103 ownership=peer phase=5 mode=interactive findings=B0/C2/S3/M1/N1/Q0

7 new findings to walk. Showing 1 of 7.

### [Critical] Possible XSS in product name render
- File: components/ProductCard.tsx:48
- Dimension: security
- Confidence: high
- Evidence:
  ```
  <div dangerouslySetInnerHTML={{__html: product.name}} />
  ```
- Issue: product.name comes from user input via API; not sanitized.
- Fix: render as plain text (`{product.name}`) or sanitize via DOMPurify.
- Impact if unfixed: stored XSS via merchant-uploaded product names.

[a]ccept | [e]dit | [d]iscard | [discuss] in person | [s]kip
> a
```

User accepts 5, edits 1 (re-tier from `Should-Have` to `May-Have` because the path is internal-tools-only), discards 1 (false positive on closer read).

**Phase 6a — post:** posts 6 (5 + 1 edited). Post-confirmation 6/6. Restored read-only.

**Phase 7 — report:** "Walked 7, posted 6 (1 Critical, 2 Should-Have, 2 May-Have, 1 Nitpick), discarded 1, re-tiered 1."

---

## Example 5 — propagation lag, post-confirmation retry succeeds at 10s

**Phase 6a:** posted 4 comments, captured 4 receipt IDs.

**Wait 5s → re-fetch:** 3 of 4 IDs found. 1 missing (`comment_id=7891234`).

**Wait 10s → re-fetch:** 4 of 4 IDs found (confirmed).

**`postback.md`:** "4/4 confirmed. 1 required 10s retry — likely propagation lag, not loss. NOT re-posted."

User's perspective: no duplicate, no missing, no manual intervention required.

---

## Example 6 — propagation lag, post-confirmation final miss at 20s

**Phase 6a:** posted 5 comments.

**Wait 5s, 10s, 20s** → only 4 of 5 IDs found.

**`postback.md`:** "5 attempted, 4/5 confirmed. ID `comment_id=7891999` UNCONFIRMED after 20s. NOT re-posted (would create duplicate). Surfacing to user: please refresh PR #2841 and confirm the 5th comment is present; if not, re-run with `--retry-unconfirmed`."

The skill stops here. The user verifies in the GitHub UI (the comment is in fact present — DB replication caught up at ~22s) and OK's.
