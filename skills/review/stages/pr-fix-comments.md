# PR Fix Comments Stage

Read review comments on a PR you authored, evaluate validity, and fix or reply with human-in-the-loop per comment.

---

## Core Principles

These principles govern how review feedback is handled:

- **Verify before implementing.** Check each comment against the codebase before acting.
- **No performative agreement.** Never respond with "Great point!" or "You're absolutely right!" -- state the fix or push back with technical reasoning.
- **YAGNI checks.** If a reviewer suggests "implementing properly" for something unused, check actual usage first.
- **Technical correctness over social comfort.** Push back when the comment is wrong, with evidence.

---

## Guideline Loading

Invoke the `coding` skill to load relevant coding guidelines. Use these guidelines when evaluating whether a review comment is technically valid.

---

## Workflow

### Step 1: Read All Review Comments

Read all review comments from the PR via source MCP or API fallback. Include thread replies and resolution state.

### Step 2: Categorize Comments

- By reviewer (human partner vs external reviewer)
- By severity (blocking, important, minor, nitpick)
- By state (open, resolved, outdated)
- Filter to unresolved comments only.

### Step 3: Human-in-the-Loop Per Comment

Present each unresolved comment:

```text
## Comment [N/total] from @reviewer

File: path/to/file.ext:LINE
Thread: <has replies: yes/no>

Comment:
<full comment text>

<If thread has replies, show them>

Assessment: [Valid -- fix needed | Debatable | Incorrect | Already fixed | Needs clarification]
Reasoning: <technical explanation of the assessment>
Suggested action: <what to do>

Action: [F]ix | [R]eply (push back) | [A]gree & reply (will address later) | [S]kip | [D]efer
```

### Step 4: Execute Actions

**Fix**: Implement the change.
- Make the code change.
- Run tests on affected files.
- If tests pass, reply in-thread: "Fixed in [commit-sha]."
- If tests fail, report the failure and ask for guidance.

**Reply (push back)**: Draft a pushback response.
- Draft a technically grounded reply explaining why the comment doesn't apply.
- Show the draft to the user for editing before posting.
- Post as a reply in the comment thread (not a top-level PR comment).

**Agree & reply**: Acknowledge without fixing now.
- Draft a reply like "Valid point. Will address in a follow-up PR / next iteration."
- Let the user edit before posting.

**Skip**: Move on without action. Return to skipped items at the end.

**Defer**: Mark for later. Don't revisit in this session.

### Step 5: Batch Operations

At any point the user can say:
- "Fix all valid" -> implement all comments assessed as valid
- "Reply to all debatable" -> draft pushback replies for all debatable comments
- "Skip remaining" -> skip all unprocessed comments

### Step 6: Verification

After all fixes are applied:
- Run the full test suite.
- Run linter and type-checker.
- Report results. If failures, identify which fix caused the failure.

### Step 7: Thread Replies

Always reply within the comment thread using `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`. Never post as a top-level PR comment.

---

## Handling Unclear Feedback

If any comment is unclear:
- Do not implement it.
- Ask for clarification by replying in-thread.
- If multiple comments are unclear, clarify all unclear items before implementing any of them (they may be related).

---

## Source-Specific Handling

**From your human partner:**
- Trusted -- implement after understanding
- Still ask if scope is unclear
- Skip to action or technical acknowledgment

**From external reviewers:**
1. Check: technically correct for THIS codebase?
2. Check: breaks existing functionality?
3. Check: reason for current implementation?
4. Check: works on all platforms/versions?
5. Check: does reviewer understand full context?

If a suggestion conflicts with your human partner's prior decisions, stop and discuss with your human partner first.

---

## Post-Fix Summary

```text
## Fix Summary

Fixed: N comments
Replied (pushback): N comments
Agreed (deferred): N comments
Skipped: N comments
Clarification requested: N comments

Verification:
- Tests: <pass/fail>
- Lint: <clean/issues>
- Types: <clean/issues>
```
