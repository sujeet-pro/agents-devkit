# `review-feedback` — comment classification

The 5-state classification rubric. Every open comment gets exactly one classification.

## States

| State | Definition | Action |
| --- | --- | --- |
| `apply-as-stated` | The reviewer's comment is clear and actionable; the suggested fix is correct as-is. | Apply the suggestion verbatim; reply with commit SHA. |
| `apply-with-modification` | The reviewer's comment is clear and actionable; we agree the issue exists; the suggested fix isn't quite right; we apply a better variant. | Apply the modified fix; reply with commit SHA + the modification rationale. |
| `discuss-not-fix` | The comment raises an architectural / design / cross-cutting concern that needs a sync conversation, not a code edit. | Reply with `discuss` template + link to a follow-up (Jira / sync invite / DM). Thread stays OPEN. |
| `wont-fix` | We genuinely disagree with the reviewer's reasoning. | Reply with `wont-fix` template + concrete reasoning + offer to discuss in person. Thread stays OPEN. |
| `already-resolved` | The underlying issue is no longer present (e.g. fixed by an intervening commit; or the reviewer was reading stale code). | Reply with `already-resolved` template citing the resolving change. Thread stays OPEN (for reviewer to confirm + click resolve). |

## Decision algorithm

```
For each open comment:

1. Read the comment body. Extract:
   - The issue (heuristic: first sentence; or first paragraph; or anything before "consider" / "suggest").
   - The suggested fix (if any). May be in a `suggestion` block, or in prose.

2. Read the current code at the comment's target line.
   - If the file is gone or the line is gone: try fuzzy re-anchor (search ±20 lines for the comment's contextual snippet).
   - If still gone: classify `already-resolved` (the diff has moved on).

3. Compare current code to the issue:
   - If the issue is no longer present (e.g. the null-check the reviewer wanted is now there) -> classify `already-resolved`.
   - Else: continue.

4. Evaluate the suggested fix (if any):
   - Does the suggestion actually solve the issue? (Read: does it compile conceptually + address the root cause?)
     - Yes, fully -> classify `apply-as-stated`.
     - Partially / has a flaw -> classify `apply-with-modification`. Write the modification rationale.
   - No suggestion in the comment body -> next step.

5. If no suggestion was given:
   - Is the issue an architectural concern (touches >1 file, or implies a design pattern change)? -> classify `discuss-not-fix`.
   - Is the issue a code-level concern we can fix in <1 hour? -> classify `apply-with-modification` (we agree; we'll write the fix).

6. If we evaluated and we don't agree the issue is real (e.g. the reviewer misread the code, or the constraint they cite doesn't apply):
   - Re-read once more, with the assumption that the reviewer is right (humility check).
   - If still confident we disagree -> classify `wont-fix`. Write concrete reasoning.
```

## Worked classification examples

### `apply-as-stated`

**Comment:** "Use `{product.name}` instead of `dangerouslySetInnerHTML` — XSS risk." (with a `suggestion` block showing `<div>{product.name}</div>`)

**Classification:** `apply-as-stated`. The suggestion is correct; we apply verbatim.

### `apply-with-modification`

**Comment:** "Consider extracting a helper for this." (no suggestion block)

**Reading:** the issue is that `processOrder` mixes two concerns (validation + persistence). Extracting a helper would force every caller (14 sites) to wire in a context.Context.

**Classification:** `apply-with-modification`. Better fix: rename `processOrder` to `processOrderItem` (clarifies the per-item scope) instead of extracting. Reply explains.

### `discuss-not-fix`

**Comment:** "I think this whole module should use the Repository pattern; the current shape is going to bite us."

**Reading:** the issue is architectural. Refactoring would touch 12 files and 4 callers across 2 services. It's a real concern but not a "fix in this PR" concern.

**Classification:** `discuss-not-fix`. Reply: link a Jira ticket for the architectural discussion + propose a sync at the next platform standup.

### `wont-fix`

**Comment:** "This will perform poorly with >1000 orders; need to add pagination."

**Reading:** the endpoint is internal admin-only; the operator's `~/.config/adk/datadog.md.slo_thresholds` doesn't list it; the team has explicitly decided not to paginate this endpoint per a 2026-Q1 ADR (which the reviewer may not have read).

**Classification:** `wont-fix`. Reply: cite the ADR + the fact that the endpoint is admin-only + the cardinality is bounded by team size (~50 orgs) + offer to revisit if external traffic ever lands here.

### `already-resolved`

**Comment posted 3 days ago:** "Missing null check on `user.email`."

**Current code:** the null check IS present, added by an intervening commit (`<sha>`).

**Classification:** `already-resolved`. Reply: "Looks like this was addressed in `<intervening-sha>`. Marking the thread to resolved." Thread stays open for reviewer to click.

## Edge cases

### Comment is a question, not a finding

**Comment:** "Is this thread-safe?"

The comment isn't asking for a fix; it's asking for clarification. Two options:

- If we know the answer: classify `apply-with-modification` (the "modification" is an explanatory comment in code or a docstring + a reply quoting it).
- If we don't know: classify `discuss-not-fix` (we'll think about it + reply later).

### Comment is a suggestion that we already addressed independently

**Comment:** "Add a test for the n+1 path."

**Current code:** the test was added in the latest commit (independent of the comment).

**Classification:** `already-resolved`. Reply: "Done in `<sha>` (added independently of this comment); thanks for catching the same gap."

### Multiple comments on the same root issue

3 comments flag the same root: "missing input validation in 3 endpoints".

**Classification:** all 3 → `apply-as-stated` (or `apply-with-modification`). Group into 1 logical fix per `references/comment-grouping.md`. Reply on each with the same SHA + per-handler one-liner.

### Comment is from a bot (Dependabot, CodeRabbit, etc.)

**Classification:** `discuss-not-fix` with treatment "delegated to the bot's resolution mechanism" — let the bot's own logic handle it. Surface in `report.md` as "bot comment; deferred".

### Thread has multiple replies (back-and-forth between reviewer + previous author)

**Reading:** read the entire thread; the LATEST relevant message is what we classify. If the reviewer's latest message says "OK, I see your point; ignore my comment", classify `already-resolved`.

### Comment is inflammatory or off-topic

**Reading:** rare; if encountered, classify `discuss-not-fix` with treatment "off-topic; surface to manager / lead". Don't engage in the thread.

## What classifications are NOT

- **`wont-fix` is NOT a way to defer hard things.** If you can fix it in 10 minutes, it's `apply-*`. `wont-fix` is for genuine disagreement.
- **`discuss-not-fix` is NOT a way to avoid replies.** Always link a follow-up (Jira / sync / DM). A `discuss-not-fix` with no follow-up is a black hole.
- **`apply-with-modification` is NOT a way to over-engineer.** The modification should be smaller-or-equal in scope to the suggested fix; if it's bigger, that's a `discuss-not-fix`.
- **`already-resolved` requires evidence.** Cite the resolving SHA / commit / file:line. Don't guess.

## Per-comment reasoning capture

Every classification in `classification.md` includes a one-line `Reasoning` field. This is the audit trail; it's also what `apply-with-modification` / `wont-fix` / `discuss-not-fix` replies are built from.

Examples:

- `apply-as-stated` reasoning: "clear actionable; suggested fix is correct".
- `apply-with-modification` reasoning: "agree; better fix is rename instead of extract (avoids context.Context wiring across 14 callers)".
- `discuss-not-fix` reasoning: "architectural; touches 12 files; tracked at CHK-1340".
- `wont-fix` reasoning: "endpoint is admin-only; ADR-2026-Q1 explicitly defers pagination; cardinality bounded".
- `already-resolved` reasoning: "null check added in `<intervening-sha>`".
