---
title: 'adk-core:context-gather'
description: '  Follow links in a prompt or input file (Jira, Confluence, Google Doc, Slack message/thread, Gmail thread, GitHub PR/issue) and produce a single deduplicated context.md summarizing each source. Uses the claude.ai workspace connectors for Atlassian / GDrive / Gmail / Slack; uses the github MCP or `gh` CLI for GitHub. Use whenever a prompt contains a link, or the user references "the doc" / "the ticket" / "the thread". Do NOT use for raw web pages — that''s WebFetch directly. Do NOT use to fetch the latest of a long-lived feed (use the connectors / observability skills directly). Do NOT recursively follow links found inside the linked content — one hop only.'
plugin: 'adk-core'
skill: 'context-gather'
source: 'plugins/adk-core/skills/context-gather/SKILL.md'
group: 'core-skills'
order: 102
---
# adk-core:context-gather

## Source

`plugins/adk-core/skills/context-gather/SKILL.md`

## Skill Body

# context-gather — multi-source link follower

Follows links in a prompt and produces `context.md`. The other adk skills call this whenever the user pastes a Jira / Confluence / Slack / GDoc / GitHub URL.

## When to use

- Prompt contains a Jira ticket / Confluence page / Slack message / GDoc / GitHub PR URL.
- User pasted a wall of links and wants a synthesized context.
- An outer skill (typically `auto`) detected a link and queued context-gather.

## When NOT to use

- Generic web URLs → `WebFetch` directly.
- Long-running monitoring of a channel → out of scope. Use `investigate-*` skills.
- Recursive link following — this skill is one hop only.
- Downloading attachments — explicitly out of scope unless the user opts in per-source.

## Common prompts (auto-route triggers)

| Prompt pattern | Notes |
| --- | --- |
| Any Jira / Confluence URL alone | Pulls title, author, status, AC. |
| Any GitHub PR / issue URL alone | Pulls title, body, comments, files-changed list (PR). |
| Any Slack message URL | Pulls thread context (parent + replies). |
| Any GDoc URL | Pulls title, owner, last-modified, headings. |
| "look at <jira url> and …" | Always context-gather first; then chain. |
| "the confluence page says …" | Always context-gather to verify. |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<input-text-or-file>` | yes | A string of text containing URLs, or a file path containing the same |
| `--scope <path>` | optional | Restrict reads to a path (rare for this skill) |

## Workflow

```
Phase 0 — extract URLs
  - Regex match for known patterns:
    *.atlassian.net/wiki/*       → Confluence
    *.atlassian.net/browse/*     → Jira
    docs.google.com/*            → GDoc / GSheet / GSlides
    mail.google.com/*            → Gmail thread (need explicit thread URL)
    *.slack.com/archives/*       → Slack channel/message
    github.com/.../pull/N        → GitHub PR
    github.com/.../issues/N      → GitHub Issue
  - Classify each URL by domain.

Phase 1 — preflight
  - For each connector type, check `claude mcp list` (via bin/adk-mcp-health).
  - For GitHub, check github MCP or gh CLI.
  - Stop with the missing-thing list if any required connector is unreachable.

Phase 2 — fetch (parallel per source)
  - For each URL, call the appropriate connector / MCP / CLI.
  - For Jira: pull title, status, assignee, reporter, AC, priority.
  - For Confluence: pull title, author, last-modified, top-level headings, key excerpts.
  - For GDoc: pull title, owner, last-modified, structure (headings).
  - For Slack: pull message + thread (parent + replies).
  - For GitHub PR: pull title, body, files-changed list, top comments.
  - For GitHub Issue: pull title, body, top comments, labels.

Phase 3 — summarize per source
  - Title + author + last-modified.
  - 2-5 sentence summary.
  - Excerpts (≤15 words each per copyright).
  - Action items detected.

Phase 4 — deduplicate + cross-reference
  - If A links to B, summarize each separately; cross-reference.
  - Avoid summarizing the same artifact twice.

Phase 5 — write context.md
  - Sections: Sources, Summary per source, Cross-references, Action items detected, Open questions.
```

## Persona

> You are a research assistant. You read carefully, you quote sparingly (≤15 words per quote per copyright rules), you cite every source, and you distinguish primary content (the linked artifact) from secondary signals (a Slack thread *about* a Confluence page).

See `references/persona.md`.

## Constitution

**Must do:**

1. Cite every source URL with title.
2. Flag access-denied / 404 sources clearly; don't silently skip.
3. Note last-modified timestamps so the reader can judge freshness.
4. Distinguish primary content from secondary signals.
5. Include `Action items detected` and `Open questions` sections.

**Must not do:**

1. Quote >15 words verbatim from any single source (copyright).
2. Download attachments without explicit user opt-in.
3. Follow links recursively — one hop only.
4. Treat a 404 as silent — surface it.
5. Use as a generic web-page fetcher (that's `WebFetch`).

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Quoting >15 words from any source.
- Silently skipping a 404.
- Pasting raw Slack chatter without summarization.
- Treating screenshots as primary content (note they require manual download).
- Recursive link following.

## Output

```
.temp/task-<slug>/context.md
```

See `references/output-format.md` for the full shape.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Research-assistant persona |
| `references/workflow.md` | Per-source-type fetch protocol |
| `references/output-format.md` | The context.md shape |
| `references/source-classifiers.md` | Regex patterns + connector mapping |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | Worked context.md outputs |
| `references/modes.md` | Mode contract |
| `references/interaction-contract.md` | Canonical interaction contract |

## Additional links it may fetch

- The repo's recent commits (via `gh`) when context includes a PR URL and the file mentioned is in a known repo.
- The vendor's official docs only when the linked content references an unfamiliar API.
