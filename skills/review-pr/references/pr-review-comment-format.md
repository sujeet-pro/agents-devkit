# PR Review Comment Format

Canonical shape for every inline comment, reply, and task-resolution note this skill posts on a remote PR. Adopt this exact structure — providers (GitHub, Bitbucket) render Markdown and these labels are the contract reviewers expect.

Keep posted Markdown provider-safe:

- no HTML-heavy formatting
- no nested callouts or admonitions (Bitbucket strips them)
- short headers
- concise paragraphs
- bold labels for the comment title and every section heading

## Stable IDs (in-session only)

Each finding gets a stable ID `F1`, `F2`, `F3`, ... assigned in the order they appear in the report. The ID is for the user-facing accept/reject loop (`a-1,3`, `r-2`, `e-4`); it is NOT posted to the PR. The posted Markdown carries no `F<n>` prefix.

## Reviewer-facing finding card (shown to the user before approval)

The finding card wraps the exact draft that would be posted plus reviewer-facing context the user needs to decide.

````text
### F<id> [<Severity>][<Type>][<focus-area>] <Short, specific title>

Location: `<file:line-or-range>`
Action: <post new inline comment | reply to existing thread | local-only note>
Task: <create | keep open | resolve | none>

Why post this comment:
- <reason 1, reviewer-facing>
- <reason 2>

Exact comment to post:
```md
<the exact Markdown that would land on the PR — see template below>
```

Reviewer explanation:
<1-3 short sentences with the extra context that helps the user decide whether to accept the comment. NOT part of the posted draft.>
````

If a candidate finding is not actually worth posting, do not list it in the main approval queue. Either drop it, or place it in a short non-actionable notes section only when the user asked for exhaustive review notes.

## Canonical posted-comment template

Use this same structure for `Issue`, `Suggestion`, `Nitpick`, `Question`, and `Praise`. Severity is implied by Type + position in the summary, NOT repeated as a separate label inside the comment.

```md
**[<Type>][<primary-focus-area>] <Short, specific title>**

**Confidence:** <0-100>/100 | **Dimension:** <dimension> | **Guideline:** <repo guideline or external standard>

**Issue Explanation:**
<Concise explanation of what is happening, where it fails, and under what condition. Use a few lines when more context is needed.>

**Suggested Fix:**
<Concrete recommendation. Add a fenced code block when a sample materially helps.>

**Impact:**
<Concrete risk if not fixed, or concrete value when this is praise.>
```

### Field guidance

- `Type`: `Blocker` | `Critical` | `Issue` | `Suggestion` | `Nitpick` | `Question` | `Praise`. (`Blocker` and `Critical` ARE Issues with elevated severity — pick the strongest applicable label.)
- `primary-focus-area`: short slug — `correctness`, `security`, `performance`, `architecture`, `patterns`, `code-quality`, `readability`, `accessibility`, `seo`, `docs`, `testing`, `consistency`, `completeness`.
- `Confidence`: 0-100 integer. Below 60: prefer `Question` type. Below 40: do not post — clarify locally first.
- `Dimension`: same vocabulary as `primary-focus-area`. Use this when the focus area in the title is broader than the specific dimension being checked.
- `Guideline`: name a repo doc, lint rule, ADR, RFC, or external standard. If none applies, write `Reviewer judgement`.

### Worked example

```md
**[Critical][correctness] Missing null guard before dereferencing `user.profile`**

**Confidence:** 90/100 | **Dimension:** correctness | **Guideline:** Defensive handling of nullable API payloads

**Issue Explanation:**
`buildCard()` reads `user.profile.avatarUrl` even when the API can return `profile = null`. Suspended-account responses can reach this branch, so the current implementation throws before the page gets a chance to render fallback UI.

**Suggested Fix:**
Guard the nullable branch before using nested profile fields, or normalize the payload earlier in the mapper. For example:

```ts
if (!user.profile) {
  return renderFallbackCard(user);
}

return renderProfileCard(user.profile.avatarUrl);
```

**Impact:**
This breaks rendering for a valid server response, turning a recoverable account state into a user-visible failure.
```

## Praise template

```md
**[Praise][<primary-focus-area>] <Short title>**

**Confidence:** <0-100>/100 | **Dimension:** <dimension> | **Guideline:** <ref>

**Issue Explanation:**
<Explain what is notably well done and why it stands out.>

**Suggested Fix:**
No change required.

**Impact:**
<Concrete positive impact worth reinforcing.>
```

## Summary comment shape (one per PR)

```md
## Review summary

**Verdict:** <approve | request-changes | comment>

**Blockers:** <count>
**Critical:** <count>
**Should Have:** <count>  (kept inline)
**Nitpicks / Questions:** <count>  (kept inline)

### Blockers
- <one-line title> — `<file:line>`
- ...

### Critical
- <one-line title> — `<file:line>`
- ...

### Out of scope
- <items explicitly not reviewed and why>

### Validation
- Diff fetched: YES (`<n>` files, +<adds> / -<dels>)
- Code read in context: YES
- Existing comments reconciled: <kept / stale / restated counts>
- Inline comments posted: <count or N/A>
- Tasks created / resolved (Bitbucket): <count or N/A>
```

## Severity ladder (decides ordering, not posted as a label)

| Severity | Meaning | Goes inline | Goes in summary |
| --- | --- | --- | --- |
| `Blocker` | Must fix before merge | Yes | Yes (listed) |
| `Critical` | Strongly recommended fix; would normally block release | Yes | Yes (listed) |
| `Should Have` | Improvement that meaningfully raises quality | Yes | Counted only |
| `May Have` | Optional polish | Yes | Counted only |
| `Nitpick` | Style or taste only | Yes | Counted only |
| `Question` | Reviewer uncertain; needs clarification | Yes | Counted only |

Lead the report with the highest. Never mix levels in one bullet.

## Consolidation rules

1. Group related findings that share a single location under one F-ID.
2. Use the highest severity in the group.
3. List each sub-issue as a bullet under the consolidated `Issue Explanation`.
4. Keep the consolidated finding actionable — if it grows beyond ~5 sub-points, split it into multiple Fs.
