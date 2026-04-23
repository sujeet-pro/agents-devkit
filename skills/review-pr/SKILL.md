---
name: review-pr
description: Review a remote pull request with severity-tiered findings, evidence per finding, existing-comment reconciliation, and posted-back comments via the appropriate provider (GitHub, Bitbucket). Auto-detects ownership of the PR — if the PR is NOT yours, defaults to posting review comments (and Bitbucket tasks for Blocker / Critical); if the PR IS yours, defaults to validating + replying to existing reviewer comments (delegating to adk-review-feedback) and, with `--fix`, locally applying the agreed-on fixes via the adk-build family before pushing. Use when a PR URL is the target and the deliverable is a structured review or a fix pass on your own PR. Do not use for local uncommitted changes (use adk-review-local) or doc-only review (use adk-docs-review).
metadata:
  category: review
  kind: task
  layer: 5
  modes: [auto, review, fix]
---

# ADK Review / PR

Standalone task skill under the `@adk:review` (a.k.a. `adk-review`) category router. Produces a findings-first review of a remote PR with explicit severity per finding, clear evidence, full reconciliation against existing comments, and (when authorized) posted-back inline + summary + tasks.

**Ownership-aware delivery (the headline behavior):**

- **PR is NOT yours (you are reviewing someone else's work)** → default behavior is full review pass: tier findings, reconcile existing threads, then post inline + summary (and Bitbucket tasks for Blocker / Critical). Equivalent to the historical default behavior of this skill.
- **PR IS yours (the current git author / repo owner created it)** → default behavior shifts to "address review on my own PR": validate every existing reviewer comment against the current diff, draft replies, and (only with `--fix`) hand off to `adk-build-feature` / `adk-build-bugfix` for local code edits before pushing. Reply drafting and posting are delegated to `adk-review-feedback`. The skill never auto-pushes — the final commit + push step is gated on the user.

Ownership is detected from the PR's `author.login` (or `user.account_id` on Bitbucket) compared to the locally-configured `git config user.email` / `gh auth status` identity. The skill always restates the detected ownership and the chosen mode before doing anything irreversible.

## When to use

- A PR URL on GitHub or Bitbucket is the target.
- Deliverable is a structured review report and (optionally) posted PR comments / Bitbucket tasks.
- The reviewer wants severity-tiered, evidence-backed findings, not freeform prose.
- A re-review is needed after the author pushed new commits, with reconciliation against existing comments.
- It is YOUR PR and you want the skill to validate + reply to existing reviewer comments (and optionally fix them locally with `--fix`).

## When NOT to use

- Changes are local and not yet pushed → `@adk:review-local` (a.k.a. `adk-review-local`)
- You only want to address feedback (not re-review the diff yourself) → `@adk:review-feedback` (a.k.a. `adk-review-feedback`) directly
- Multi-dimensional repo-wide audit → `@adk:audit-repo` (a.k.a. `adk-audit-repo`)
- Doc-only review → `@adk:docs-review` (a.k.a. `adk-docs-review`) (with `--mode confluence` for Confluence pages)

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<pr-url>` | yes | Full PR URL (provider auto-detected per `pr-mcp-fallback.md`) |
| `<focus>` | optional | `correctness` / `security` / `performance` / `style` / `all` (default) |
| `<ownership>` | optional | `auto` (default — detect from PR author vs local git identity) / `not-mine` (force review-and-post path) / `mine` (force feedback-and-fix path) |
| `<post-mode>` | optional | `auto` (default — `post` when not-mine, `dry-run-replies` when mine) / `dry-run` / `post` |
| `<reconciliation>` | optional | `validate-then-keep` (default) / `aggressive-cleanup` / `read-only` |
| `<task-strategy>` | optional | Bitbucket only: `task-per-blocker-and-critical` (default) / `task-per-blocker-only` / `no-tasks` |
| `<scope>` | optional | Path filter inside the PR diff |
| `--fix` | optional | When `ownership=mine`: locally apply fixes for accepted reviewer comments via `adk-build-feature` / `adk-build-bugfix` after replies are drafted. When `ownership=not-mine`: silently ignored (you can't push fixes to someone else's branch). Equivalent to `--mode fix`. |
| `--auto` | optional | Skip approval gates (still validates per `pr-review-validator.md`) |

## Workflow

1. **Confirm intent** — restate PR URL, focus, ownership decision (auto / mine / not-mine), post-mode, reconciliation aggressiveness, task strategy. Approval gate unless `--auto`.
2. **Validator gate (Phase 1)** — pre-execution checks per `pr-review-validator.md`: PR URL parses, provider auth works, network reachable, diff size sane.
3. **Fetch context** — retrieve PR diff, description, author, linked issue, branch, base, and ALL existing comments / replies / tasks via `pr-mcp-fallback.md`. Confirm the diff matches the URL.
4. **Detect ownership** — compare the PR's `author.login` (GitHub) or `user.account_id` (Bitbucket) against the locally-configured identity (`gh auth status`, `git config user.email`, Bitbucket username from the configured MCP / app password). Result: `mine` | `not-mine`. Surface the comparison in the status banner. The `<ownership>` input overrides the detection. **Branch the workflow on the result:**
    - `not-mine` → continue with steps 5–17 (review pass).
    - `mine` → continue with steps 5–8 (read code + classify existing comments) then jump to step 18 (feedback path).
5. **Read code** — read the changed files in their post-PR state, plus immediate dependencies and tests, per `pr-research-protocol.md`.
6. **Validator gate (Phase 2: `code-read`)** — every changed file read in context.
7. **Reconcile existing comments** — classify every existing thread per `pr-comment-reconciliation.md` (keep-open / resolved-confirmed / resolved-stale / moved / no-longer-applicable / pushback / clarify). Plan replies and (Bitbucket) task actions.
8. **Validator gate (Phase 2: `reconciled`)** — every existing thread classified.

### Path A — `ownership = not-mine` (review-and-post)

9. **Run dimension passes** — depending on focus, run each dimension as a parallel pass and collect findings:
   - Correctness: logic, edge cases, error handling, types.
   - Security: input validation, secrets, authz/n, injection.
   - Performance: complexity, allocations, network round-trips.
   - Style: naming, structure, repo conventions (lint config, `CONTRIBUTING.md`).
   - Tests: coverage of changed behavior, regression tests for any bug fixed.
10. **Tier and shape findings** — assign each finding Type (Blocker / Critical / Issue / Suggestion / Nitpick / Question / Praise), Severity (Blocker > Critical > Should Have > May Have > Nitpick > Question), Confidence (0-100), Dimension, file:line, quoted evidence, suggested fix. Render every drafted comment in the canonical shape from `pr-review-comment-format.md`.
11. **Validator gate (Phase 2: `findings-tiered`)** — every finding has all required fields.
12. **Decide post-mode** — default `post` for `not-mine` (the source supports comments — that IS the deliverable). Override to `dry-run` only if `--mode review` was passed. Present findings + reconciliation map for approval unless `--auto`.
13. **Validate (Phase 3: pre-post)** — every check in `pr-review-validator.md` Phase 3: findings reproducible from current diff, comment shape compliant, no duplicates, task strategy declared per finding, verdict honest, posting permission confirmed. STOP and fix on any BLOCKER.
14. **Postback** — per `pr-postback-protocol.md`: inline comments first, then (Bitbucket) tasks, then reconciliation replies, then summary comment. Each piece uses templates from `pr-review-comment-format.md` and `pr-reply-templates.md`. Capture every provider-returned ID into the in-session post receipt set.
15. **Verify posted comments (post-confirmation)** — per `pr-postback-protocol.md` "Post-confirmation": wait 5s, re-fetch the PR's full comment + reply + (Bitbucket) task graph, and confirm every receipt ID re-appears. On miss, retry at 10s and 20s (3-attempt total budget, 35s wall-clock). Final result is `OK` (all confirmed) or `WARN: <n> entries unconfirmed` — surface the unconfirmed IDs in the report. Do NOT re-post on a miss; the API said 2xx and a re-post would create duplicates if the comment is just propagation-lagged.
16. **Validate (Phase 4: post-execution)** — every approved finding posted, all reconciliation replies posted, summary comment present (or N/A), tasks reconciled, post-confirmation pass logged (OK or WARN), validator log written to `.temp/notes/`.
17. **Report** — final report per `pr-output-format.md`: status banner, verdict, reconciliation summary, findings ordered by severity, validation block, postback summary (with the post-confirmation outcome), residual risk.

### Path B — `ownership = mine` (feedback-and-fix)

18. **Validate every existing reviewer comment against the current diff** — for each external comment from step 7's reconciliation, decide: still-applicable / now-stale / partial. Skip your own previous comments unless they explicitly ask for action.
19. **Classify per reviewer comment** (delegated reply shape matches `adk-review-feedback`): `Apply` / `Discuss` / `Defer` / `Decline` / `Already-fixed`. Approval gate unless `--auto`.
20. **Draft replies via `adk-review-feedback`** — hand off the classified set to `adk-review-feedback` so the reply templates and posting protocol stay identical. This skill keeps ownership of the validation + classification; `adk-review-feedback` owns the reply text and posting.
21. **(`--fix` only) Local fix loop** — for every comment classified `Apply`:
    - Pick the right adk-build skill (`adk-build-bugfix` for bug-shaped feedback, `adk-build-refactor` for cleanup-shaped, `adk-build-feature` for behavior change).
    - Dispatch it as a focused subagent loaded with the comment + the affected files. The build skill runs its own plan / implement / validate phases.
    - After each comment is addressed, re-run `adk-review-local` on the changed files to confirm the fix matches the comment intent and didn't regress anything.
22. **(`--fix` only) Stage but never auto-push** — collected commits stay local. The skill writes a single staging report at `.temp/reports/review-pr-<provider>-<number>-fix-plan.md` with each commit grouped by reviewer comment ID, and waits for the user to push (or for `adk-publish-github` / `adk-publish-bitbucket` to be called explicitly).
23. **Post drafted replies** — per `pr-postback-protocol.md`. `Applied` replies link to the local commit SHA(s); `Defer` replies link to the follow-up; `Decline` replies carry the rationale. Capture every provider-returned reply ID into the in-session post receipt set.
24. **Verify posted replies (post-confirmation)** — same protocol as Path A's step 15: wait 5s, re-fetch the PR's full comment + reply graph, confirm every receipt ID re-appears. Retry at 10s and 20s on miss (3-attempt budget, 35s wall-clock). Final outcome `OK` or `WARN: <n> entries unconfirmed` is logged and surfaced. Never re-post on a miss — propagation lag is more likely than a failed write.
25. **Validate (Phase 4: post-execution)** — every comment in the filter set has exactly one reply class, replies posted (or N/A on dry-run-replies), every `Apply` has a local commit, post-confirmation pass logged, validator log written.
26. **Report** — final report per `pr-output-format.md` (feedback variant): status banner, ownership detection result, comment-by-comment table (id / class / fix commit / reply preview), validation block, post-confirmation outcome, push recommendation.

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

**Path A (`not-mine`) — review posting:**

- Inline comments anchor to a precise line range from the PR diff (one finding per inline comment; consolidate per location).
- Summary comment lists Blockers + Critical only by name; everything else as counts.
- Bitbucket tasks tracked per `task-strategy` (default: every Blocker and every Critical gets a linked task).
- Reconciliation replies posted per `pr-comment-reconciliation.md` and `pr-reply-templates.md`.
- Idempotent: the validator log records provider-returned IDs so re-runs do NOT duplicate.
- Never auto-approve. Never auto-merge. The Approve button is always a human action even under `--auto`.
- **Always run post-confirmation.** A successful API call is not the same as a visible comment. After every postback, wait 5s, re-fetch, verify each receipt ID re-appears (retry at 10s and 20s on miss). Surface unconfirmed IDs as a `WARN` in the report; never re-post automatically — propagation lag would turn a re-post into a real duplicate.

**Path B (`mine`) — feedback posting:**

- One reply per reviewer comment thread, labelled with the resolution class (`Applied` / `Already-fixed` / `Deferring` / `Declining` / `Discussing`).
- `Applied` replies must reference a local commit SHA produced in step 21 of the workflow — never bare assertions.
- A single summary comment is posted at the end (Applied count / Already-fixed count / Deferred count + links / Declined count / Discussing count + latest validation status).
- Never push to the branch automatically — even under `--auto`, `--fix` only stages commits locally and writes a fix-plan report. Push is a separate, gated action.
- Never auto-resolve a Bitbucket task on someone else's behalf. `Applied` may move a task to "Resolved" only when the validator confirms the fix is in the branch and the original task author authored the comment.
- **Same post-confirmation rule as Path A.** Drafted replies are not "posted" until the verification fetch sees them; otherwise they go into the report as `WARN` so the user can manually confirm.

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
- Skipping the ownership detection step or quietly defaulting to the wrong path. Always restate `mine` vs `not-mine` in the status banner before doing anything irreversible.
- Auto-pushing under `--fix` on your own PR. `--fix` stages local commits; the human pushes.
- Reviewing your own PR end-to-end (Path A) without first asking whether you wanted Path B (feedback-and-fix). Default for `mine` is Path B.
- Treating "the API returned 2xx" as proof a comment is on the PR. Always run the post-confirmation re-fetch + retry budget (5s → 10s → 20s) before declaring Phase 4 done.
- Re-posting on a post-confirmation miss. A re-post would create real duplicates if the original is just propagation-lagged; the only correct action is to log a `WARN` with the receipt ID + html_url and let the user check (or re-run the skill, which will reconcile via `pr-comment-reconciliation.md`).

## Examples

```
adk-review-pr https://github.com/org/repo/pull/842                                # ownership auto-detected
adk-review-pr https://github.com/org/repo/pull/842 --focus correctness,security   # someone else's PR; review-and-post
```

```
adk-review-pr https://bitbucket.org/org/repo/pull-requests/17 --post-mode post --auto   # someone else's PR; full post pass
```

```
adk-review-pr https://github.com/org/my-repo/pull/19                              # YOUR PR → defaults to validate + draft replies
adk-review-pr https://github.com/org/my-repo/pull/19 --fix                        # YOUR PR → also locally fix Apply'd comments via adk-build-*
adk-review-pr https://github.com/org/my-repo/pull/19 --ownership not-mine         # force Path A even on your own PR
```

```
adk-review-pr https://bitbucket.org/org/repo/pull-requests/17 --reconciliation aggressive-cleanup --task-strategy no-tasks
```

See `pr-examples.md` for full input + output samples.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the documented default for each (see `pr-clarifying-questions.md`) and reports the choices.

1. **What is the PR URL and provider (GitHub or Bitbucket)?** — _How to pick:_ Detect from URL host. github.com / GHE → github. bitbucket.org → bitbucket.
2. **Ownership: is this your PR or someone else's?** — _How to pick:_ Default `auto` (detect from PR author vs your local git identity). `not-mine` forces Path A (review-and-post). `mine` forces Path B (validate + reply + optional `--fix`). Confirm whenever the auto-detection has low confidence (no remote auth, ambiguous identity, fork PR).
3. **Focus: correctness, security, performance, style, all?** — _How to pick:_ All = default for first review. Narrow to one when re-reviewing after changes or when scope is huge.
4. **Post mode: post (inline + summary + tasks) or dry-run (report only)?** — _How to pick:_ Default `post` when `ownership=not-mine` (the source supports comments — that IS the deliverable). Default `dry-run-replies` when `ownership=mine` so you can inspect drafted replies before they hit the PR. Force `dry-run` only when you want to inspect findings before they hit the PR.
5. **Reconciliation aggressiveness on existing comments?** — _How to pick:_ `validate-then-keep` (default) re-validates and replies; `aggressive-cleanup` also dismisses no-longer-applicable threads; `read-only` skips reply-on-existing entirely.
6. **(Bitbucket only) Task strategy for new Blockers / Critical findings?** — _How to pick:_ `task-per-blocker-and-critical` (default), `task-per-blocker-only`, or `no-tasks`.
7. **(Path B / `mine` only) Apply local fixes via `--fix`?** — _How to pick:_ Default `no` — draft replies only, leave the code unchanged. Pick `yes` (or pass `--fix`) when you want the skill to call `adk-build-bugfix` / `adk-build-refactor` / `adk-build-feature` for every `Apply`'d comment. Local commits stay staged; the push is gated on you.

## Default vs detailed output

**Default report (Path A):** Status banner (with `ownership = not-mine`) + verdict + reconciliation summary + severity-grouped findings + validation block. See `pr-output-format.md`.

**Default report (Path B):** Status banner (with `ownership = mine`) + comment-by-comment table (id / class / fix commit / reply preview) + validation block + push recommendation. See `pr-output-format.md`.

**Detailed report (on request or `--verbose`):** Add per-dimension narrative (correctness/security/perf/style/tests), drift map, lint/test output captured, suggested patches as code blocks. Path B detailed adds per-comment plan, evidence each fix matches the comment intent, and residual disagreement notes.

**Artifact (Path A):** `pr-review-comments` — inline comments + summary comment + (Bitbucket) tasks on the remote PR. Markdown report mirrored in `.temp/`. See `pr-artifact-format.md`.

**Artifact (Path B):** `pr-feedback-replies` — drafted replies (posted unless dry-run) + a fix-plan markdown listing the local commits per reviewer comment. Push is a separate, user-gated action.

**Artifact path:** `.temp/reports/review-pr-<provider>-<number>.md` (full report). Validator log at `.temp/notes/review-pr-<provider>-<number>-validator.md`. Path B fix plan at `.temp/reports/review-pr-<provider>-<number>-fix-plan.md`. Inline + summary + tasks live on the remote PR.

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
