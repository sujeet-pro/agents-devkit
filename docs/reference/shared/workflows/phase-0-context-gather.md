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
- `~/.config/adk/overrides.yaml` (workspaces, repos, data sources).

## Steps

1. **Run `scripts/url_classifier.py`** on the prompt. Get back JSON: `{urls: [...], local_paths: [...], freeform: "..."}`.
2. **Pick the working repo**: match `cwd` against `overrides.yaml.repos[*].path`. If no match: ask the user to confirm or specify a repo.
3. **Pick the active workspace**: derive from the matched repo's `workspace` field. If multi-workspace user is ambiguous: ask.
4. **Resolve task-slug**: build `<skill>-<discriminator>` where discriminator comes from input (Jira key, PR number, repo+date, etc.).
5. **Create `<repo>/.temp/<task-slug>/`** (or `~/code/agents-devkit/.temp/<task-slug>/` if not in a repo).
6. **Fan-out fetch each URL in parallel** (cap 4 concurrent) via the matching MCP. See `shared/input-classifiers/<type>.md` for each URL type's fetcher.
7. **Merge results** into `<task-slug>/context.md`. One section per source. Quote ≤15 words per claim; link out for the rest.
8. **Optional RAG enrichment**: if `rag.enabled: true` AND prompt matches `rag.trigger_keywords` (or user explicitly says "check our internal docs"), query the RAG MCP with the prompt + key entities. Merge results tagged `[source: rag]`.
9. **Load relevant guidelines**: based on detected task category (frontend / api / data / observability / security / …), pre-load matching `shared/guidelines/*.md` into the working context.

## Output

`<task-slug>/context.md` layout:

```markdown
# context for <task-slug>

## working repo
- name: storefront-bff (from overrides.yaml.repos[0])
- path: /Users/sujeet/code/quince/storefront-bff
- workspace: quince-work

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
