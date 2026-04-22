---
title: 'docs-review'
description: 'Review an existing technical document (Markdown file, fetched URL, or Confluence page) for accuracy, freshness, structure, completeness, and readability — producing severity-tiered findings against the actual code or configs the doc claims to describe. With `--mode confluence`, posts inline + footer comments back to the live page (with reconciliation against existing comments). Use when the deliverable is a critique with actionable fixes for a doc that already exists. Do not use to write a new doc (use adk-docs-write), publish a doc (use adk-publish-confluence), or review code (use adk-review-pr / adk-review-local).'
skill_name: docs-review
category: router
---
# ADK Docs / Review

Standalone task skill under the `@adk:docs` (a.k.a. `adk-docs`) category router. Produces a findings-first review of an existing document with each finding anchored to the doc and to the source-of-truth it claims to describe. In `--mode confluence`, also reconciles existing comments and posts inline + footer comments back to the live page.

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
| `<post-mode>` | optional | Confluence only: `dry-run` (default) / `post` (post inline + footer) |
| `<reconciliation>` | optional | Confluence only: `validate-then-keep` (default) / `aggressive-cleanup` / `read-only` |
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
12. **Decide post-mode** (Confluence) — present findings + reconciliation map; if `post` (or `--auto`), proceed to Validate. Otherwise emit dry-run report and stop.
13. **Validate (Phase 3: pre-post)** (Confluence) — every check in `doc-review-validator.md` Phase 3: findings reproducible from current page + source, comment shape compliant, anchors stable, no duplicates, verdict honest, posting permission confirmed. STOP and fix on any BLOCKER.
14. **Postback** (Confluence) — per `doc-postback-protocol.md`: inline comments first, then reconciliation replies, then footer summary. Each piece uses templates from `doc-review-comment-format.md` and `doc-reply-templates.md`.
15. **Validate (Phase 4: post-execution)** — every approved finding posted (or report written, in local mode), validator log written to `.temp/notes/`.
16. **Report** — final report per `doc-review-output-format.md`: status banner, verdict, reconciliation summary (Confluence), findings ordered by severity, validation block, postback summary (Confluence), recommended next step.

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

## Posting rules (Confluence mode)

- Inline comments anchor to a verbatim text snippet from the current page (one finding per inline comment).
- Footer summary comment lists Blockers + Critical only by name; everything else as counts.
- Reconciliation replies posted per `doc-comment-reconciliation.md` and `doc-reply-templates.md`.
- Idempotent: validator log records Confluence-returned IDs so re-runs do NOT duplicate.
- Never edit page content. This skill ONLY comments.

## Anti-patterns

See `doc-review-anti-patterns.md` for the full list. Key ones:

- Calling out "improve clarity" without a concrete suggested replacement.
- Marking nitpicks as Critical because they are visible.
- Reviewing the doc against memory instead of the source code.
- Findings without doc anchors AND source anchors.
- Verdict of "looks good" with zero validation runs against the source.
- (Confluence) Skipping `doc-comment-reconciliation.md` and producing duplicates.
- (Confluence) Editing page content (this skill only comments).
- Posting before the user approves (unless `--auto`).

## Examples

```
adk-docs-review docs/README.md
```

```
adk-docs-review docs/runbooks/oncall.md --focus accuracy,freshness --source src/oncall/
```

```
adk-docs-review https://your-org.atlassian.net/wiki/spaces/ENG/pages/12345 --mode confluence --post-mode post --auto
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
5. **(Confluence only) Post mode: dry-run (report only) or post (inline + footer)?** — _How to pick:_ Default dry-run on first run. Post after explicit approval (or pass `--auto`).
6. **(Confluence only) Reconciliation aggressiveness on existing comments?** — _How to pick:_ `validate-then-keep` (default), `aggressive-cleanup`, or `read-only`.

## Default vs detailed output

**Default report:** Status banner + severity-grouped findings + verification block + recommended next skill (usually `adk-docs-write` to fix).

**Detailed report (on request or `--verbose`):** Add drift map (doc claim → actual code state), readability metrics (Flesch, sentence length), missing sections by doc-type template.

**Artifact:**
- Local mode: `doc-review-report` — Markdown report. The doc itself is unchanged.
- Confluence mode: `doc-review-comments` — inline + footer comments on the live Confluence page, plus a Markdown mirror under `.temp/`.

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
