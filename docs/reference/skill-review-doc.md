---
title: 'review-doc'
description: 'Review an existing technical document (Markdown file in repo, fetched URL, Confluence page, Google Doc) for accuracy, freshness, structure, completeness, and readability.'
artifact_kind: skill
skill_name: review-doc
category: review
---
# review-doc

Review an existing technical document (Markdown file in repo, fetched URL, Confluence page, Google Doc) for accuracy, freshness, structure, completeness, and readability. Produces severity-tiered findings against the actual code or configs the doc claims to describe. Optionally accepts SUPPORTING DOCS (additional Confluence pages, Slack threads, Gmail threads, Google Docs) to add context to the review. Modes: `review` (post comments / write `review.md`) and `fix` (apply edits where authoritative). Use for any "look at this doc and tell me what's wrong / outdated / missing" request. Do not use to write a new doc (use `@adk:docs-write` (a.k.a. `adk-docs-write`)) or to publish a doc (use `@adk:publish-confluence` / `@adk:publish-gdrive`).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-review-doc` form via `agents-skills/`.

```text
/adk:review-doc            # interactive run (Claude Code)
/adk:review-doc --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-review-doc` (resolved through the
`agents-skills/adk-review-doc/` symlink).

## Source

Direct from `skills/review-doc/SKILL.md` — this page is auto-generated.

Replaces / extends the legacy `docs-review` skill. Adds support for passing supporting docs that inform the review.

## When to use

- "Review this doc."
- "Check if this Confluence page is still accurate."
- "Compare this README against the actual code."
- "Re-validate this runbook."

## When NOT to use

- Code review on a PR → `@adk:review-pr` (a.k.a. `adk-review-pr`).
- Writing a new doc → `@adk:docs-write` (a.k.a. `adk-docs-write`).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<target>` | yes | Path / URL / Confluence page id / Google Doc id |
| `<task-slug>` | yes | |
| `<supporting-docs>` | optional | List of URLs to consult for context (Confluence pages, Slack threads, Gmail, GDocs) — handed to `@adk:context-gather` |
| `<focus>` | optional | `accuracy` / `freshness` / `structure` / `completeness` / `readability` / `all` (default) |
| `<post-mode>` | optional | `dry-run` (default — write `review.md`) / `post` (post inline + footer comments to live Confluence/GDoc) |
| `--mode` | optional | `review` (default) / `fix` (apply edits if authoritative) |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Phase 1 validator.** Target reachable; supporting docs reachable (or skip with reason).
2. **Fetch target.** Markdown file → read; URL → WebFetch; Confluence → confluence MCP; GDoc → google-drive MCP.
3. **Fetch supporting docs.** Hand off to `@adk:context-gather`. Output goes to `.temp/task-<slug>/context.md`.
4. **Read code/configs the doc claims to describe.** Resolve every cited file path / URL. Extract real current state.
5. **Per dimension pass:**
   - **Accuracy** — every factual claim verified against code/config; flag drift.
   - **Freshness** — last-updated timestamps, deprecated APIs, dead links.
   - **Structure** — headings hierarchy, navigability, scannable.
   - **Completeness** — gaps (assumed knowledge, missing prereqs, missing failure modes).
   - **Readability** — sentence length, jargon, redundant prose, terminology consistency.
6. **Tier findings** (per `references/severity-ladder.md`): Blocker / Critical / Should / May / Nitpick / Question / Praise.
7. **Phase 3 validator.** Findings have evidence (cited file:line or URL).
8. **Decide post-mode.** Default dry-run.
9. **(`fix` mode):** apply auto-fixable findings (typos, broken links, deprecated API names, version drift) directly. Re-run the review to confirm zero residual.
10. **(`post` mode for Confluence/GDoc):** post inline comments + footer summary via the appropriate MCP.
11. **Phase 4 validator.**
12. **Report.**

## Mode contract

- `--mode review` (default): write `.temp/task-<slug>/review.md`. Never edit source.
- `--mode fix`: edit source where authoritative (the markdown file in this repo). For Confluence/GDoc, fix-mode is rejected (would silently overwrite live content) — use `post` mode to leave comments instead.
- `--mode auto`: same as review then offer to run fix.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/review.md` | Findings, severity-tiered |
| `.temp/task-<slug>/context.md` | Supporting docs (if gathered) |
| Live page | Comments (only in `--post-mode post`) |

## Anti-patterns

- Reviewing the doc without reading the code it describes.
- Tagging "outdated" without showing the new state.
- Auto-fixing a Confluence page (high blast radius; use comments instead).
- Skipping supporting-docs when the user provided them.
- Confusing style critique (Nitpick) with accuracy issues (Blocker).

## References

Standard set + `references/severity-ladder.md`, `references/dimension-passes.md`, `references/post-comment-format.md`.


## Related skills

- [`context-gather`](./skill-context-gather.md) — `@adk:context-gather` (a.k.a. `adk-context-gather`)
- [`docs-review`](./skill-docs-review.md) — `@adk:docs-review` (a.k.a. `adk-docs-review`)
- [`docs-write`](./skill-docs-write.md) — `@adk:docs-write` (a.k.a. `adk-docs-write`)
- [`review`](./skill-review.md) — `@adk:review` (a.k.a. `adk-review`)
- [`review-pr`](./skill-review-pr.md) — `@adk:review-pr` (a.k.a. `adk-review-pr`)
