---
title: "code-review-fix"
description: Fix PR review comments — read comments, apply code fixes, reply to reviewers, mark threads resolved
skill_name: code-review-fix
category: task
workflow_tier: full
user_invocable: true
---

# code-review-fix

The "fix" counterpart to `/adk:code-review-pr`. Reads review comments on a PR, applies code fixes, replies to reviewers explaining what changed, and marks threads resolved. Supports GitHub and Bitbucket PRs with severity filtering and dry-run mode.

## When to Use

- Fix unresolved review comments on a pull request
- Address reviewer feedback systematically across all threads
- Batch-fix blocking or critical comments before re-review
- Preview what fixes would be applied without making changes (dry-run)
- Reply to reviewers with concise explanations of fixes
- Push back on incorrect review comments with technical evidence

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<pr-url>` | PR URL (GitHub or Bitbucket) | required | The PR whose review comments to fix |
| `--auto` | flag | off | Skip confirmations, fix all fixable comments automatically |
| `--filter` | `blocker` \| `critical` \| `all` | `all` | Only address comments at or above the specified severity |
| `--dry-run` | flag | off | Show what would be fixed without making changes |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Default** | Reads all unresolved comments, presents fix plan, executes with human approval per comment |
| `--auto` | Skips Phase 0-2 confirmations, fixes all fixable comments, replies and resolves automatically |
| `--dry-run` | Runs full analysis but produces a plan only — no code changes, no replies posted |
| `--filter blocker` | Only addresses comments marked as blocking or must-fix |
| `--filter critical` | Addresses blocker + critical severity comments |
| `--filter all` | Addresses all unresolved comments (default) |

## Priorities

Comments are categorized by **severity** and **type** before fixing:

**By severity** (in processing order):
1. **Blocker** — must fix before merge
2. **Critical** — strongly recommended fix
3. **Suggestion** — optional improvement
4. **Nitpick** — style or preference
5. **Question** — needs clarification, not a fix

**By type** (determines action):
1. **Code-fix** — direct code change needed
2. **Design-change** — architectural or design refactor
3. **Test-addition** — missing test coverage
4. **Doc-update** — documentation or comment change
5. **Discussion** — needs conversation, not a code change

## Key Behaviors

- **Verify before implementing**: checks each comment against the codebase before acting
- **No performative agreement**: states the fix or pushes back with technical reasoning — never "Great point!"
- **YAGNI checks**: if a reviewer suggests over-engineering, checks actual usage first
- **Technical correctness over social comfort**: pushes back when the comment is wrong, with evidence
- **Batch operations**: user can say "fix all remaining", "skip remaining", or "fix all in \<file\>"
- **Fix plan approval**: presents categorized plan (Will Fix / Needs Discussion / Will Skip) before executing
- **Concise replies**: posts thread replies like "Fixed. Added null check before accessing `user.preferences`."

## Workflow

Follows the full 6-phase workflow.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm which PR, which comments to address (all, blockers only, specific threads) |
| 1. Research & Options | yes | Read all unresolved comments, categorize by severity and type |
| 2. Approach Selection | yes | Present the fix plan — which comments will be fixed, how, and which need discussion |
| 3. Planning | yes | Plan fix order: dependencies between fixes, group by file |
| 4. Execute | yes | Apply fixes, reply to comments, mark resolved |
| 5. Validate & Learn | yes | Run tests/linting, produce summary of fixed vs needs-discussion |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect source, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `review-standards` | always | Review pipeline and canonical comment template |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |
| `github` | target is GitHub | PR details, diff, comments, thread resolution via `gh` CLI |
| `bitbucket` | target is Bitbucket | PR details, diff, comments, tasks via REST API |

## Output Format

Produces a fix summary with these sections:

- **Fixed**: count and table of applied fixes with file, line, description, and test status
- **Replied (pushback)**: comments where the current implementation was kept with technical reasoning
- **Needs discussion**: comments requiring design conversation
- **Skipped**: already resolved or no-action-needed comments
- **Validation**: test suite results, lint status, type-check status
- **Needs Follow-Up**: comments requiring further discussion with reviewer references

When `--dry-run` is set, produces the same summary with "Would fix" instead of "Fixed", and no code changes or replies posted.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:code-review-pr` | Perform the review that generates the comments |
| `/adk:dev-build` | More complex changes that go beyond comment-level fixes |
| `/adk:coding` | Load repo-specific coding guidelines directly |

## Examples

```
/adk:code-review-fix https://github.com/org/repo/pull/42
/adk:code-review-fix https://github.com/org/repo/pull/42 --auto
/adk:code-review-fix https://github.com/org/repo/pull/42 --filter blocker
/adk:code-review-fix https://github.com/org/repo/pull/42 --dry-run
/adk:code-review-fix https://bitbucket.org/workspace/repo/pull-requests/15
```
