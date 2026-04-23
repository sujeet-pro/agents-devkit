---
name: docs-review
description: Review an existing technical document (Markdown file, fetched URL, or Confluence page) for accuracy, freshness, structure, completeness, and readability — producing severity-tiered findings against the actual code or configs the doc claims to describe. By default, posts comments back when the source supports it (Confluence inline + footer) and otherwise writes a Markdown review file under `.temp/reports/`. With `--fix`, finalizes the findings then hands off to `adk-docs-write` to apply the auto-fixable ones in the source doc. Use when the deliverable is a critique with actionable fixes for a doc that already exists. Do not use to write a new doc from scratch (use adk-docs-write directly), publish a doc (use adk-publish-confluence), or review code (use adk-review-pr / adk-review-local).
metadata:
  category: review
  kind: task
  layer: 5
  modes: [auto, review, fix]
---

# ADK Docs / Review

Standalone task skill under the `@adk:docs` (a.k.a. `adk-docs`) category router. Produces a findings-first review of an existing document with each finding anchored to the doc and to the source-of-truth it claims to describe.

**Default delivery is automatic, based on the source:**

- **Confluence pages** (`*.atlassian.net/wiki/...`) → reconcile existing threads and post inline + footer comments back to the live page.
- **Local Markdown files / fetched URLs** → write a Markdown review file under `.temp/reports/doc-review-<slug>.md` (no live posting target exists, so the review IS the deliverable).

`--mode review` forces dry-run (report only, even on Confluence). `--mode fix` finalizes the findings and then delegates to `adk-docs-write` to apply the auto-fixable ones to the source doc, with the residual report attached.

## When to use

- A doc is suspected of drifting from the code.
- A doc must be checked before publishing or before a release.
- A doc is being adopted by a new team and they want a quality bar.
- A handoff requires confirming the doc is still accurate.
- A Confluence page has accumulated stale inline comments that need reconciliation.

## When NOT to use

- The doc does not exist yet → `@adk:docs-write` (a.k.a. `adk-docs-write`)
- Publishing a Markdown doc to Confluence → `@adk:publish-confluence` (a.k.a. `adk-publish-confluence`)
- Reviewing code, not docs → `@adk:review-pr` (a.k.a. `adk-review-pr`) / `@adk:review-local` (a.k.a. `adk-review-local`)
- Auditing a whole repo (which can call this skill per-doc) → `@adk:audit-repo` (a.k.a. `adk-audit-repo`)
- You want to also EDIT the page (Confluence owner workflow) → `quince-confluence-doc`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<target>` | yes | Local file path, fetched URL, or Confluence page URL/ID |
| `<mode>` | optional | `local` (default for files / public URLs) / `confluence` (default for `*.atlassian.net/wiki/...`) |
| `<focus>` | optional | `accuracy` / `freshness` / `structure` / `completeness` / `readability` / `all` (default) |
| `<source-of-truth>` | optional | Path or URL the doc must agree with (default: inferred from doc — surfaces a WARN) |
| `<post-mode>` | optional | Confluence only: `post` (default — post inline + footer) / `dry-run` (force review-only) |
| `<reconciliation>` | optional | Confluence only: `validate-then-keep` (default) / `aggressive-cleanup` / `read-only` |
| `--fix` | optional | After findings are approved, hand off auto-fixable ones to `adk-docs-write` to edit the source doc, then re-validate. Equivalent to `--mode fix`. |
| `--repo <url-or-path>` | optional | Repeatable; extra repos for source-of-truth (per `doc-review-multi-repo.md`) |
| `--auto` | optional | Skip approval gates (still validates per `doc-review-validator.md`) |

## Workflow

1. **Confirm intent** — restate target, mode, focus, source-of-truth, post-mode (Confluence), reconciliation aggressiveness (Confluence). Approval gate unless `--auto`.
2. **Validator gate (Phase 1)** — pre-execution checks per `doc-review-validator.md`: target reachable, mode valid, (Confluence) Atlassian MCP authenticated, source-of-truth resolvable.
3. **Fetch context** — read the doc (file or URL) and (Confluence) all existing inline + footer comments via `doc-review-mcp-fallback.md`.
4. **Validator gate (Phase 2: `doc-fetched`)** — doc retrieved and matches the target.
5. **Read source-of-truth** — read the linked code, configs, scripts, env files, and any cross-repo source per `doc-review-multi-repo.md`. Repo evidence over guessing.
6. **Validator gate (Phase 2: `source-read`)** — every referenced source read in current state.
7. **Reconcile existing comments** (Confluence mode only) — classify every existing thread per `doc-comment-reconciliation.md`. Plan replies.
8. **Validator gate (Phase 2: `reconciled`)** (Confluence) — every existing thread classified.
9. **Run dimension passes** — depending on focus, run each dimension as a parallel pass and collect findings:
   - **Accuracy**: every command, code block, schema, env var, link resolves and matches the source.
   - **Freshness**: any "as of X" claims, version references, screenshots, version-specific instructions are still current.
   - **Structure**: presence and order of expected sections (per doc type), level hierarchy, table consistency.
   - **Completeness**: gaps the doc-type's audience expects (e.g., README missing Quick Start; runbook missing rollback).
   - **Readability**: lead, scannability, jargon vs defined terms, length.
10. **Tier and shape findings** — assign each finding Type (Blocker / Critical / Issue / Suggestion / Nitpick / Question / Praise), Severity (Blocker > Critical > Should Have > May Have > Nitpick > Question), Confidence (0-100), Dimension, doc anchor, source anchor, quoted evidence, suggested fix. Render every drafted comment in the canonical shape from `doc-review-comment-format.md`.
11. **Validator gate (Phase 2: `findings-tiered`)** — every finding has all required fields.
12. **Decide delivery** — auto-pick based on source:
    - **Confluence**: default to `post-mode=post` (post inline + footer). Override to `dry-run` only when `--mode review` was passed or the user opted into dry-run during clarifying questions.
    - **Local file / fetched URL**: write the Markdown review file to `.temp/reports/doc-review-<slug>.md` (this IS the delivery — there is no live source to post into).
    Present findings + reconciliation map (Confluence) for approval unless `--auto`.
13. **Validate (Phase 3: pre-post)** (Confluence post-mode only) — every check in `doc-review-validator.md` Phase 3: findings reproducible from current page + source, comment shape compliant, anchors stable, no duplicates, verdict honest, posting permission confirmed. STOP and fix on any BLOCKER.
14. **Deliver** — per `doc-postback-protocol.md`:
    - Confluence post: inline comments first, then reconciliation replies, then footer summary. Each piece uses templates from `doc-review-comment-format.md` and `doc-reply-templates.md`. Capture every Confluence-returned ID into the in-session post receipt set.
    - Local mode: write the Markdown review file. Report path is part of the final report.
15. **Verify posted comments (post-confirmation, Confluence post-mode only)** — per `doc-postback-protocol.md` "Post-confirmation": wait 5s, re-fetch the page's full inline + footer comment graph, and confirm every receipt ID re-appears (and, for inline comments, on the expected anchor text). On miss, retry at 10s and 20s (3-attempt total budget, 35s wall-clock). Final result is `OK` (all confirmed) or `WARN: <n> entries unconfirmed` — surface the unconfirmed IDs (with `_links.webui`) in the report. Do NOT re-post on a miss; the API said 2xx and a re-post would create duplicates if the comment is just propagation-lagged. Skipped entirely in `--mode local` and dry-run.
16. **Validate (Phase 4: post-execution)** — every approved finding posted (or report written, in local mode), post-confirmation pass logged (OK or WARN, or N/A in local / dry-run), validator log written to `.temp/notes/`.
17. **Report** — final report per `doc-review-output-format.md`: status banner, verdict, reconciliation summary (Confluence), findings ordered by severity, validation block, postback summary (Confluence; with the post-confirmation outcome) or report path (local), recommended next step.
18. **(`--fix` only) Hand off to `adk-docs-write`** — for every finding marked auto-fixable in step 10, dispatch `adk-docs-write` with the doc path + the `Suggested Fix` block as the change spec. After `docs-write` finishes, re-run this skill in `--mode review` against the same target to confirm the residual finding set shrank as expected. Residual findings are appended to the original report under a `## After auto-fix pass` section.

## Severity ladder

| Label | Doc meaning |
| --- | --- |
| `Blocker` | Wrong or dangerous — command does not work, env var name wrong, security advice incorrect |
| `Critical` | Misleading or seriously outdated — reader will likely waste time or hit a wall |
| `Should Have` | Notable gap — missing section the doc type expects, ambiguous wording |
| `May Have` | Minor improvement — phrasing, ordering |
| `Nitpick` | Style only — punctuation, list bullet style |
| `Question` | Reviewer uncertain whether this is right; needs author input |

Lead with the highest. Never mix levels in one bullet.

## Type ladder

| Type | When |
| --- | --- |
| `Blocker` | Severity-elevated Issue that must block publish |
| `Critical` | Severity-elevated Issue strongly recommended before publish |
| `Issue` | Doc disagrees with source; reader will be misled |
| `Suggestion` | Improvement, not mandatory |
| `Nitpick` | Style or taste only |
| `Question` | Reviewer uncertain; needs author / owner input |
| `Praise` | Highlights a notably well-written section |

## Finding shape (reviewer-facing card)

Each finding is presented to the user before approval as a card per `doc-review-comment-format.md`:

````text
### F<id> [<Severity>][<Type>][<focus-area>] <Short, specific title>

Doc location: `<doc-path>:LINE-LINE` (or section heading + anchor)
Source-of-truth: `<source-path>:LINE-LINE` (or URL with retrieval date)
Action: <add inline comment | reply to existing thread | local-only note>

Why post this comment:
- <reason 1>
- <reason 2>

Exact comment to post:
```md
**[<Type>][<focus-area>] <Short, specific title>**

**Confidence:** <0-100>/100 | **Dimension:** <dim> | **Source-of-truth:** <source-anchor>

**Issue Explanation:**
<concise paragraph>

**Suggested Fix:**
<concrete recommendation, fenced code if useful>

**Impact:**
<concrete consequence>
```

Reviewer explanation:
<1-3 short sentences with extra context>
````

Stable IDs (`F1`, `F2`, `F3`, ...) drive the user's accept/reject loop.

## Output format

Full report shape lives in `doc-review-output-format.md`. Default report leads with status banner, verdict, reconciliation summary (Confluence), findings ordered by severity, and a validation block. Detailed mode (`--verbose`) adds drift map, readability metrics, missing-sections analysis, per-dimension narrative, suggested replacement Markdown blocks.

## Per-doc-type focus tips

| Doc type | Watch for |
| --- | --- |
| README | Quick-start commands actually work; install steps include version requirements; supported OS list current |
| Runbook | Mitigation steps tested in the last quarter; commands are copy-paste ready; on-call rotation links current |
| API reference | Signatures match the code; error codes complete; deprecated endpoints flagged |
| ADR | Status reflects reality (Accepted vs Superseded); consequences honest; supersedes-link present |
| Onboarding | Day-1 list still possible from a clean machine; "who to ask" is current; access requests still valid |
| Migration guide | Source/target versions still relevant; rollback path concrete; "how to verify" steps present |
| Tech radar | Dates and signals not stale; ring movement justified |

## Delivery rules

**Confluence (default `post-mode=post`):**

- Inline comments anchor to a verbatim text snippet from the current page (one finding per inline comment).
- Footer summary comment lists Blockers + Critical only by name; everything else as counts.
- Reconciliation replies posted per `doc-comment-reconciliation.md` and `doc-reply-templates.md`.
- Idempotent: validator log records Confluence-returned IDs so re-runs do NOT duplicate.
- This skill never edits page content directly — it ONLY comments. Use `--fix` to delegate edits to `adk-docs-write` (which works on Markdown sources only; Confluence page edits still happen out-of-band).
- **Always run post-confirmation.** A successful API call is not the same as a visible comment. After every postback, wait 5s, re-fetch the page's inline + footer comment graph, verify each receipt ID re-appears (retry at 10s and 20s on miss). Surface unconfirmed IDs as a `WARN` in the report; never re-post automatically — Confluence propagation lag would turn a re-post into a real duplicate.

**Local Markdown / fetched URL:**

- The Markdown review file at `.temp/reports/doc-review-<slug>.md` IS the deliverable — there is no live posting target.
- The doc itself is unchanged unless `--fix` is passed.

**`--fix` (any source):**

- Only auto-fixable findings (those whose `Suggested Fix` is a concrete replacement block, not a question or a "discuss") are handed off.
- Edits go through `adk-docs-write` so style + validation rules stay identical to fresh authoring.
- After the fix pass, this skill re-runs in `--mode review` and appends residuals to the original report under `## After auto-fix pass`.

## Anti-patterns

See `doc-review-anti-patterns.md` for the full list. Key ones:

- Calling out "improve clarity" without a concrete suggested replacement.
- Marking nitpicks as Critical because they are visible.
- Reviewing the doc against memory instead of the source code.
- Findings without doc anchors AND source anchors.
- Verdict of "looks good" with zero validation runs against the source.
- (Confluence) Skipping `doc-comment-reconciliation.md` and producing duplicates.
- (Confluence) Editing page content directly (this skill only comments — `--fix` delegates to `adk-docs-write`).
- Posting before the user approves (unless `--auto`).
- Skipping the live posting target on Confluence by defaulting to dry-run when the source clearly supports it (post is the default; dry-run is the override).
- Calling `adk-docs-write` under `--fix` for findings that aren't auto-fixable (questions, discuss, design feedback).
- Treating "the API returned 2xx" as proof a comment is on the page. Always run the post-confirmation re-fetch + retry budget (5s → 10s → 20s) before declaring Phase 4 done.
- Re-posting on a post-confirmation miss. A re-post would create real duplicates if the original is just propagation-lagged; the only correct action is to log a `WARN` with the receipt ID + `_links.webui` and let the user check (or re-run the skill, which will reconcile via `doc-comment-reconciliation.md`).

## Examples

```
adk-docs-review docs/README.md
```

```
adk-docs-review docs/runbooks/oncall.md --focus accuracy,freshness --source src/oncall/
```

```
adk-docs-review https://your-org.atlassian.net/wiki/spaces/ENG/pages/12345           # auto-detects Confluence; defaults to post
```

```
adk-docs-review https://your-org.atlassian.net/wiki/spaces/ENG/pages/12345 --mode review   # force dry-run on Confluence
```

```
adk-docs-review docs/runbooks/oncall.md --fix                                          # review + hand off auto-fixes to adk-docs-write
```

```
adk-docs-review docs/integration-guide.md --repo https://github.com/org/service-a --repo https://github.com/org/service-b
```

See `doc-review-examples.md` for full input + output samples.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the documented default for each (see `doc-review-clarifying-questions.md`) and reports the choices.

1. **Where is the doc (path or URL)?** — _How to pick:_ Required. URLs are fetched if reachable. Confluence URLs auto-detect `--mode confluence`.
2. **Where is the source-of-truth (path, URL, or 'inferred from doc')?** — _How to pick:_ Explicit > inferred. State the file/dir that the doc claims to describe.
3. **Mode: local (Markdown report only) or confluence (post inline + footer comments)?** — _How to pick:_ Auto-detected from target shape; override only when the auto-detect is wrong.
4. **Focus: accuracy / freshness / structure / completeness / readability / all?** — _How to pick:_ All for first review. Narrow when iterating after a fix pass.
5. **(Confluence only) Post mode: post (inline + footer) or dry-run (report only)?** — _How to pick:_ `post` is the default — the source supports comments, so the comments ARE the deliverable. Pick `dry-run` (or pass `--mode review`) only when you want to inspect findings before they hit the page.
6. **(Confluence only) Reconciliation aggressiveness on existing comments?** — _How to pick:_ `validate-then-keep` (default), `aggressive-cleanup`, or `read-only`.
7. **Apply auto-fixes to the source doc (`--fix`)?** — _How to pick:_ Default `no`. Pick `yes` (or pass `--fix`) when the doc is a Markdown file you own and the goal is to land the corrections, not just file them. Confluence pages cannot be auto-edited; `--fix` only applies to Markdown sources.

## Default vs detailed output

**Default report:** Status banner + severity-grouped findings + verification block + recommended next skill (usually `adk-docs-write` to fix).

**Detailed report (on request or `--verbose`):** Add drift map (doc claim → actual code state), readability metrics (Flesch, sentence length), missing sections by doc-type template.

**Artifact:**
- Local mode: `doc-review-report` — Markdown report under `.temp/reports/`. The doc itself is unchanged unless `--fix` is passed.
- Confluence mode (default `post`): `doc-review-comments` — inline + footer comments on the live Confluence page, plus a Markdown mirror under `.temp/`.
- Any mode with `--fix`: same as above, plus an `adk-docs-write` edit pass against the source Markdown (Confluence pages cannot be auto-edited) and a residual review appended to the report.

See `doc-review-artifact-format.md`.

**Artifact path:** `.temp/reports/doc-review-<slug>.md`. Validator log at `.temp/notes/doc-review-<slug>-validator.md`. (Confluence) inline + footer comments live on the live page.

## Multi-repo context

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `doc-review-multi-repo.md` for full handling.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/interaction-contract.md` | Default-ask, explained-options, `--auto` contract every skill must follow (global, identical across skills). |
| `references/doc-reviewer-persona.md` | The doc-reviewer persona (mission, focus areas, hard rules, status banner). |
| `references/doc-review-standards.md` | Constitution: shared ADK baseline + skill-specific non-negotiables for doc review. |
| `references/doc-review-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/doc-review-output-format.md` | Default vs detailed report shapes; status banner; severity ladder; verbosity rules. |
| `references/doc-review-artifact-format.md` | The deliverable's format and where it lives (Markdown report + Confluence comments + `.temp/` mirror). |
| `references/doc-review-anti-patterns.md` | Things to avoid (review shape, reconciliation, posting, validator, workflow). |
| `references/doc-review-examples.md` | Trigger phrases, sample invocations, sample dry-run + posted output. |
| `references/doc-review-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline for doc review. |
| `references/doc-review-mcp-fallback.md` | Atlassian MCP for Confluence mode; REST fallback; mode auto-detect. |
| `references/doc-review-multi-repo.md` | How to pull source-of-truth from extra cloned or local-path repos. |
| `references/doc-review-comment-format.md` | Canonical posted-comment template (bold-label) plus reviewer-facing finding card and summary shape. |
| `references/doc-reply-templates.md` | Reply templates: fix-acknowledged, pushback, partial-fix, clarification, stale-dismissal, anchor-restatement, out-of-scope. |
| `references/doc-comment-reconciliation.md` | (Confluence) How to validate existing comments / replies against current page before drafting new. |
| `references/doc-postback-protocol.md` | (Confluence) When and how to post: pre-post gate, posting order, verdict rules, idempotent retry. |
| `references/doc-review-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-post, post-execution) the skill MUST run. |

<!-- adk:references:end -->
