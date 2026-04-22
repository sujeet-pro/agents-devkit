---
title: 'review-feedback'
description: 'Triage existing PR review comments, address each in code with traceable replies, and produce a single response summary.'
artifact_kind: skill
skill_name: review-feedback
category: review
---
# review-feedback

Triage existing PR review comments, address each in code with traceable replies, and produce a single response summary. Use when reviewer comments already exist on a PR (GitHub or Bitbucket) and the goal is to act on them - apply changes, push back with rationale, or accept and defer - while keeping every comment thread answered. Do not use to author the original review (use adk-review-pr) or to review your own local changes (use adk-review-local).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-review-feedback` form via `agents-skills/`.

```text
/adk:review-feedback            # interactive run (Claude Code)
/adk:review-feedback --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-review-feedback` (resolved through the
`agents-skills/adk-review-feedback/` symlink).

## Source

Direct from `skills/review-feedback/SKILL.md` — this page is auto-generated.

Standalone task skill under the `@adk:review` (a.k.a. `adk-review`) category router. Walks every reviewer comment, classifies it, addresses it in code or with a reply, and produces a single response summary with traceability.

## When to use

- A remote PR has reviewer comments that must be addressed.
- The goal is to act on each comment and reply, not just read.
- A respond-and-iterate loop is expected before merge.

## When NOT to use

- No reviewer comments yet -> `@adk:review-pr` (a.k.a. `adk-review-pr`) (to author them) or `@adk:review-local` (a.k.a. `adk-review-local`) (to self-review)
- Comments are on a doc, not a PR -> `@adk:docs-review` (a.k.a. `adk-docs-review`) cycle
- Comments belong to a different PR you do not own; nothing to address

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<pr-url>` | yes | Full PR URL (provider auto-detected) |
| `<filter>` | optional | `unresolved` (default) / `all` / `since:<sha>` |
| `<scope>` | optional | Path filter for which comments to act on |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Confirm intent** - restate PR, filter, scope. Approval gate unless `--auto`.
2. **Fetch comments** - pull every comment in the filter set with file path, line, author, body, thread state. Use `gh api` / Bitbucket REST / appropriate MCP.
3. **Classify** - assign each comment a class:
   - `Apply`: agree, change code.
   - `Discuss`: need more info from the reviewer.
   - `Defer`: valid but out of scope; create a follow-up.
   - `Decline`: disagree with rationale.
   - `Already-fixed`: change has already been made; just point to the diff.
4. **Plan changes** - for each `Apply`, list the file edit. For each `Defer`, draft the follow-up issue or task line. Approval gate unless `--auto`.
5. **Execute** - apply edits in dependency order. Group by file; commit per logical group.
6. **Validate** - run repo-native checks (tests / lint / type-check) on changed files.
7. **Reply** - draft one reply per comment that:
   - states the class (`Applied`, `Discussing`, `Deferring`, `Declining`, `Already fixed`),
   - links to the commit / line / follow-up,
   - explains the reasoning when not `Applied`.
8. **Post** - approval gate unless `--auto`; then post replies to each thread plus a single summary comment.

## Reply templates

```markdown
**Applied** in <commit-sha> (`path/to/file.ts:LINE`).
<one-sentence note if useful>
```

```markdown
**Already fixed** in <commit-sha> (`path/to/file.ts:LINE`) - thanks for catching it.
```

```markdown
**Deferring** to follow-up <issue-or-link>.
Reason: <one sentence - why it is out of scope here>.
```

```markdown
**Declining** with rationale:
<2-3 sentences>
Happy to revisit if <condition>.
```

```markdown
**Discussing** - <follow-up question>
Ping me when you have a chance.
```

## Summary comment template

Posted once at the end, separate from inline replies:

```markdown
## Feedback addressed
- Applied: <count>
- Already fixed: <count>
- Deferred: <count> (links: <list>)
- Declined: <count>
- Discussing: <count>

Latest validation: `<command>` PASS

Re-request review when ready.
```

## Output format

```
## Feedback Triage: <PR title> (#<number>)
- URL: <pr-url>
- Comments processed: <N>

## Classification
| File | Line | Author | Class | Action |
| --- | --- | --- | --- | --- |
| `src/foo.ts` | 42 | @alice | Apply | Edit + reply |
| `src/bar.ts` | 17 | @bob | Decline | Reply with rationale |

## Changed Files
- `path/to/file.ts` - <one-line description>

## Validation
<command output, or explicit "not verified" with reason>

## Replies
- <count> inline replies drafted
- 1 summary comment drafted

Ready to post (or already posted if --auto)?
```

## Hard rules

- Every comment in the filter set gets exactly one reply class.
- Replies link to a commit SHA, file:line, or follow-up - never bare assertions.
- `Decline` requires rationale; `Defer` requires a follow-up link or task.
- Validation runs before replies are posted.
- No bulk "addressed all comments" replies; each thread gets its own.

## Anti-patterns

- Replying "done" without a commit link.
- Quietly applying some comments and ignoring others.
- Re-requesting review before validation runs.
- Bundling new feature work into the feedback pass. Defer it.
- Silently force-pushing in a way that detaches existing review comments.

## Examples

```
adk-review-feedback https://github.com/org/repo/pull/842
```

```
adk-review-feedback https://bitbucket.org/org/repo/pull-requests/17 --filter unresolved --scope src/
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/review-feedback-clarifying-questions.md`) and reports the choices.

1. **What is the PR URL?** — _How to pick:_ Required. Provider auto-detected from host.
2. **Filter: address all, only Blockers/Critical, or only specific comment IDs?** — _How to pick:_ All = default. Severity-only = use when many comments and we want to ship core fixes first. Specific IDs = surgical follow-up.
3. **Reply style: terse ('Fixed in <sha>') or explanatory (one-paragraph 'why this fix')?** — _How to pick:_ Terse for nits, explanatory for design comments and pushbacks.

**Default report:** Comment-by-comment table (id / severity / status / fix commit / reply preview).

**Detailed report (on request or `--verbose`):** Add: per-comment plan before fix, evidence each fix actually addresses the issue, residual disagreement notes.

**Artifact:** `feedback-resolution-comments` — PR replies + commits. Plan + evidence in .temp/.

**Artifact path:** .temp/reports/feedback-<provider>-<number>.md (resolution log). Replies + commits land on the remote PR.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/review-feedback-clarifying-questions.md`) and reports the choices.

1. **What is the PR URL?** — _How to pick:_ Required. Provider auto-detected from host.
2. **Filter: address all, only Blockers/Critical, or only specific comment IDs?** — _How to pick:_ All = default. Severity-only = use when many comments and we want to ship core fixes first. Specific IDs = surgical follow-up.
3. **Reply style: terse ('Fixed in <sha>') or explanatory (one-paragraph 'why this fix')?** — _How to pick:_ Terse for nits, explanatory for design comments and pushbacks.

## Default vs detailed output

**Default report:** Comment-by-comment table (id / severity / status / fix commit / reply preview).

**Detailed report (on request or `--verbose`):** Add: per-comment plan before fix, evidence each fix actually addresses the issue, residual disagreement notes.

**Artifact:** `feedback-resolution-comments` — PR replies + commits. Plan + evidence in .temp/.

**Artifact path:** .temp/reports/feedback-<provider>-<number>.md (resolution log). Replies + commits land on the remote PR.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/review-feedback-anti-patterns.md` | Things to avoid when running this skill. |
| `references/review-feedback-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/review-feedback-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/review-feedback-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/review-feedback-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/review-feedback-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/review-feedback-persona.md` | The agent persona that drives this skill. |
| `references/review-feedback-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/review-feedback-review-comment-format.md` | Standard finding format with stable IDs and severities. |
| `references/review-feedback-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->


## Related skills

- [`docs-review`](./skill-docs-review.md) — `@adk:docs-review` (a.k.a. `adk-docs-review`)
- [`review`](./skill-review.md) — `@adk:review` (a.k.a. `adk-review`)
- [`review-local`](./skill-review-local.md) — `@adk:review-local` (a.k.a. `adk-review-local`)
- [`review-pr`](./skill-review-pr.md) — `@adk:review-pr` (a.k.a. `adk-review-pr`)
