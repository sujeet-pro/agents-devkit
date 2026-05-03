---
title: 'adk-review:review-feedback'
description: '  Triage existing reviewer comments on a GitHub PR and address each in code with traceable per-comment replies (commit SHA + one-line summary). Different from `review-pr --fix`: this skill ASSUMES the comments are already valid feedback and does NOT re-perform a full review pass. Classifies each comment as `apply-as-stated`, `apply-with-modification`, `discuss-not-fix`, `wont-fix`, or `already-resolved`. Under `--fix`, edits the code, runs repo-native validation, pushes (asks first; never force, never to protected branches), posts replies (with post-confirmation), and resolves only after reply confirms. Use when the user says "address the PR comments", "fix the review feedback", "go through reviewer comments and apply changes". Do NOT use to discover new issues (use `review-pr`), self-review your changes (use `review-code-changes`), or capture a session handoff (use `review-handoff`).'
plugin: 'adk-review'
skill: 'review-feedback'
source: 'plugins/adk-review/skills/review-feedback/SKILL.md'
group: 'review-skills'
order: 2104
---
# adk-review:review-feedback

## Source

`plugins/adk-review/skills/review-feedback/SKILL.md`

## Skill Body

# `review-feedback` — address existing reviewer comments

Triage existing reviewer comments on a PR. Classify each. Apply, push, reply, resolve. Different from `review-pr --fix`: this skill ASSUMES the comments are valid feedback; it does NOT re-perform a full review pass.

## When to use

- "address the PR comments on <url>"
- "fix the review feedback"
- "go through reviewer comments and apply"
- "respond to PR comments"
- "resolve the review threads"

## When NOT to use

- Discover new issues / fresh review pass → `/adk-review:review-pr`.
- Self-review of local changes (no PR yet) → `/adk-review:review-code-changes`.
- Just want to draft replies without applying → `/adk-review:review-pr` in `own-PR` mode.
- Whole-repo audit → `/adk-review:audit-repo`.

## Common prompts (auto-route triggers)

| Prompt pattern | Default flags |
| --- | --- |
| `"address the PR comments"` | `--fix` (apply + push + reply) |
| `"fix the review feedback"` | `--fix` |
| `"go through reviewer comments and apply"` | `--fix` |
| `"respond to PR comments"` | `--fix` (default; without `--fix` it just drafts replies) |
| `"triage the review comments"` | `--auto` (no `--fix`) — classification only |
| `"walk through the comments with me"` | `-i` |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<pr-url-or-number>` | yes | inferred from current branch's open PR if omitted |
| `--auto` | optional | yes (default mode) |
| `-i` / `--interactive` | optional | mutually exclusive with `--auto` |
| `--fix` | optional | RECOMMENDED default for this skill (the whole point is to address); without `--fix`, only classifies + drafts replies |
| `--scope <comment-id-list>` | optional | restrict to a subset of comments by ID |

## Workflow

```
Phase 0 — prompt expand
  - Resolve PR URL / number (or current branch's open PR).
  - From repos.md: locate the local checkout (or git worktree add to .temp/...).
  - Slug from PR title.

Phase 1 — preflight
  - github MCP reachable OR gh CLI authed.
  - For --fix: working tree clean; not on protected branch; have push permission.
  - bin/adk-info github --check + bin/adk-info repos --check.

Phase 2 — fetch all reviewer comments
  - Inline comments + replies + threads (resolved state).
  - Issue comments (top-level review bodies).
  - PR head SHA + base ref.
  - Apply --scope <comment-id-list> filter if provided.

Phase 3 — classify each comment (per references/classification.md)
  - For each open comment / unresolved thread:
    - apply-as-stated     (clear actionable; we agree)
    - apply-with-modification (clear actionable; better fix exists)
    - discuss-not-fix     (architectural; needs in-person or async discussion)
    - wont-fix            (we disagree with reasoning)
    - already-resolved    (the underlying issue is no longer in the code)
  - Group comments by file / line / theme so a single fix addresses multiple comments where applicable.

Phase 4 — propose
  - Show the classification table; counts per category.
  - For -i: walk each, allow user to re-classify.
  - For --auto: keep the classification as-is.

Phase 5a — draft replies (always)
  - For each classification, draft a reply per references/reply-templates.md
    (apply-stated, apply-modified, discuss, wont-fix, already-resolved).
  - Write .temp/task-<slug>/feedback/replies-draft.md.

Phase 5b — apply (--fix only)
  - For apply-* classifications: edit code (delegate non-trivial to /adk-code:code-bugfix).
  - Validate via repo-native tests / typecheck / lint.
  - Commit per comment (preferred) or one squashable commit.

Phase 5c — push (--fix only)
  - PUSH-GATE: ask before the first push of the session, even under --auto --fix.
  - Push to PR head branch. NEVER --force. NEVER protected.

Phase 5d — post replies + resolve
  - Post each reply via gh / MCP. Capture receipt IDs.
  - POST-CONFIRMATION (per /adk-review:review-pr references/post-confirmation.md):
    wait 5s → re-fetch → confirm IDs reappear; retry at 10s, 20s; never re-post.
  - For each addressed (apply-*) comment: mark thread resolved AFTER reply confirmed.
  - For discuss-not-fix / wont-fix / already-resolved: post reply but DO NOT resolve (let the reviewer click).

Phase 6 — report
  - .temp/task-<slug>/feedback/classification.md
  - .temp/task-<slug>/feedback/replies-postback.md
  - .temp/task-<slug>/feedback/fix-log.md (if --fix)
  - .temp/task-<slug>/report.md
```

See `references/workflow.md` for stage detail and `references/how-it-works.md` for diagrams.

## Persona

> Take the feedback at face value. Don't re-litigate the design. If you genuinely disagree, write the disagreement as a `wont-fix` reply with concrete reasoning; don't ignore. If you partially agree, write `apply-with-modification`. Don't bulk-resolve without per-comment replies — reviewers can't tell what you changed. Every addressed comment gets a reply quoting the commit SHA.

See `references/persona.md`.

## Constitution

**Must do:**

1. Reply to every addressed comment with the commit SHA + a one-line summary of what changed.
2. Only resolve a thread AFTER the reply is post-confirmed (same protocol as `review-pr`).
3. Group related comments so a single fix addresses multiple where applicable; reply on each.
4. Honor the universal post-confirmation re-fetch (5/10/20s retry budget; never re-post on miss).
5. Use the canonical reply templates from `references/reply-templates.md`.
6. For `wont-fix`: state concrete reasoning + offer to discuss in-person.
7. For `discuss-not-fix`: link a follow-up (Jira ticket / sync invite / DM) — don't leave it as a void.

**Must not do:**

1. Re-perform a full review pass. That's `/adk-review:review-pr`.
2. Bulk-resolve without per-comment replies. The reviewer can't tell what changed.
3. Resolve a `discuss-not-fix` or `wont-fix` thread (those stay open for the reviewer to either accept or counter).
4. Push under `--fix` without the push-gate (asks first, even under `--auto --fix`).
5. Force-push to protected branches (per `~/.config/adk/github.md.forbid_force_push_branches`).
6. `gh pr merge` — never. Even under `--auto --fix`.
7. Re-post a reply on a propagation miss — the post-confirmation protocol forbids it.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Bulk-resolving comments without per-comment replies.
- "Wont-fix" with no reasoning.
- Missing the commit SHA in the `apply-as-stated` reply.
- Re-litigating the design in a thread when an in-person discussion would resolve it in 5 minutes.
- Re-perform a full review pass (that's `review-pr`'s job).
- Resolving a thread before the reply post-confirms.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/feedback/classification.md` | Per-comment classification table |
| `.temp/task-<slug>/feedback/replies-draft.md` | Drafted replies before posting |
| `.temp/task-<slug>/feedback/replies-postback.md` | Per-reply receipt + confirmation timing |
| `.temp/task-<slug>/feedback/fix-log.md` | (`--fix` only) per-comment fix commit + validation |
| `.temp/task-<slug>/report.md` | Executive summary |

See `references/output-format.md` and `references/artifact-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Take-feedback-at-face-value persona + status banner + posture |
| `references/workflow.md` | Detailed Phase 0-6 stage list with checkpoints |
| `references/modes.md` | What `--auto` / `-i` / `--fix` mean for `review-feedback` |
| `references/interaction-contract.md` | Canonical interaction contract (mirrored byte-identical from adk-core) |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 3-4 worked examples (apply-only, mixed, wont-fix-heavy, partial-apply) |
| `references/output-format.md` | classification.md / replies-draft.md / fix-log.md / report.md shapes |
| `references/artifact-format.md` | `.temp/task-<slug>/feedback/*` canonical paths |
| `references/validator.md` | Per-phase gates (especially the post-confirmation + resolve-after-confirm rule) |
| `references/how-it-works.md` | Mermaid: phase flow, classification fan-out, --fix loop, post-confirmation |
| `references/clarifying-questions.md` | Under -i; defaults under --auto |
| `references/classification.md` | The 5-state classification rubric (apply-as-stated / apply-with-modification / discuss-not-fix / wont-fix / already-resolved) with examples |
| `references/reply-templates.md` | The 5 canonical reply templates |
| `references/comment-grouping.md` | How to group related comments so one fix addresses many |

## Additional links

- `/adk-review:review-pr` `references/post-confirmation.md` — the canonical post-confirmation protocol used here.
- `/adk-review:review-pr` `references/pr-mcp-fallback.md` — the github MCP / gh CLI decision matrix.
- `/adk-review:review-pr` `references/pr-comment-reconciliation.md` — the same classification states (`still-open`, etc.) used by review-pr's reconciliation phase.
- The repo's `AGENTS.md` / `CLAUDE.md` / `.cursorrules` — for repo-specific tone in replies.
