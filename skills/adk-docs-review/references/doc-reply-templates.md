# Doc Review Reply Templates

Reply shapes for responding to existing comments on a Confluence page (only relevant under `--mode confluence`). Same provider-safe Markdown rules as `doc-review-comment-format.md`.

Each template is short on purpose — replies should not restate the original concern; they should declare the resolution, the pushback, or the request and leave a clear next step.

## Fix-acknowledged reply (you re-validated and the doc is now correct)

```md
Confirmed in the latest revision. <One sentence describing what you re-checked and what evidence you used (e.g., "command now matches `cli/index.mjs:42-58`").>
```

Use when:

- A previous reviewer (or you, in an earlier round) raised a concern.
- The page owner edited the doc.
- You re-read the doc + source and confirmed the concern is addressed.

## Pushback reply (the comment is technically incorrect)

```md
Keeping the current wording. <Technical explanation grounded in the source. Reference the file:line that justifies the position.>
```

Rules:

- Never use this without a concrete technical reason.
- Cite the exact source-of-truth file:line that justifies the doc as-written.
- Treat the original commenter as right-by-default and walk through the evidence.

### Worked example

```md
Keeping the current wording. The doc says the command supports `--auto`, and `cli/index.mjs:118` confirms `--auto` is accepted (it is forwarded to the runner). The earlier comment may have been against an older revision of the CLI.
```

## Explanation-accepted reply (author / owner replied; no doc change needed)

```md
The explanation makes sense and the current doc matches it. No change needed here.
```

Use when an owner reply is sufficient and the original concern was a Question or Suggestion that the owner talked you down on.

## Partial-fix reply (some of it is fixed; gap remains)

```md
The latest edit addresses part of this, but the remaining gap is still <brief remaining risk — e.g., "the dark-mode screenshot in section 4 is still v2.x and the CLI is now v3.x">. Leaving this thread open so the remaining case can be handled.
```

Use when only part of the originally-reported issue is resolved.

## Clarification request (feedback is unclear; do not act on it yet)

```md
Not enough context to act on this safely yet. Can you clarify <specific aspect> — for example, <a concrete example of the ambiguity>?
```

Use when reviewer feedback is ambiguous and acting on it would be guesswork.

## Stale-comment dismissal (concern no longer applies)

```md
No longer applicable in the current page state: <one sentence on why — section was rewritten in `<revision>`, the source-of-truth changed in `<commit-sha>`, the env var was renamed and the doc now matches, etc.>. Closing the thread.
```

Use when an existing comment was filed against doc content that has since been removed or fundamentally changed by a later edit, AND the original concern no longer applies.

## Out-of-scope acknowledgement (valid point, wrong page)

```md
Valid point but out of scope for this page. Tracked for follow-up: <link to the right page / Jira issue / TODO>. Closing the thread here.
```

Use when a reviewer surfaces a real issue that does not belong on the current page (e.g., it's about the linked architecture doc, not this onboarding guide). ALWAYS create the follow-up before posting this reply.

## Anchor-restatement note (concern still applies; section moved)

```md
The original concern still applies. Restating at the updated location: `<new section heading + anchor>`.
```

Use when a previously-resolved comment's underlying concern has reappeared in the page after a restructure, OR when the page owner moved the relevant section without addressing the original issue.
