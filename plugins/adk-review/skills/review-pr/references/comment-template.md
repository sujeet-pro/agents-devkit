# `review-pr` — comment template

The canonical shape for every posted PR comment. Used by Phase 6a (post) and Phase 6b (replies).

## Inline comment template (Phase 6a)

Posted via `gh pr review --comment -F` as part of one consolidated review, or via `gh api /repos/<repo>/pulls/<num>/comments` for individual comments.

```
**Type:** Code-review finding
**Severity:** <Blocker | Critical | Should-Have | May-Have | Nitpick | Question>
**Confidence:** <low | med | high>
**Dimension:** <correctness | security | performance | tests | docs | style>

### Issue
<one to two sentences — what's wrong, in plain language>

### Fix
<one to two sentences — the smallest correct change>
<optional: a 3-5 line code suggestion in a fenced ```suggestion block (GitHub-rendered)>

### Impact if unfixed
<one sentence — what goes wrong in production / for the user / for the codebase>

<optional: References — line/file pointers to the existing convention or the related fix>

— posted by `/adk-review:review-pr` for <reviewer-name>
```

### Worked example

```
**Type:** Code-review finding
**Severity:** Blocker
**Confidence:** high
**Dimension:** security

### Issue
The new `/admin/users/delete` endpoint at `routes/admin.go:42` doesn't call `RequireRole("admin")` like the other admin handlers in this file. Any authenticated user can call it.

### Fix
Wrap the route in the existing admin middleware group, or add the role check in the handler:
```suggestion
admin := router.Group("/admin", middleware.RequireRole("admin"))
admin.POST("/users/delete", adminHandler.DeleteUser)
```

### Impact if unfixed
Privilege escalation: any authenticated user can delete any other user.

References: see the existing pattern at `routes/admin.go:18-31`.

— posted by `/adk-review:review-pr` for Sujeet Jaiswal
```

## Reply template (Phase 6b)

Used when replying to existing reviewer comments on your own PR (the `own` ownership path). See `references/pr-reply-templates.md` for the full set of reply templates (fix-acknowledged / fix-applied / pushback / partial / clarification).

## Top-level review summary (Phase 6a)

When posting as one consolidated review (the default), the review body itself uses this template:

```
## review-pr summary
- Severity counts: B<n>/C<n>/S<n>/M<n>/N<n>/Q<n>
- Reviewed at head SHA: <sha>
- Top issue: <one-line description of the highest-severity finding>

<optional: 1-2 sentence framing of the overall change — only when it materially helps the author land the PR>

— posted by `/adk-review:review-pr` for <reviewer-name>
```

The actual findings are inline comments on the diff lines; the top-level body just gives the author the at-a-glance.

## Hard rules for the template

1. **Always include the 4 header fields** (Type / Severity / Confidence / Dimension). Skipping them makes the comment ungroupable.
2. **Always include `Issue` + `Fix` + `Impact if unfixed`** as labeled sections. The author's eye goes to `Fix:` first.
3. **Code suggestions use the GitHub-rendered `suggestion` fenced block** when the fix fits in ≤5 lines. Larger fixes describe the change in prose.
4. **Quote ≤15 words** verbatim from the file. The full quote belongs in the `findings.md` artifact, not in the posted comment (which links back to the diff line anyway).
5. **No emojis.** Per the universal interaction contract.
6. **No "I noticed" / "I think" / "maybe consider".** State the issue and the fix directly. The Confidence field carries the uncertainty.
7. **No "as a Principal Engineer".** No appeal to authority. The evidence is the authority.
8. **Never quote a secret value verbatim** (security findings of type `secret_in_diff`). Name the type + location.
9. **End with a single attribution line** — `— posted by /adk-review:review-pr for <reviewer-name>`. Lets the author / future-self trace where the comment came from.
10. **Match the repo's tone.** If the codebase has a casual / formal house style for comments, match it. (`~/.config/adk/review.md` may carry an `house_style` override.)

## Severity-prefix convention (alternative)

If the user prefers shorter inline comments, the template degrades to:

```
**[<Severity>] [<dimension>]** <one-line summary>

<one or two sentences combining issue + fix + impact>

— posted by `/adk-review:review-pr` for <reviewer-name>
```

Toggled via `~/.config/adk/review.md.comment_style: short`. Default is the full template.
