---
name: adk-code-review-fix
description: "adk - [full] [code-review] Fix PR review comments — reads comments, applies code fixes, replies to reviewers, marks threads resolved."
user-invocable: true
argument-hint: "<pr-url> [--auto] [--filter blocker|critical|all] [--dry-run]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
  mcp-servers: [detect-from-input]
workflow-tier: full
---

# Review Fixes

This skill is the "fix" counterpart to `/adk:code-review-pr`. You've received review comments on a PR — this skill reads them, applies code fixes, replies to reviewers explaining what changed, and marks threads resolved.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. Cross-platform markdown safe for GitHub + Bitbucket. |
| `/adk:review-standards` | always (review skills) | Pipeline: intake → ingestion → parallel review → consolidation → output → postback. Canonical comment template with severity, confidence, concern, depth, dimension, guideline. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |
| `/adk:github` | when target is GitHub | GitHub operations via `gh` CLI — PR details, diff, reviews, comments, thread resolution. Validates `gh` install and auth. |
| `/adk:bitbucket` | when target is Bitbucket | Bitbucket REST API via `curl` — PR details, diff, comments, tasks. Uses `BITBUCKET_USERNAME`+`BITBUCKET_TOKEN` from `~/.zshenv`. |

Core principles:
- **Verify before implementing.** Check each comment against the codebase before acting.
- **No performative agreement.** State the fix or push back with technical reasoning — never "Great point!"
- **YAGNI checks.** If a reviewer suggests over-engineering, check actual usage first.
- **Technical correctness over social comfort.** Push back when the comment is wrong, with evidence.

---

## Reference Loading

Load reference files conditionally to minimize token usage:

| Reference | Load When |
|-----------|-----------|
| `workflow-6phase.md` | always (read only the section for the current phase) |
| `communication-style.md` | always |
| `preflight.md` | before preflight check |
| `output-formats.md` | when producing final output |
| `output-format-modes.md` | when producing final output |
| `principal-engineer.md` | Phase 0, complexity >= medium |
| `agentic-teams.md` | Phase 4, when launching child agents |
| `inline-interaction.md` | interactive phases, NOT --auto |
| `help-format.md` | when --help is passed |
| `project-guidelines.md` | Phase 1, when scanning project |
| `review-pipeline.md` | review skills only |
| `review-comment-template.md` | when posting review comments |
| `source-routing.md` | when target is external (PR, Confluence, Google Docs) |

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<pr-url>` | PR URL (GitHub or Bitbucket) | required | The PR whose review comments to fix |
| `--auto` | flag | off | Skip confirmations, fix all fixable comments automatically |
| `--filter` | `blocker`, `critical`, `all` | `all` | Only address comments at or above the specified severity |
| `--dry-run` | flag | off | Show what would be fixed without making changes |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | -- | -- | Show this help section and exit |

### Behavior Variations

- **Default**: reads all unresolved comments, presents fix plan, executes with human approval per comment
- **`--auto`**: skips Phase 0-2 confirmations, fixes all fixable comments, replies and resolves automatically
- **`--dry-run`**: runs full analysis but produces a plan only — no code changes, no replies posted
- **`--filter blocker`**: only addresses comments marked as blocking or must-fix
- **`--filter critical`**: addresses blocker + critical severity comments
- **`--filter all`**: addresses all unresolved comments (default)

### Examples

```
/adk:code-review-fix https://github.com/org/repo/pull/42
/adk:code-review-fix https://github.com/org/repo/pull/42 --auto
/adk:code-review-fix https://github.com/org/repo/pull/42 --filter blocker
/adk:code-review-fix https://github.com/org/repo/pull/42 --dry-run
/adk:code-review-fix https://bitbucket.org/workspace/repo/pull-requests/15
```

---

## Preflight & MCP Resolution

Before reading the PR or launching child agents, attempt MCP-first, then fall back gracefully.

### Step 1: Detect Provider

Detect GitHub or Bitbucket from:
- The PR URL (required argument)
- The git remote origin (`git remote get-url origin`)

### Step 2: Check MCP

Run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR} pr=<pr-url>`

Then do one lightweight read through the matching source-native MCP to confirm it is connected:

- GitHub -> `mcp__github__*`
- Bitbucket -> `mcp__bitbucket__*`

### Step 3: MCP Fallback — Direct API or Git

If the MCP is **not configured** or the connectivity check fails, fall back in this order:

#### 3a. Direct API via CLI

Check for the required token in `~/.zshenv`:

- **GitHub**: `GITHUB_PAT` — use `gh` CLI or `curl` with the GitHub REST API
- **Bitbucket**: `BITBUCKET_USERNAME` + `BITBUCKET_TOKEN` — use `curl` with the Bitbucket REST API

Read the token:

```bash
grep '^export GITHUB_PAT=' ~/.zshenv | sed 's/^export GITHUB_PAT=//' | tr -d '"'"'"
```

If the token exists, proceed with API-based workflow.

**GitHub API commands:**

```bash
# PR review comments (unresolved threads)
gh api repos/{owner}/{repo}/pulls/{number}/comments

# Reply to a comment thread
gh api repos/{owner}/{repo}/pulls/{number}/comments/{id}/replies -f body="..."

# PR diff
gh pr diff <number>
```

**Bitbucket API commands:**

```bash
# PR comments
curl -s -u "${BITBUCKET_USERNAME}:${BITBUCKET_TOKEN}" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments"
```

#### 3b. Git-Only Fallback (No Token Available)

If no token is found:

1. **Tell the user** which token is missing and ask them to add it.
2. In git-only mode, this skill cannot read or reply to PR comments. Inform the user and suggest they configure the token or MCP, then re-run.

---

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm which PR, which comments to address (all, blockers only, specific threads) |
| 1. Research & Options | yes | Read all unresolved comments, categorize by severity and type |
| 2. Approach Selection | yes | Present the fix plan — which comments will be fixed, how, and which need discussion |
| 3. Planning | yes | Plan fix order: dependencies between fixes, group by file |
| 4. Execute | yes | Apply fixes, reply to comments, mark resolved |
| 5. Validate & Learn | yes | Run tests/linting, produce summary of fixed vs needs-discussion |

---

## Phase 0: Confirm Scope

Confirm with the user:

1. **Which PR** to process (from the provided URL)
2. **Which comments** to address:
   - All unresolved (default)
   - Blockers only (`--filter blocker`)
   - Critical and above (`--filter critical`)
   - Specific threads (user can list comment IDs or quote text)
3. **Behavior**: fix and reply, or dry-run

In `--auto` mode, skip confirmation: process all unresolved comments matching the filter.

---

## Phase 1: Read & Categorize Comments

### Step 1: Read All Review Comments

Read all review comments from the PR via source MCP or API fallback. Include thread replies and resolution state.

### Step 2: Categorize Each Comment

By **severity**:
- `blocker` — must fix before merge
- `critical` — strongly recommended fix
- `suggestion` — optional improvement
- `nitpick` — style or preference
- `question` — needs clarification, not a fix

By **type**:
- `code-fix` — direct code change needed
- `design-change` — architectural or design refactor
- `test-addition` — missing test coverage
- `doc-update` — documentation or comment change
- `discussion` — needs conversation, not a code change

### Step 3: Filter

Apply `--filter` to remove comments below the severity threshold.

### Guideline Loading

Invoke `/adk:coding` to detect the repo stack and load matching coding guidelines. Use these guidelines when evaluating comment validity and implementing fixes.

---

## Phase 2: Fix Plan

Present the categorized comments and proposed actions:

```text
## Fix Plan for PR #<number>

### Will Fix (N comments)
| # | File | Line | Reviewer | Severity | Type | Proposed Fix |
|---|------|------|----------|----------|------|-------------|
| 1 | src/auth.ts | 47 | @reviewer | blocker | code-fix | Add null check before access |
| 2 | src/api.ts | 102 | @reviewer | critical | code-fix | Switch to parameterized query |

### Needs Discussion (N comments)
| # | File | Line | Reviewer | Severity | Type | Reason |
|---|------|------|----------|----------|------|--------|
| 3 | src/db.ts | 88 | @reviewer | suggestion | design-change | Conflicts with existing pattern |

### Will Skip (N comments)
| # | Reason |
|---|--------|
| 4 | Already resolved |
| 5 | Nitpick, no code change needed |

Approve? [Y]es / [E]dit plan / [C]ancel
```

The user can:
- Approve the full plan
- Move comments between categories (e.g., skip a blocker, force-fix a discussion item)
- Cancel and exit

In `--auto` mode, skip this confirmation. Fix all "Will Fix" items, skip "Needs Discussion" and "Will Skip".

---

## Phase 3: Fix Order

Plan the execution order:

1. **Group by file** — minimize context switching
2. **Dependency order** — if fix B depends on fix A, do A first
3. **Severity order within groups** — blockers first, then critical, then suggestions
4. **Test additions last** — after the code they test is already fixed

---

## Phase 4: Execute Fixes

For each fix in the planned order:

### Step 1: Apply the Code Change

- Read the current file content around the comment location
- Implement the fix per the coding guidelines
- Verify the fix addresses the reviewer's concern

### Step 2: Reply to the Comment

Post a reply in the comment thread (never a top-level PR comment):

**Reply format** (concise, states what changed and why):
```text
Fixed. <one-sentence description of what changed>.
```

Examples:
- "Fixed. Added null check before accessing `user.preferences` — returns early with 400 if missing."
- "Fixed. Switched to parameterized query to prevent SQL injection."
- "Addressed. Added unit test for the edge case where `items` is empty."

For pushback (when the comment is incorrect):
```text
Keeping current implementation. <technical reasoning with evidence>.
```

### Step 3: Mark Resolved

After posting the reply, mark the thread as resolved via MCP or API if the platform supports it.

### Batch Operations

At any point the user can say:
- "Fix all remaining" — implement all remaining planned fixes
- "Skip remaining" — skip all unprocessed comments
- "Fix all in <file>" — fix all comments in a specific file

---

## Phase 5: Validate & Summarize

### Validation

After all fixes are applied:

1. Run the test suite
2. Run linter and type-checker
3. If failures occur, identify which fix caused the failure and offer to revert or adjust

### Summary

```text
## Fix Summary for PR #<number>

Fixed: N comments
Replied (pushback): N comments
Needs discussion: N comments
Skipped: N comments

### Fixes Applied
| # | File | Line | Fix Description | Status |
|---|------|------|-----------------|--------|
| 1 | src/auth.ts | 47 | Added null check | tests pass |
| 2 | src/api.ts | 102 | Parameterized query | tests pass |

### Validation
- Tests: pass/fail (N passed, N failed)
- Lint: clean/N issues
- Types: clean/N issues

### Needs Follow-Up
- Comment #3 from @reviewer on src/db.ts:88 — needs design discussion
```

### Dry-Run Output

When `--dry-run` is set, produce the same summary but with "Would fix" instead of "Fixed", and no code changes or replies posted.

---

## Adjacent Skills

- `/adk:code-review-pr` for performing the review that generates the comments
- `/adk:dev-build` for more complex changes that go beyond comment-level fixes
- `/adk:coding` for loading repo-specific coding guidelines
