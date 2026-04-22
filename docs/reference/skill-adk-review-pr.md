---
title: 'adk-review-pr'
description: 'Review a remote pull request with severity-tiered findings, evidence per finding, existing-comment reconciliation, and posted-back comments via the appropriate provider (GitHub, Bitbucket). On Bitbucket, manages tasks for Blocker / Critical findings. Use when a PR URL is the target and the deliverable is a structured review (findings + optional posted comments). Do not use for local uncommitted changes (use adk-review-local), addressing existing reviewer feedback (use adk-review-feedback), doc-only review (use adk-docs-review), or auditing the whole repo (use adk-audit-repo).'
skill_name: adk-review-pr
category: task
---
# ADK Review / PR

Standalone task skill under the `adk-review` category router. Produces a findings-first review of a remote PR with explicit severity per finding, clear evidence, full reconciliation against existing comments, and (when authorized) posted-back inline + summary + tasks.

## When to use

- A PR URL on GitHub or Bitbucket is the target.
- Deliverable is a structured review report and (optionally) posted PR comments / Bitbucket tasks.
- The reviewer wants severity-tiered, evidence-backed findings, not freeform prose.
- A re-review is needed after the author pushed new commits, with reconciliation against existing comments.

## When NOT to use

- Changes are local and not yet pushed → `adk-review-local`
- Existing reviewer comments need to be addressed in code → `adk-review-feedback`
- Multi-dimensional repo-wide audit → `adk-audit-repo`
- Doc-only review → `adk-docs-review` (with `--mode confluence` for Confluence pages)

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<pr-url>` | yes | Full PR URL (provider auto-detected per `pr-mcp-fallback.md`) |
| `<focus>` | optional | `correctness` / `security` / `performance` / `style` / `all` (default) |
| `<post-mode>` | optional | `dry-run` (default — report only) / `post` (post inline + summary + tasks) |
| `<reconciliation>` | optional | `validate-then-keep` (default) / `aggressive-cleanup` / `read-only` |
| `<task-strategy>` | optional | Bitbucket only: `task-per-blocker-and-critical` (default) / `task-per-blocker-only` / `no-tasks` |
| `<scope>` | optional | Path filter inside the PR diff |
| `--auto` | optional | Skip approval gates (still validates per `pr-review-validator.md`) |

## Workflow

1. **Confirm intent** — restate PR URL, focus, post-mode, reconciliation aggressiveness, task strategy. Approval gate unless `--auto`.
2. **Validator gate (Phase 1)** — pre-execution checks per `pr-review-validator.md`: PR URL parses, provider auth works, network reachable, diff size sane.
3. **Fetch context** — retrieve PR diff, description, linked issue, branch, base, and ALL existing comments / replies / tasks via `pr-mcp-fallback.md`. Confirm the diff matches the URL.
4. **Validator gate (Phase 2: `diff-fetched`)** — diff retrieved and matches URL.
5. **Read code** — read the changed files in their post-PR state, plus immediate dependencies and tests, per `pr-research-protocol.md`.
6. **Validator gate (Phase 2: `code-read`)** — every changed file read in context.
7. **Reconcile existing comments** — classify every existing thread per `pr-comment-reconciliation.md` (keep-open / resolved-confirmed / resolved-stale / moved / no-longer-applicable / pushback / clarify). Plan replies and (Bitbucket) task actions.
8. **Validator gate (Phase 2: `reconciled`)** — every existing thread classified.
9. **Run dimension passes** — depending on focus, run each dimension as a parallel pass and collect findings:
   - Correctness: logic, edge cases, error handling, types.
   - Security: input validation, secrets, authz/n, injection.
   - Performance: complexity, allocations, network round-trips.
   - Style: naming, structure, repo conventions (lint config, `CONTRIBUTING.md`).
   - Tests: coverage of changed behavior, regression tests for any bug fixed.
10. **Tier and shape findings** — assign each finding Type (Blocker / Critical / Issue / Suggestion / Nitpick / Question / Praise), Severity (Blocker > Critical > Should Have > May Have > Nitpick > Question), Confidence (0-100), Dimension, file:line, quoted evidence, suggested fix. Render every drafted comment in the canonical shape from `pr-review-comment-format.md`.
11. **Validator gate (Phase 2: `findings-tiered`)** — every finding has all required fields.
12. **Decide post-mode** — present findings + reconciliation map; if `post` (or `--auto`), proceed to Validate. Otherwise emit dry-run report and stop.
13. **Validate (Phase 3: pre-post)** — every check in `pr-review-validator.md` Phase 3: findings reproducible from current diff, comment shape compliant, no duplicates, task strategy declared per finding, verdict honest, posting permission confirmed. STOP and fix on any BLOCKER.
14. **Postback** — per `pr-postback-protocol.md`: inline comments first, then (Bitbucket) tasks, then reconciliation replies, then summary comment. Each piece uses templates from `pr-review-comment-format.md` and `pr-reply-templates.md`.
15. **Validate (Phase 4: post-execution)** — every approved finding posted, all reconciliation replies posted, summary comment present (or N/A), tasks reconciled, validator log written to `.temp/notes/`.
16. **Report** — final report per `pr-output-format.md`: status banner, verdict, reconciliation summary, findings ordered by severity, validation block, postback summary, residual risk.

## Severity ladder

| Label | Meaning |
| --- | --- |
| `Blocker` | Must fix before merge — bug, security hole, broken contract |
| `Critical` | Strongly recommended fix; would normally block release |
| `Should Have` | Improvement that meaningfully raises quality |
| `May Have` | Optional polish |
| `Nitpick` | Style or taste only |
| `Question` | Reviewer uncertain; needs clarification |

Lead with the highest. Never mix levels in one bullet. Severity drives summary inclusion (Blockers + Critical listed; rest counted only) and verdict (any Blocker → request-changes).

## Type ladder

| Type | When |
| --- | --- |
| `Blocker` | Severity-elevated Issue that must block merge |
| `Critical` | Severity-elevated Issue strongly recommended before merge |
| `Issue` | Bug or violation of expectations |
| `Suggestion` | Improvement, not mandatory |
| `Nitpick` | Minor cosmetic tweak |
| `Question` | Seeks clarification |
| `Praise` | Highlights well-executed code or design |

Type goes in the posted comment title (`**[Type][focus] Title**`); Severity drives report ordering. They are NOT redundant — Type is "what kind of feedback this is", Severity is "how merge-blocking it is".

## Finding shape (reviewer-facing card)

Each finding is presented to the user before approval as a card per `pr-review-comment-format.md`:

````text
### F<id> [<Severity>][<Type>][<focus-area>] <Short, specific title>

Location: `<file:line-or-range>`
Action: <post new inline comment | reply to existing thread | local-only note>
Task: <create | keep open | resolve | none>

Why post this comment:
- <reason 1>
- <reason 2>

Exact comment to post:
```md
**[<Type>][<focus-area>] <Short, specific title>**

**Confidence:** <0-100>/100 | **Dimension:** <dim> | **Guideline:** <ref>

**Issue Explanation:**
<concise paragraph>

**Suggested Fix:**
<concrete recommendation, fenced code if useful>

**Impact:**
<concrete consequence>
```

Reviewer explanation:
<1-3 short sentences with extra context to help the user decide>
````

Stable IDs (`F1`, `F2`, `F3`, ...) drive the user's accept/reject loop (`a-1,3`, `r-2`, `e-4`). The ID is NOT included in the posted comment text.

## Output format

The full report shape lives in `pr-output-format.md`. The default report leads with a status banner, verdict, reconciliation summary, findings ordered by severity, and a validation block. Detailed mode (under `--verbose`) adds per-dimension narrative, drift map, captured lint/test output, and suggested patches as code blocks.

## Posting rules

- Inline comments anchor to a precise line range from the PR diff (one finding per inline comment; consolidate per location).
- Summary comment lists Blockers + Critical only by name; everything else as counts.
- Bitbucket tasks tracked per `task-strategy` (default: every Blocker and every Critical gets a linked task).
- Reconciliation replies posted per `pr-comment-reconciliation.md` and `pr-reply-templates.md`.
- Idempotent: the validator log records provider-returned IDs so re-runs do NOT duplicate.
- Never auto-approve. Never auto-merge. The Approve button is always a human action even under `--auto`.

## Anti-patterns

See `pr-anti-patterns.md` for the full list. Key ones:

- Mixing severities in a single bullet ("nit / blocker?"). Pick one Type + Severity.
- Findings without evidence. If you cannot quote it, do not file it.
- Reviewing the description instead of the code.
- Skipping `pr-comment-reconciliation.md` and producing a "fresh" review that re-files what's already raised.
- Resolving a Bitbucket task because the author replied "fixed" without re-validating against the current code.
- Posting before the user approves (unless `--auto`).
- Stapling multiple findings into one inline comment.
- Posting an Approve verdict automatically — never.

## Examples

```
adk-review-pr https://github.com/org/repo/pull/842 --focus correctness,security
```

```
adk-review-pr https://bitbucket.org/org/repo/pull-requests/17 --post-mode post --auto
```

```
adk-review-pr https://bitbucket.org/org/repo/pull-requests/17 --reconciliation aggressive-cleanup --task-strategy no-tasks
```

See `pr-examples.md` for full input + output samples.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the documented default for each (see `pr-clarifying-questions.md`) and reports the choices.

1. **What is the PR URL and provider (GitHub or Bitbucket)?** — _How to pick:_ Detect from URL host. github.com / GHE → github. bitbucket.org → bitbucket.
2. **Focus: correctness, security, performance, style, all?** — _How to pick:_ All = default for first review. Narrow to one when re-reviewing after changes or when scope is huge.
3. **Post mode: dry-run (report only) or post (inline + summary + tasks)?** — _How to pick:_ Default dry-run on first run so the user can review the findings. Post after explicit approval (or pass `--auto`).
4. **Reconciliation aggressiveness on existing comments?** — _How to pick:_ `validate-then-keep` (default) re-validates and replies; `aggressive-cleanup` also dismisses no-longer-applicable threads; `read-only` skips reply-on-existing entirely.
5. **(Bitbucket only) Task strategy for new Blockers / Critical findings?** — _How to pick:_ `task-per-blocker-and-critical` (default), `task-per-blocker-only`, or `no-tasks`.

## Default vs detailed output

**Default report:** Status banner + verdict + reconciliation summary + severity-grouped findings + validation block. See `pr-output-format.md`.

**Detailed report (on request or `--verbose`):** Add per-dimension narrative (correctness/security/perf/style/tests), drift map, lint/test output captured, suggested patches as code blocks.

**Artifact:** `pr-review-comments` — inline comments + summary comment + (Bitbucket) tasks on the remote PR. Markdown report mirrored in `.temp/`. See `pr-artifact-format.md`.

**Artifact path:** `.temp/reports/review-pr-<provider>-<number>.md` (full report). Validator log at `.temp/notes/review-pr-<provider>-<number>-validator.md`. Inline + summary + tasks live on the remote PR.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/interaction-contract.md` | Default-ask, explained-options, `--auto` contract every skill must follow (global, identical across skills). |
| `references/pr-reviewer-persona.md` | The PR-reviewer persona (mission, focus areas, hard rules, status banner) that drives this skill. |
| `references/pr-review-standards.md` | Constitution: shared ADK baseline + skill-specific non-negotiables for PR review. |
| `references/pr-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/pr-output-format.md` | Default vs detailed report shapes; status banner; severity ladder; verbosity rules. |
| `references/pr-artifact-format.md` | The deliverable's format and where it lives (PR comments + tasks + `.temp/` mirror). |
| `references/pr-anti-patterns.md` | Things to avoid when running this skill (review shape, reconciliation, posting, validator, workflow). |
| `references/pr-examples.md` | Trigger phrases, sample invocations, sample dry-run + posted output. |
| `references/pr-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline for PR review. |
| `references/pr-mcp-fallback.md` | Preferred MCP server (github / bitbucket) and the manual CLI / REST fallback. |
| `references/pr-review-comment-format.md` | Canonical posted-comment template (bold-label) plus reviewer-facing finding card and summary shape. |
| `references/pr-reply-templates.md` | Reply templates: fix-acknowledged, fix-applied, pushback, partial-fix, clarification, task-resolution, task-restatement, stale-dismissal, out-of-scope. |
| `references/pr-comment-reconciliation.md` | How to validate existing comments / replies / Bitbucket tasks against current code before drafting new comments. |
| `references/pr-postback-protocol.md` | When and how to post: pre-post gate, posting order, verdict rules, provider mapping, idempotent retry. |
| `references/pr-review-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-post, post-execution) the skill MUST run. |

<!-- adk:references:end -->
