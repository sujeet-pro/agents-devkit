# PR Reply Templates

Canonical reply shapes for responding to existing comments and threads on a PR. All replies follow the same provider-safe Markdown rules as `pr-review-comment-format.md` (no HTML-heavy formatting, no nested callouts, short paragraphs).

Each template below is short on purpose — replies should not restate the original concern; they should declare the resolution, the pushback, or the request, and leave a clear next step.

## Fix-acknowledged reply (you re-validated and the fix is correct)

```md
Confirmed in the latest revision. <One sentence describing what you re-checked and what evidence you used.>
```

Use when:

- You posted a comment in a previous round.
- The author pushed a change.
- You re-read the diff and confirmed the concern is addressed.

## Fix-applied reply (your own PR, after you actually pushed the fix)

```md
Fixed in the latest push. <One sentence describing what changed and, if relevant, what was validated.>
```

Use only after the fix is pushed AND validated. Never post this preemptively.

### Worked example

```md
Fixed in the latest push. Added the null guard in `buildCard()` and covered the suspended-account case with a unit test (`buildCard.test.ts:142`).
```

## Pushback reply (the comment is technically incorrect)

```md
Keeping the current implementation. <Technical explanation grounded in the current code and behavior. Reference the file:line that justifies the position.>
```

Rules:

- Never use this without a concrete technical reason.
- Cite the exact file:line that contradicts the comment.
- Do not be defensive; treat the reviewer as right-by-default and walk through the evidence.

### Worked example

```md
Keeping the current implementation. The payload is already normalized in `mapUserResponse()` (`src/api/mapUserResponse.ts:48-61`), so adding another guard here would be redundant and would not change behavior.
```

## Explanation-accepted reply (author replied; no code change needed)

```md
The explanation makes sense and the current implementation matches it. No code change needed here.
```

Use when an author reply is sufficient and the original concern was a Question or Suggestion that the author talked you down on.

## Partial-fix reply (some of it is fixed; gap remains)

```md
The latest change addresses part of this, but the remaining gap is still <brief remaining risk>. Leaving this open so the remaining case can be handled.
```

Use when only part of the originally-reported issue is resolved. Keep or recreate the linked task on Bitbucket.

## Clarification request (feedback is unclear; do not implement yet)

```md
Not enough context to apply this safely yet. Can you clarify the intended behavior for <specific case>?
```

Use when reviewer feedback is ambiguous and applying it would be guesswork. Do not implement until clarified.

## Task-resolution note (Bitbucket task being resolved)

Posted as the resolution comment when closing a Bitbucket task after re-validation:

```md
Confirmed handled in the latest code state. Resolving the task.
```

Rules:

- Only post when you have re-read the current code and confirmed the concern is addressed.
- If the code moved, restate the concern at the new location BEFORE resolving (see next template).
- Never resolve a task purely because the author replied "fixed".

## Task-restatement note (concern still applies; code moved or was reverted)

```md
The original concern still applies in the current code state, so restating it at the updated location and keeping the follow-up open: `<new file:line>`.
```

Use when:

- A previously-resolved task's concern has reappeared.
- The code being reviewed moved to a new location since the original comment was posted.
- The author marked a task resolved but the underlying issue is still present.

## Stale-comment dismissal (concern no longer applies)

```md
No longer applicable in the current diff: <one sentence on why — code removed, replaced by `<new file:line>`, behavior changed by `<commit-sha>`, etc.>. Closing the thread.
```

Use when an existing comment was filed against code that has since been removed or fundamentally changed by a later push, AND the original concern no longer applies.

## Out-of-scope acknowledgement (valid point, wrong PR)

```md
Valid point but out of scope for this PR. Tracked for follow-up: <link to issue / task / TODO>. Closing the thread here.
```

Use when a reviewer surfaces a real issue that does not belong in the current change set. ALWAYS create the follow-up before posting this reply; the linked tracker is the contract.
