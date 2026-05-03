# `review-feedback` — workflow detail

Detailed phase-by-phase stage list. Logs to `.temp/task-<slug>/validation/per-skill/review-feedback.md`.

## Phase 0 — prompt expand

1. **Resolve PR.** Accept URL, `<owner>/<repo>#<num>`, or bare `#<num>` (resolves against current repo). If no arg, use the current branch's open PR (`gh pr view --json number --jq .number`).
2. **Locate local checkout** via `~/.config/adk/repos.md`. If not found, `gh repo clone` into `.temp/task-<slug>/feedback-checkout/`.
3. **For `--fix`:** prefer the user's main checkout (the user typically wants the changes in their main worktree to commit + push from). Surface a "using main checkout" line in the banner. If the main checkout is dirty or on a different branch, ask once.
4. **Slug.** Derive from PR title (e.g. `feedback-checkout-pr-2841`). Prefix with `feedback-` to disambiguate from a `review-pr` run on the same PR.
5. **Create `.temp/task-<slug>/`** + write `prompt.txt`.
6. **Determine mode.** `--auto` (default), `-i`, `--fix`, or compositions.

## Phase 1 — preflight

1. **MCP / CLI selection.** Same logic as `review-pr`: prefer `gh` if both available.
2. **Auth scope check.** `gh api /user`; for `--fix` also `gh api /repos/<repo>` to confirm `permissions.push: true`.
3. **Local repo state.** Working tree clean for `--fix`; warned otherwise.
4. **Branch protection.** `gh api /repos/<repo>/branches/<base>/protection`. Refuse `--fix` if head branch is protected.
5. **Meta-info.** `bin/adk-info github --check` AND `bin/adk-info repos --check` must return 0.

## Phase 2 — fetch all reviewer comments

Parallel fetch into `.temp/task-<slug>/feedback/pr-context/`:

| Call | Output | Tool |
| --- | --- | --- |
| PR metadata | `pr.json` | `gh pr view <num> --json title,headRefOid,baseRefName,...` |
| Inline comments + replies | `comments.json` | `gh api /repos/<repo>/pulls/<num>/comments --paginate` |
| Issue (top-level) comments | `issue-comments.json` | `gh api /repos/<repo>/issues/<num>/comments --paginate` |
| Reviews | `reviews.json` | `gh api /repos/<repo>/pulls/<num>/reviews --paginate` |
| Review threads + resolved state | `threads.json` | `gh api graphql ...` |

Apply `--scope <comment-id-list>` filter if provided.

Assemble the per-comment list:

```python
comments = []
for c in inline_comments:
    if c.id in scope or scope is empty:
        comments.append(Comment(id=c.id, body=c.body, file=c.path, line=c.line, ...))

# Plus thread replies; plus issue-comments classified as findings.
```

## Phase 3 — classify each comment

For each open comment / unresolved thread, classify per `references/classification.md`:

| Classification | Definition |
| --- | --- |
| `apply-as-stated` | Clear actionable; the suggested fix is correct; we apply exactly as the reviewer suggested. |
| `apply-with-modification` | Clear actionable; we agree the issue exists but the suggested fix isn't quite right; we apply a better variant. |
| `discuss-not-fix` | The comment raises an architectural / design concern that needs a sync conversation, not a code edit. |
| `wont-fix` | We disagree with the reviewer's reasoning. Reply with concrete reasoning. |
| `already-resolved` | The underlying issue is no longer present (e.g. fixed by an intervening commit). |

The classification algorithm:

```
1. Read the comment body (extract the issue + the suggested fix).
2. Read the current code at the target line (post-diff state).
3. If the issue is no longer present in the code -> already-resolved.
4. Else: read the suggested fix (extract via heuristic or `suggestion` block).
   - Does the suggestion compile / typecheck conceptually? Does it solve the issue?
     - Yes -> apply-as-stated.
     - Partially -> apply-with-modification (write the modification rationale).
     - No, the suggestion is wrong, we still agree the issue exists -> apply-with-modification.
   - Is the issue an architectural concern (>1 file, design pattern change)? -> discuss-not-fix.
   - Do we believe the issue isn't real (e.g. the reviewer misread the code)? -> wont-fix (write the reasoning).
```

Apply per-comment grouping per `references/comment-grouping.md`:

- 3+ comments on the same root issue → group into one fix; reply on each.

Write `.temp/task-<slug>/feedback/classification.md` with the per-comment table.

## Phase 4 — propose

1. **Show the classification table** with counts: `A<n>/M<n>/D<n>/W<n>/R<n>`.
2. **Mode branch:**
   - `-i`: walk each comment, allow re-classification.
   - `--auto`: keep classifications as-is.
3. **Approval gate** (unless `--auto`): user confirms the classifications.

## Phase 5 — draft + apply + push + reply

### Phase 5a — draft replies (always)

For each classification, draft per `references/reply-templates.md`:

- `apply-as-stated` → `apply-stated` template (will be filled with commit SHA after Phase 5b).
- `apply-with-modification` → `apply-modified` template.
- `discuss-not-fix` → `discuss` template (with link to follow-up).
- `wont-fix` → `wont-fix` template (with concrete reasoning).
- `already-resolved` → `already-resolved` template.

Write `.temp/task-<slug>/feedback/replies-draft.md`.

### Phase 5b — apply (`--fix` only)

1. **Build the fix queue.** Grouped fixes from Phase 3.
2. **For each grouped fix:** edit code (delegate non-trivial to `/adk-code:code-bugfix`).
3. **Validate after each (or once at end if scope is small):** repo-native tests + typecheck + lint.
4. **Commit per logical fix** (preferred for traceability) OR one squashable commit (under `-i`, ask once).
5. **Capture commit SHAs** to fill into the reply drafts (Phase 5a's templates have `<commit-sha>` placeholders).
6. Write `.temp/task-<slug>/feedback/fix-log.md` with per-fix commit + validation evidence.

### Phase 5c — push (`--fix` only)

1. **PUSH-GATE.** Ask before the first push of the session, even under `--auto --fix`.
2. **Push** to the PR's head branch. NEVER `--force`. NEVER to a branch in `forbid_force_push_branches`.
3. Update `fix-log.md` with the push timestamp.

### Phase 5d — post replies + resolve

1. **Post each reply** via `gh api -X POST /repos/<repo>/pulls/<num>/comments` (with `in_reply_to=<id>` for inline) OR `gh pr comment` (for top-level). Capture receipt IDs.
2. **POST-CONFIRMATION** per `/adk-review:review-pr` `references/post-confirmation.md`:
   - Wait 5s → re-fetch → confirm.
   - On miss: 10s → 20s.
   - On final miss: log to `replies-postback.md` as `unconfirmed`. **NEVER re-post.**
3. **For `apply-*` classifications:** mark thread resolved via `gh api graphql` mutation, AFTER the reply is post-confirmed.
4. **For `discuss-not-fix` / `wont-fix` / `already-resolved`:** post the reply, but DO NOT resolve. Let the reviewer accept or counter.

Write `.temp/task-<slug>/feedback/replies-postback.md` with per-reply receipts + resolution status.

## Phase 6 — report

1. **Final report** at `.temp/task-<slug>/report.md` per `references/output-format.md`.
2. **Surface to user**: classification counts, replies posted (with URLs), commits pushed (with SHAs), threads resolved, threads left open, residual risk.
3. **Offer depth**: "Need more detail on any classification?" — never dump long context unprompted.

## Loop control

- **Same comment classified differently across runs.** When re-running on the same PR, the prior classification.md is moved to `.archive/<iso-ts>/`; the new run starts fresh. The user may notice and re-classify.
- **Post-confirmation final miss.** Surface to user; do NOT re-post; do NOT resolve the thread (resolution requires the reply to be visible).
- **Fix validation fails.** Stop applying further fixes; surface; let user decide whether to skip + continue or abort the queue.
- **Reviewer posts NEW comments mid-session.** Detected via re-fetch in Phase 5d; surfaced as "<n> new comments since classification; consider re-running".
- **More than 4 parallel subagents.** Refuse — coordination overhead grows past 4.

## Key differences from `review-pr --fix`

| Concern | `review-pr --fix` | `review-feedback --fix` |
| --- | --- | --- |
| Performs a full review pass | yes | NO — assumes comments are valid |
| Drafts new findings | yes | NO — only addresses existing |
| Reconciles existing comments | yes (Phase 4) | yes — but the WHOLE skill is reconciliation |
| Per-comment classification | implicit (in reconciliation) | explicit, surfaced for user (5 states) |
| `wont-fix` / `discuss-not-fix` paths | minimal | first-class (templates, follow-up linking) |
| Push gate | yes | yes (same protocol) |
| Post-confirmation | yes | yes (same protocol) |
| Resolves threads | only after reply confirms | only after reply confirms (apply-* only) |
