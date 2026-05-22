---
title: 'workflows/phase-0-context-gather'
description: '- Raw user prompt + any URLs / paths / IDs in it.'
source: 'shared/workflows/phase-0-context-gather.md'
group: 'shared-workflows'
order: 6100
---
# shared/workflows/phase-0-context-gather

> Source: `shared/workflows/phase-0-context-gather.md`

# workflow: Phase 0 — context gather

> The fan-out step. Every polymorphic skill runs this first. Reads everything referenced in the user's input.

## Inputs

- Raw user prompt + any URLs / paths / IDs in it.
- Current working directory (resolves `<repo>/.adk/` + `<repo>/ai-guidelines/`).
- `~/.agents-devkit/config/core.yaml (+ repos.md + connectors/*.md)` (workspaces, repos, data sources).

## Steps

1. **Run `scripts/url_classifier.py`** on the prompt. Get back JSON: `{urls: [...], local_paths: [...], freeform: "..."}`.
2. **Pick the working repo**: match `cwd` against `repos.md frontmatter repos[*].path`. If no match: ask the user to confirm or specify a repo.
3. **Pick the active workspace**: derive from the matched repo's `workspace` field. If multi-workspace user is ambiguous: ask.
4. **Resolve task-slug + task folder** via `scripts/adk_task_slug.py --skill <stem> --input <prompt> --create --json`. The script picks the right root per `shared/paths.md` (repo-bound vs global), derives the discriminator from the input (Jira key, PR number, repo+date, etc.), and returns the absolute path. Skills that are **always global** (`pr-review`, `investigate`, `setup`, `improve`, `explain`) pass `--scope global`; skills that are **always repo-bound** (`implement`, `document`) pass `--scope repo`; **hybrid** skills (`review`, `sync`) pass `--scope auto` and let the script decide.
5. **Use the returned `task_dir`** as the working dir for the rest of this skill run. Every artifact path below is relative to it.
6. **Fan-out fetch each URL in parallel** (cap 4 concurrent) via the matching MCP. See `shared/input-classifiers/<type>.md` for each URL type's fetcher.
7. **Merge results** into `<task_dir>/context.md`. One section per source. Quote ≤15 words per claim; link out for the rest.
8. **Optional RAG enrichment**: if `rag.enabled: true` AND prompt matches `rag.trigger_keywords` (or user explicitly says "check our internal docs"), query the RAG MCP with the prompt + key entities. Merge results tagged `[source: rag]`.
9. **Load relevant guidelines**: based on detected task category (frontend / api / data / observability / security / …), pre-load matching `shared/guidelines/*.md` into the working context.

## Output

`<task_dir>/context.md` layout:

```markdown
# context for <task-slug>

## working repo
- name: storefront-bff (from repos.md repos[0])
- path: /Users/sujeet/code/acme/storefront-bff
- workspace: personal-work

## sources fetched
### [jira] SF-1234 — coupon engine
fetched: 2026-05-18T10:00Z
summary: 2-sentence summary
key fields: status=In Progress, assignee=sujeet, sprint=Sprint 47
acceptance criteria:
  - …
link: https://acme.atlassian.net/browse/SF-1234

### [confluence] storefront-bff design doc
fetched: 2026-05-18T10:00Z
summary: 2-sentence summary
relevant section: "Coupon engine" — at https://acme.atlassian.net/wiki/...

### [github-pr] #456 — prior coupon work
fetched: 2026-05-18T10:00Z
summary: …
relevant diff: services/coupon.py +120/-30
link: https://github.com/...

### [rag] internal coupon policy doc
fetched: 2026-05-18T10:00Z
chunks: 3
relevance: high
quoted: "…" (link)

### [skipped] [slack] — credentials file missing token
gap: SLACK_BOT_TOKEN not exported by $SLACK_CREDENTIALS_FILE
```

## Anti-patterns

- Fetching transitively. Follow links the user gave you. **Don't** follow links inside fetched content. One hop.
- Embedding fetched bodies. Quote tightly, link for the rest. Save tokens.
- Failing the whole phase on one source. If 4 of 5 sources fetched and 1 failed, report the failure and proceed.
- Auto-running expensive queries (full DD log dump, Snowflake table scan). The user did not ask for that — only fetch what each URL points at.
