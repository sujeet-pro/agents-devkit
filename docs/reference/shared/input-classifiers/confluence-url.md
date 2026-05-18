---
title: 'input-classifiers/confluence-url'
description: '```'
source: 'shared/input-classifiers/confluence-url.md'
group: 'shared-input-classifiers'
order: 6200
---
# shared/input-classifiers/confluence-url

> Source: `shared/input-classifiers/confluence-url.md`

# input classifier: Confluence URL

## Pattern

```
https?://<site>.atlassian.net/wiki/spaces/<SPACE>/pages/<pageId>/<title-slug>
https?://<site>.atlassian.net/wiki/spaces/<SPACE>/pages/<pageId>
```

## Fetch via

`adk-mcp-atlassian` → `getConfluencePage(pageId)` (returns content in storage format / ADF / Markdown depending on flag).

## Extract into context.md

```markdown
### [confluence] <title>
url: <full URL>
space: <SPACE>
page id: <pageId>
last edited: <date> by <author>
labels: [...]
summary (first 80 words of body, plain text): <quote>
key sections (h2/h3):
  - <section title> — <one-line summary>
linked pages: [...]
attachments: <count, names>
```

## Hints

- `/adk-implement`: if the page is a TDD/spec, parse it into acceptance criteria.
- `/adk-document --type adr | --type runbook`: if updating, fetch the current version first.
- `/adk-sync --read`: this is the primary read path.

## Anti-patterns

- Don't paste the entire page body into context. Quote sparingly; link out.
- If the page has attachments (images, especially), note their existence but don't fetch unless asked.
