# Post PR Comments Stage

This stage handles posting review comments to a PR after the primary review is complete. It runs when the current user is NOT the PR author.

---

## Prerequisites

This stage runs after `stages/pr-review.md` has completed and produced a set of accepted findings.

---

## Posting Flow

### Step 1: Collect Accepted Findings

Gather all findings that were accepted (or edited and accepted) during the interactive loop or standard flow. Also collect praise comments (auto-accepted).

### Step 1.5: Merge Same-Line Comments

Before formatting, apply the comment consolidation rules from `stages/pr-review.md`:

1. **Group findings by file + line**: Identify findings targeting the same file:line or overlapping line ranges.
2. **Merge groups**: For each group with 2+ findings, combine into a single merged comment using the merged format from `stages/pr-review.md`.
3. **Merge replies in the same thread**: If multiple reply drafts target the same existing comment thread, combine them into a single reply with `---` section breaks between distinct points.

This prevents comment clutter and makes reviews easier for authors to follow.

### Step 2: Format Comments

Format each finding (or merged finding group) using the canonical comment template from `references/review-comment-template.md`. Use the icon-prefixed format with summary tables for visual scannability:

```md
<icon> **[<PRIORITY>][<PRINCIPLE>]** <Short, specific title>

| | |
|---|---|
| **Location** | `<file-path>:<line-range>` |
| **Confidence** | <score>/100 |
| **Guideline** | <which standard or best practice is violated> |

#### Issue
<description>

#### Where it fails
<cases>

#### Why it matters
<impact>

#### Suggested fix
<recommendation with code>

<details>
<summary>Suggested tests</summary>

<test cases>
</details>
```

Format praise using the lightweight praise template:

```md
:star2: **[Praise][<PRINCIPLE>]** <Short, specific title>

> <1-3 sentences explaining what's well done and why it matters.>
```

### Step 3: Post via MCP or API

**If MCP is available:**
- Use the source-native MCP to post inline review comments at the correct file and line.
- Group related comments into a single review submission when supported.

**If API fallback:**

GitHub:
```bash
# Post a review with inline comments
gh api repos/{owner}/{repo}/pulls/{number}/reviews \
  -f body="Review summary" \
  -f event="COMMENT" \
  --input comments.json
```

Bitbucket:
```bash
curl -s -u "${BITBUCKET_USERNAME}:${BITBUCKET_TOKEN}" \
  -X POST \
  -H "Content-Type: application/json" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments" \
  -d '{"content": {"raw": "..."}}'
```

### Step 4: Resolve Handled Comments

For comments from previous reviews that are now confirmed fixed:
- Resolve the thread on the platform when supported
- Post a brief acknowledgment: "Confirmed fixed in [commit-sha]."

### Step 5: Reopen Critical Threads

For comments that were marked outdated/resolved but the issue persists:
- Reopen the thread when the platform supports it
- Or post a new comment referencing the original thread

---

## Git-Only Fallback

When no MCP or API is available:

1. Write all accepted comments to `.temp/pr-review/pr-<number>-review.md`
2. Each entry includes file path, line number, severity, and full comment body
3. Inform the user: "Review saved to .temp/pr-review/pr-<number>-review.md -- post these comments manually or re-run with the token configured."

---

## Thread Management Rules

- Reuse an existing thread when a new finding matches a live discussion
- Do not repost already-resolved feedback unless the issue is still present
- Prefer line comments when the source supports them and the line mapping is stable
- Fall back to a grouped summary comment when exact line mapping is not possible
- Always reply within comment threads, never post as top-level PR comments for thread-related responses

## Idempotency

Before posting any comment, check for duplicate comments to prevent double-posting when the skill is re-run:

1. Read all existing review comments on the PR by the current user.
2. For each accepted finding, check if a comment with the same file, approximate line range (within 5 lines), and matching title already exists.
3. If a matching comment is found:
   - If the content is substantively the same, skip posting and count as "already posted."
   - If the content differs (e.g., the finding was refined), update the existing comment in-place when the platform supports it. Otherwise, skip and note the discrepancy.
4. Log the deduplication results in the summary.

```text
## Idempotency Check

Already posted (skipped): N
Updated in place: N
New comments posted: N
```

---

## Summary

After posting, display:

```text
## Comments Posted

New comments: N
Praise comments: N
Merged (same-line): N findings → M comments
Resolved threads: N
Reopened threads: N
Failed to post: N (if any)
Output: [PR comments | Markdown at <path>]
```
