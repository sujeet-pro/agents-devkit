# PR Review Stage

This stage handles reviewing a PR created by someone else. It covers first review with interactive comment loop, re-reviews with comment reconciliation and reply evaluation, and PR status management.

This stage is review-only. Do not update the PR branch in place. Leave source comments or produce a markdown review artifact.

---

## Source Handling

When MCP or API is available:

Read the PR metadata, diff, commits, existing review comments, thread status, and any prior resolutions before starting analysis.

When git-only fallback:

Read the diff between the PR branch and its target branch, along with commit history on the PR branch.

---

## Dual Diff Review

**Every review** (whether via MCP, API, or git-only) must analyze the changes through **both** approaches and merge the findings:

### Approach 1: PR Diff Review

Read the raw diff (from MCP, API, or `git diff <target>...<head>`). This catches:
- Exact line changes and their context
- Files added, removed, renamed
- Diff-visible issues like incomplete migrations or leftover debug code

### Approach 2: Isolated Branch Review (Git Worktree)

Use a **git worktree** to review the PR branch in isolation. This allows multiple PRs to be reviewed in parallel from different terminals without checkout conflicts.

```bash
# Ensure we have the PR branch locally
git fetch origin <head-branch>

# Create an isolated worktree for this review
git worktree add .temp/worktrees/pr-<number> <head-branch>
```

All file reads for the full-context review happen inside the worktree directory (`.temp/worktrees/pr-<number>/`). Do **not** checkout the PR branch in the main working tree.

```bash
# Get changed files relative to target (from within the worktree)
git -C .temp/worktrees/pr-<number> diff --name-only <target-branch>...<head-branch>
```

For each changed file, read the **full file** from the worktree (not just the diff hunk) to catch:
- Issues in surrounding code that interact with the change
- Missing imports or type mismatches outside the diff
- Broken invariants across the file
- Whether a suggested pattern already exists elsewhere in the file

### Worktree Lifecycle

- **Create** at the start of the review: `git worktree add .temp/worktrees/pr-<number> <head-branch>`
- **Use** throughout the review for all full-file reads and validation commands
- **Clean up** after the review completes (Phase 5): `git worktree remove .temp/worktrees/pr-<number>`
- If the worktree already exists (re-run), update it: `git -C .temp/worktrees/pr-<number> pull --ff-only origin <head-branch>`
- Worktrees are inside `.temp/` which is gitignored, so they never pollute the main repo

### Parallel Review Support

Because each PR gets its own worktree under `.temp/worktrees/pr-<number>/`, multiple PRs can be reviewed simultaneously from different terminals:

- Terminal 1: reviewing PR #42 -> worktree at `.temp/worktrees/pr-42/`
- Terminal 2: reviewing PR #87 -> worktree at `.temp/worktrees/pr-87/`
- Terminal 3: reviewing PR #103 -> worktree at `.temp/worktrees/pr-103/`

Each review session is fully isolated. Session data also uses the PR number for isolation: `.temp/interactive/pr-<number>/` for TUI state, `.temp/pr-review/pr-<number>-review.md` for the markdown artifact.

### Merging Both Approaches

Deduplicate findings from both approaches. If a finding appears in both, keep the one with more context. If a finding only appears in the branch checkout review, mark it as `[full-context]` in the output.

---

## Implementation Approach Alignment

Before reviewing individual code changes, understand what the PR is trying to accomplish at a high level. This prevents review comments that suggest a completely different approach when the chosen approach is sound.

### Step 1: Read PR Intent

- Read the PR title and description.
- Read commit messages on the PR branch.
- Identify the stated goal, approach, and any design decisions mentioned.
- Note any linked issues, specs, or ADRs referenced in the description.

### Step 2: Diff-Level Approach Detection

From the diff, identify the actual approach taken:

- What patterns were introduced or modified?
- What files were added, modified, or deleted?
- What is the architectural shape of the change (new module, refactor, migration, hotfix)?
- What dependencies or imports changed?

### Step 3: Align Intent with Implementation

Compare stated intent (from description and commits) with actual implementation (from diff):

- **Flag misalignment**: If the description says "add caching" but the diff shows a database schema change, that's a mismatch that needs clarification before detailed code review.
- **Identify undocumented decisions**: Architectural choices visible in the code but not mentioned in the description (e.g., chose a specific data structure, added a new abstraction layer, changed an API contract).
- **Detect scope creep**: Changes in the diff that don't relate to the stated goal.

### Step 4: Set Review Lens

Use the aligned understanding to frame all review comments:

- Comments should reference the stated approach: "Given the approach of X, this Y is problematic because..."
- Suggestions should be consistent with the PR's architectural direction — don't propose a completely different approach unless the approach itself is the concern (in which case, frame it as a high-level architectural comment, not a line-level nit).
- If the approach itself seems wrong, raise it as a single top-level comment before proceeding with line-level review.

---

## Mode Detection

When `mode=auto` (the default):

1. After reading the PR metadata and existing review comments, check whether the current user has previously submitted a review on this PR.
2. If the current user has **no prior review comments** on this PR -> treat as a **fresh review** and use the **interactive** flow.
3. If the current user has **prior review comments** on this PR -> treat as a **follow-up review** and use the **followup** flow.

When `mode=standard`, `mode=interactive`, or `mode=followup`, skip auto-detection and use the specified flow directly.

---

## Large PR Handling

When the PR diff exceeds 500 changed lines:

1. Present a PR structure overview:
```text
## Large PR Detected - <N> files, <M> lines changed

Areas of change:
1. <area 1>: N files, M lines -- <brief description>
2. <area 2>: N files, M lines -- <brief description>
3. <area 3>: N files, M lines -- <brief description>

Focus options:
[A]ll areas | [1-3] Specific areas | [C]ritical paths only | [S]ecurity focus
```

2. Use the user's selection to prioritize review depth -- deeply review selected areas, surface-scan others.

---

## Comment Reconciliation

Before generating new findings, build a comment ledger with these buckets:

- open and still actionable
- handled in code but not resolved yet
- marked resolved or outdated
- ambiguous and needs re-verification

For each prior comment:

- re-review the latest diff or file state before assuming the issue is fixed
- if the issue is truly handled, avoid reposting it and resolve or acknowledge it when the source supports resolution
- if the issue was marked outdated or resolved but the risk is still present and critical, reopen the thread when the source supports it or post a replacement comment that references the unresolved risk
- if the issue is partially fixed, post only the remaining gap

---

## Required Child Agents

Run at least these child agents in parallel:

- `code-reviewer` for correctness, security, performance, tests, and code patterns
- `repo-auditor` for architecture, dependency direction, and change isolation
- `doc-reviewer` for docs, migration notes, naming, and reviewer ergonomics
- one domain specialist pass for frontend, backend, or design-system concerns
- `source-publisher` after consolidation if `publish` includes source posting

---

## UI Review Pass

When `ui=true` or when the PR is auto-detected as frontend (touches `.tsx`, `.jsx`, `.vue`, `.svelte`, `.css`, `.scss` files):

Add a UI review child agent that checks:
- Visual consistency with existing patterns
- Accessibility (ARIA, keyboard nav, focus management)
- Responsive design (breakpoint coverage)
- Interaction states (empty, loading, error, disabled)
- Component API ergonomics

UI findings follow the same interactive loop and comment template as code review findings.

For full visual audit, suggest using `/review --focus ui` for a dedicated 6-pillar UI/UX review.

---

## Review Requirements

Every review must cover:

- correctness and regressions
- security and performance
- architecture and boundary fit
- tests, docs, and migration impact
- code patterns and maintainability
- reconciliation of prior comments and thread state

When `focus` is specified, weight child agent priorities accordingly:
- `security` -> security reviewer gets extra depth, others surface-scan
- `performance` -> performance analysis prioritized
- `ui` -> UI review pass activated, visual patterns prioritized
- `correctness` -> correctness and regression analysis prioritized
- `architecture` -> boundary, coupling, and migration impact prioritized

---

## Auto-Validation Phase

**Before presenting any finding to the user**, every generated comment must pass an automated validation against the actual code on the PR branch. This phase runs after child agent consolidation and before the interactive loop.

### Validation Steps

For each candidate finding:

1. **File existence check**: Verify the referenced file exists on the PR branch.
   - If deleted or renamed, discard the finding or re-map to the new path.

2. **Line accuracy check**: Verify the referenced line number matches the described code.
   ```bash
   # Read the actual line(s) from the worktree
   sed -n '<line>p' .temp/worktrees/pr-<number>/<file-path>
   ```
   - If the line content doesn't match what the finding describes, attempt to locate the correct line by searching the file for the described pattern.
   - If the pattern is not found, discard the finding.

3. **Code state verification**: Verify the issue described actually exists in the current code.
   - Read the full function/block containing the referenced line.
   - Confirm the described condition (null dereference, missing check, N+1 query, etc.) is actually present.
   - If the code already handles the described scenario (e.g., a null check exists that the reviewer missed), discard the finding.

4. **Suggested fix applicability**: Verify the suggested fix is compatible with the actual code.
   - Check that variables, types, and imports referenced in the suggestion exist.
   - Check that the suggested pattern doesn't conflict with the surrounding code.
   - If the suggestion references APIs or patterns not used in this codebase, flag it for revision.

5. **Duplicate/stale check**: Verify the finding isn't already addressed by another change in the same PR.
   - Search other files in the diff for the same fix already applied.
   - If the issue is handled elsewhere (e.g., a shared utility was added), discard.

6. **Suggested fix verification**: For each finding that includes a suggested fix with a code snippet:
   - Mentally apply the fix to the actual code at the referenced location.
   - Verify the fix parses correctly in the surrounding context (correct syntax, matching types, valid imports).
   - Check that the fix does not break adjacent code (variable references, return types, function signatures).
   - If the fix is non-trivial or touches shared interfaces, mark it as "suggested fix needs manual verification" rather than presenting it as a drop-in replacement.
   - Verify the fix is consistent with the project's coding patterns detected by the `/coding` skill.

### Validation Outcomes

| Outcome | Action |
|---------|--------|
| All checks pass | Keep the finding, proceed to interactive loop |
| Line mismatch but issue found at different line | Update line reference, keep the finding |
| Issue not present in actual code | **Discard** -- do not present to user |
| Suggested fix incompatible | Keep the finding, revise or remove the suggestion |
| File doesn't exist | **Discard** |

### Validation Report

After validation, log a brief summary before the interactive loop:

```text
## Auto-Validation Summary

Findings from child agents: N
Validated and kept: M
Discarded (not present in code): K
Line references corrected: L
Suggestions revised: J
```

Only validated findings proceed to the interactive loop or standard posting.

---

## Interactive Flow (Fresh Review)

Used when `mode=interactive` or when auto-detection selects a fresh review (the default for first-time reviews).

### Phase 1: Review

1. Run the full review pipeline: preflight, source handling, comment reconciliation, guideline loading, child agents.
2. Run the Dual Diff Review (both PR diff and branch checkout approaches).
3. Consolidate findings: deduplicate, assign severity and confidence scores.
4. Filter findings below the confidence threshold.

### Phase 2: Auto-Validation

Run the Auto-Validation Phase on all consolidated findings. Only validated findings proceed.

### Phase 3: Interactive Review TUI

Launch the interactive review TUI so the user can accept, reject, or request edits on all findings at once.

#### Step 1: Prepare Session

Create the session directory and write all validated findings as `items.json`:

```bash
mkdir -p .temp/interactive/pr-<number>/
```

Write `.temp/interactive/pr-<number>/items.json`:

```json
{
  "title": "Review: <PR title> (#<number>)",
  "items": [
    {
      "id": "finding-<N>",
      "title": "[<Priority>][<Principle>] <short title>",
      "body": "<full comment formatted per review-comment-template.md>",
      "metadata": {
        "file": "<file-path>",
        "line": "<line-number>",
        "priority": "<Blocker|Critical|Should Have|May Have|Nitpick|Question>",
        "principle": "<Correctness|Security|Performance|...>",
        "confidence": "<score>",
        "source": "<diff-only|full-context|both>"
      }
    }
  ]
}
```

Sort items by severity (Blocker first, Nitpick last).

#### Step 2: Launch TUI

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/tui/review.py .temp/interactive/pr-<number>/
```

The TUI auto-installs its dependency (`textual`) on first run. The user navigates the comment list, reads each finding in the detail pane, and marks each as:

- **Accept** (a): queue for posting as-is
- **Reject** (r): discard entirely
- **Edit** (e): mark for regeneration with a user-provided prompt

The user presses **Done** (d) when all items are marked.

#### Step 3: Process Results

Read `.temp/interactive/pr-<number>/results.json` and process:

- **`accepted`** → Post to source platform immediately (see Posting below)
- **`rejected`** → Discard. Do not post.
- **`edit`** → Regenerate the comment using the `prompt` field from results. Apply the same auto-validation to the regenerated comment.

#### Step 4: Edit Loop

If any results have `action: "edit"`:

1. Regenerate those comments based on each item's edit `prompt`
2. Re-run auto-validation on the regenerated comments
3. Write a **new** `items.json` containing only the regenerated items
4. Launch the TUI again (go back to Step 2)
5. Repeat until all items are either `accepted` or `rejected` — no `edit` items remain

#### Posting

**If MCP or API is available:**
- Post accepted comments through the matching MCP or API
- Resolve handled comments that were confirmed fixed
- Reopen or replace critical outdated comments that still apply

**If git-only fallback:**
- Write all accepted comments to `.temp/pr-review/pr-<number>-review.md` using the canonical comment template format
- Each comment includes the file path, line number, severity, and full comment body
- Inform the user: "Review saved to .temp/pr-review/pr-<number>-review.md — post these comments manually or re-run with the token configured."

#### Summary

After all rounds complete, display:

```text
## Review Summary

TUI rounds: N
Accepted: N
Rejected: N
Resolved old threads: N
Reopened critical threads: N
Auto-validation discarded: N
Output: [PR comments posted | Markdown saved to <path>]
```

---

## Follow-Up Flow (Re-Review)

Used when `mode=followup` or when auto-detection finds the current user has prior review comments on this PR.

### Phase 1: Build Previous Review Ledger

1. Read all existing review comments and their resolution state from the source MCP (or API fallback).
2. If `previous-review` is provided, also load that artifact and cross-reference its findings with the comment threads.
3. Build a ledger of every previous review comment with these fields:
   - comment ID and thread ID
   - original issue description
   - file and line reference
   - current resolution state (open, resolved, outdated)
   - author replies (if any)

### Phase 2: Re-Evaluate Each Comment

For each previous review comment in the ledger:

1. Read the current state of the referenced file and surrounding context (use branch checkout, not just the diff).
2. Check the commits since the last review for changes to the referenced area.
3. Classify the comment into one of these buckets:

   - **Addressed**: the code change fixes the issue. Queue for resolution.
   - **Partially addressed**: the fix is incomplete or introduces a related gap. Draft a follow-up comment describing the remaining issue.
   - **Not addressed**: the code is unchanged or the issue persists. Keep the comment open.
   - **Resolved but not fixed**: the comment was marked resolved on the platform but the underlying issue is still present. Queue for reopening with explanation.
   - **Obsolete**: the surrounding code was refactored in a way that makes the comment no longer applicable. Queue for resolution.

#### Reply Handling

When the PR author has replied to a review comment:

1. Read the reply in full context.
2. Evaluate the reply against the original concern:
   - **Explanation is valid**: the author's reasoning resolves the concern. Queue the comment for resolution with a brief acknowledgment.
   - **Explanation is insufficient**: the concern remains. Draft a follow-up reply explaining why the concern still applies.
   - **Explanation needs discussion**: the point is debatable. Present to the user with both sides for a decision.
3. Present each reply evaluation to the user:

```text
## Reply on Comment [N/total]

Original concern: <summary>
Author reply: <reply text>
Code state: [changed | unchanged]

Assessment: [Valid explanation | Insufficient | Needs discussion]
Reasoning: <why>

Action: [A]ccept resolution | [R]eply (draft provided) | [E]dit reply | [D]efer
```

#### Outdated Comment Validation

When a comment is marked outdated (file changed significantly):

1. Check if the underlying issue was actually fixed by the new code.
2. If the issue was fixed, resolve the comment.
3. If the issue was NOT fixed but merely moved (code relocated, refactored around the problem), post a new comment at the updated location referencing the original concern.
4. If the code area was deleted entirely, resolve as obsolete.

#### Code Movement Tracking

When code referenced by a comment has moved (file renamed, function extracted, block relocated):

1. Search the diff for the moved code using distinctive identifiers (function name, variable name, string literals from the original context).
2. If found at a new location, update the comment's file:line reference and re-evaluate the concern at the new location.
3. If the code was split across multiple locations (e.g., a function was extracted into multiple helpers), create one follow-up comment per location where the original concern still applies.
4. If the code was inlined or merged into another function, re-evaluate the concern in the new combined context — the issue may no longer apply or may manifest differently.

### Phase 3: Scan for New Issues

Run the standard review pipeline on the new commits and changed files:

1. Load coding guidelines via the `coding` skill.
2. Run Dual Diff Review on the new changes.
3. Launch child agents in parallel:
   - `code-reviewer` for correctness, security, performance
   - `repo-auditor` for architecture and boundaries
   - `doc-reviewer` for docs, naming, reviewer ergonomics
   - domain specialist for frontend, backend, or design-system concerns
4. Consolidate findings: deduplicate against previous comments, assign severity and confidence scores.
5. Filter out issues that duplicate already-open threads.
6. **Run Auto-Validation Phase** on all new findings.

### Phase 4: Interactive Summary

Present the full follow-up summary to the user before posting anything:

```text
## Follow-Up Review Summary

### Previous Comments
| Status              | Count |
|---------------------|-------|
| Addressed           |     N |
| Partially addressed |     N |
| Not addressed       |     N |
| Resolved but unfixed|     N |
| Obsolete            |     N |
| Replies evaluated   |     N |

### New Issues Found: N (after auto-validation)

[List each new issue with severity, file, and description]
```

Ask the user to confirm before proceeding to post. Allow the user to:

- Override any classification (e.g., mark something as addressed that was classified as not addressed).
- Edit any follow-up comment text before posting.
- Skip posting for specific items.

### Phase 5: Post and Resolve

After user confirmation:

1. **Addressed comments**: resolve the thread on the platform when supported. Post a brief acknowledgment reply (e.g., "Confirmed fixed in [commit-sha].").
2. **Partially addressed comments**: post a follow-up reply in the existing thread describing the remaining gap.
3. **Not addressed comments**: leave the thread open. Optionally post a gentle nudge if the user approves.
4. **Resolved but not fixed**: reopen the thread when the platform supports it, or post a new comment referencing the original thread and explaining why the issue persists.
5. **Obsolete comments**: resolve the thread with a note that the surrounding code was refactored.
6. **New issues**: post as new review comments through the matching MCP or API.

For git-only fallback, write all actions to the markdown report file instead.

---

## Standard Flow

Used when `mode=standard`.

1. Run the review pipeline: preflight, source handling, comment reconciliation, guideline loading, child agents.
2. Run Dual Diff Review.
3. Consolidate findings: deduplicate, assign severity and confidence scores.
4. Filter findings below the confidence threshold.
5. **Run Auto-Validation Phase.**
6. Post validated findings directly through the matching MCP or API (if `publish` includes source posting). For git-only fallback, write to markdown.
7. Produce the markdown review output.
8. Set PR status based on severity.

---

## PR Status Decision

After every review (fresh, follow-up, or standard), decide the PR status. This is a unified flow for all modes.

**Note:** PR status management is only available when MCP or API access is configured. In git-only fallback mode, include a status recommendation in the markdown output but do not attempt to set it.

### Step 1: Read Current Status

Check the current review status on the PR:
- What status has this reviewer previously set (if any)?
- What statuses have other reviewers set?
- Is the PR currently in draft?

### Step 2: Decide New Status

Apply this decision matrix based on the review outcome:

| Condition | Status | Action |
|-----------|--------|--------|
| Any accepted critical or high-severity findings remain unresolved | **Request Changes** | Set or keep |
| All previous comments addressed, no new critical/high findings | **Approve** | Set (remove existing Request Changes if set by this reviewer) |
| Only medium/low findings, nothing blocking | **Comment Only** | Optionally remove Request Changes if previously set by this reviewer |
| No findings at all, code looks good | **Approve** | Set |
| PR is in draft, findings are irrelevant until out of draft | **Comment Only** | Note draft status in summary |

### Step 3: Present and Confirm

Before setting the status, show the user:

```text
## PR Status

Current status: <current status set by this reviewer, or "none">
Other reviewers: <summary of other reviewers' statuses>
Recommended: <recommended status>
Reason: <brief explanation>

Set status? [Y]es | [C]hange to <alternative> | [S]kip (no status change)
```

### Step 4: Set Status

Use the source-native MCP or API fallback to submit the review status:

- GitHub MCP: `mcp__github__pull_request_review_write`
- GitHub API: `gh api repos/{owner}/{repo}/pulls/{number}/reviews -f event="APPROVE"` (or `REQUEST_CHANGES`, `COMMENT`)
- Bitbucket MCP: `mcp__bitbucket__approvePullRequest` or equivalent
- Bitbucket API: `curl -X POST` to the approve/unapprove endpoint

---

## Output

Always produce a markdown review with:

- severity-ordered findings
- confidence scores
- source tag (`[diff-only]`, `[full-context]`, `[both]`) per finding
- auto-validation summary
- open questions and assumptions
- summary of what was posted back to the PR (or saved to markdown)
- comment reconciliation summary covering carried-forward, resolved, reopened, and skipped threads

Display a final summary:

```text
## Review Complete

PR Status: [Approved | Request Changes | Comment Only | Skipped | N/A (git-only)]
Mode: [standard | interactive | followup (auto-detected)]
Access: [MCP | API fallback | git-only]

Auto-validation: N kept / M discarded
Resolved threads: N
Reopened threads: N
New comments posted: N
Threads left open: N
Replies evaluated: N
Output: [PR comments | Markdown at <path>]
Worktree: [cleaned up | retained for follow-up]
```

After displaying the summary, clean up the worktree:

```bash
git worktree remove .temp/worktrees/pr-<number> 2>/dev/null || true
```

If the user may want to do a follow-up review soon, ask before cleanup.
