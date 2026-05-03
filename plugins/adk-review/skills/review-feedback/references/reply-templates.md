# `review-feedback` — reply templates

The 5 canonical reply templates, one per classification state. Closely related to `/adk-review:review-pr` `references/pr-reply-templates.md`; this skill uses an extended set scoped to feedback triage.

## Template index

| Template | Classification | Thread resolved after reply? |
| --- | --- | --- |
| `apply-stated` | `apply-as-stated` | yes (after post-confirmation) |
| `apply-modified` | `apply-with-modification` | yes (after post-confirmation) |
| `discuss` | `discuss-not-fix` | NO (by design) |
| `wont-fix` | `wont-fix` | NO (by design) |
| `already-resolved` | `already-resolved` | NO (let reviewer click) |

## `apply-stated`

```
Done in <commit-sha>. <one-line summary of what changed>

<optional: 1 sentence on a tradeoff or follow-up if relevant>

— /adk-review:review-feedback
```

### Example

```
Done in a1b2c3d. Added `RequireRole("admin")` to the route group; matches the pattern at routes/admin.go:18-31.

— /adk-review:review-feedback
```

### Variant: same SHA addresses multiple comments (grouped)

When one commit addresses multiple comments, each thread gets its own `apply-stated` reply with the SAME SHA but a per-thread one-liner:

```
Done in a1b2c3d. Added shared `validateProduct` validator and applied to `POST /products` (this handler at line 42).

— /adk-review:review-feedback
```

```
Done in a1b2c3d. Same shared `validateProduct` applied to `POST /products/bulk` (this handler at line 78).

— /adk-review:review-feedback
```

(Both reference the same commit; each is anchored to the right handler.)

## `apply-modified`

```
Done in <commit-sha> with a small modification: <what differed from the suggestion> (<one-line reasoning>).

<optional: 1 sentence on a follow-up>

— /adk-review:review-feedback
```

### Example

```
Done in ghi9012 with a small modification: renamed `processOrder` to `processOrderItem` (clarifies the per-item scope) instead of extracting a helper. Extracting would have forced 14 callers to wire in a context.Context. Happy to revisit if we add a second per-item codepath.

— /adk-review:review-feedback
```

### Important

- **The modification rationale is not optional.** The reviewer needs to see why we deviated.
- **The modification should be smaller-or-equal in scope** to the original suggestion. If it's bigger, classify as `discuss-not-fix` instead.
- **Cite the file:line of the change** if the diff isn't obvious.

## `discuss`

```
<one-sentence acknowledgment that the point is valid>. This is non-trivial — would prefer to discuss in person rather than turn this into a thread.

<one sentence sketching the gist of our thinking>.

Tracked at <follow-up link>. Suggesting we sync at <when-and-where>.

— /adk-review:review-feedback
```

### Example

```
Good architectural point — this is non-trivial and I'd rather discuss in person than turn this thread into an essay.

Sketch: the Repository pattern would help if we add a second backend (NoSQL / message queue), but with one SQL backend the abstraction layer is overhead.

Tracked at https://acme.atlassian.net/browse/CHK-1340. Suggesting we sync at the next platform standup, or DM me on Slack.

— /adk-review:review-feedback
```

### Important

- **Always link a follow-up.** Jira ticket, sync invite, DM. Without it, the thread is a void.
- **Always sketch the gist** so the reviewer doesn't have to wait for the sync to know your direction.
- **Always offer a concrete next step** (when-and-where).
- **Thread STAYS OPEN.** Don't auto-resolve.

## `wont-fix`

```
Considered this; respectfully pushing back.

Reasoning: <one or two sentences with concrete signal — name the constraint, the file/line, the trade-off, or the prior decision>.

<optional: link to the ADR / prior discussion / data that supports the position>.

Happy to revisit if <concrete trigger that would change the answer>. Otherwise, suggest closing the thread on your end.

— /adk-review:review-feedback
```

### Example

```
Considered this; respectfully pushing back.

Reasoning: the endpoint is admin-only; cardinality is bounded by team size (~50 orgs); pagination would add complexity without measurable benefit. The team explicitly deferred pagination in ADR-2026-Q1 (linked).

ADR: docs/adr/2026-Q1-admin-endpoint-pagination.md

Happy to revisit if external traffic ever lands here, or if we add an org-of-orgs feature. Otherwise, suggest closing the thread on your end.

— /adk-review:review-feedback
```

### Important

- **Concrete reasoning is the minimum.** Plain "won't fix" is rude.
- **Cite the constraint / ADR / data.** Anchored disagreement is engaging; vague disagreement is dismissive.
- **Offer the trigger that would change the answer.** Shows we considered the position seriously.
- **End with the suggested next step** (typically: "close on your end").
- **Thread STAYS OPEN.** Don't auto-resolve. The reviewer accepts or counters.

## `already-resolved`

```
Looks like this was addressed in <commit-sha-or-ref> (<one-line summary of the resolving change>). <optional: file:line citation>.

<optional: 1 sentence on whether the resolving change was related to the comment, or independent>.

Marking the thread to resolved on my end — please click resolve if you agree.

— /adk-review:review-feedback
```

### Example

```
Looks like this was addressed in a1b2c3d (added the null check at user.go:42 — independent of this comment, came in via the auth refactor PR).

Marking the thread to resolved on my end — please click resolve if you agree.

— /adk-review:review-feedback
```

### Important

- **Cite the resolving commit / file:line.** Required evidence.
- **Note whether the resolution was related or independent.** Helps the reviewer understand the timeline.
- **Thread STAYS OPEN.** The phrase "marking to resolved on my end — please click resolve if you agree" signals; we don't actually click. Let the reviewer.

## Hard rules across all templates

1. **Always include the commit SHA** for `apply-*` replies. The SHA is the proof.
2. **Always sign with the attribution line** — `— /adk-review:review-feedback`.
3. **Always cite file:line** when the reply references code.
4. **Never use emojis** (per the universal interaction contract).
5. **Never quote >15 words verbatim** from the comment or the code.
6. **Never close a thread without a reply.**
7. **Never resolve a `discuss` / `wont-fix` / `already-resolved` thread automatically.** Only `apply-*` threads auto-resolve (after reply confirms).
8. **Match the repo's tone** per `~/.config/adk/review.md.house_style` if set.
9. **Keep replies short.** 2-5 sentences for `apply-stated` / `apply-modified`. 3-7 for `discuss` / `wont-fix` / `already-resolved`.
10. **Never re-litigate the design** in a `discuss` reply. Sketch + link to follow-up.
11. **Never silently change the meaning** of the reviewer's comment when paraphrasing.

## Tone calibration via `~/.config/adk/review.md`

```yaml
house_style: formal | casual | terse  # default: formal
sign_off: "— /adk-review:review-feedback"  # default; can override
```

Examples:

- `formal` (default): "Considered this; respectfully pushing back."
- `casual`: "Pushing back on this one."
- `terse`: "No — see ADR-2026-Q1."

The skill defaults to `formal` because reviewers are usually peers across teams and tone-matching reduces friction.

## When NOT to draft a reply at all

- Comment is from a bot (Dependabot, CodeRabbit, etc.) — let the bot's own resolution mechanism handle it. Surface in `report.md`.
- Comment is on a file owned by a different team per CODEOWNERS — defer; the team owner replies. Surface as "deferred to <owner>".
- Comment is meta (e.g. "rebase on main please") — handle the meta action; no reply needed.
