# `docs-publish-confluence` — output format

## Per-turn status

```
[adk-docs:docs-publish-confluence] task=<slug> phase=<0|1|2|3|4|5> space=<space> parent="<parent>" action=<new|update|defer> mode=<auto|interactive>
```

## `storage.xhtml`

The converted Confluence storage format. Rules:

- UTF-8, no BOM.
- Top-level nodes are block elements (`<h1>`, `<p>`, `<ul>`, etc.).
- Code fences → `ac:structured-macro` with language parameter.
- Mermaid fences → `ac:structured-macro ac:name="mermaid"` with
  `ac:plain-text-body CDATA`.
- Admonitions (`> [!NOTE]`, `> [!WARNING]`, `> [!TIP]`) →
  `ac:structured-macro ac:name="info"` / `"warning"` / `"tip"`
  panels.

## `existence-check.md`

```markdown
# Existence check — <slug>

| Field | Value |
| --- | --- |
| Query | `space=ENG, parent="Runbooks", title="Runbook: Platform on-call rotation"` |
| Found | yes |
| Page id | 12345 |
| Version | 3 |
| Last editor | adk-bot@acme.com |
| Is bot | true |
| Last updated | 2026-04-25T09:14:02Z |
| Existing labels | [runbook, platform] |
| Action | update |
```

## `publish-plan.md`

```markdown
# Publish plan — <slug>

## Target
- Space: `ENG`
- Parent: `Runbooks` (page id 8801)
- Title: `Runbook: Platform on-call rotation`
- Action: `update` (page id 12345)

## Content
- Source: `docs/runbooks/oncall.md`
- Converted: `storage.xhtml` (2.1 KB)

## Labels
- Existing: [runbook, platform]
- Add: [adk-published]
- Final: [runbook, platform, adk-published]

## Diff summary (for updates)
- `+ 3 lines`
- `- 1 line`
- `~ 2 lines modified`
- See `.temp/task-<slug>/diff.txt` for the full diff.
```

## `published.md`

```markdown
# Published — <slug>

- page_id: 12345
- version: 4
- url: https://acme.atlassian.net/wiki/spaces/ENG/pages/12345/Runbook+Platform+on-call+rotation
- labels: [runbook, platform, adk-published]
- verified_at: 2026-05-03T13:01:22Z
- verification: match (storage re-fetch OK modulo macro ids)
```

## Final report

`.temp/task-<slug>/report.md`:

```markdown
# docs-publish-confluence report — <slug>

## Result
Updated existing Confluence page "Runbook: Platform on-call
rotation" (id 12345) to version 4.

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | space | ENG | CLI arg |
| 0 | parent | Runbooks | CLI arg |
| 3 | action | update | existing page; last editor is bot |
| 4 | publish | yes | user confirmed |

## Validation evidence
- connector: reachable
- existence check: 1 match; last-editor bot
- post-publish re-fetch: storage matches modulo macro ids
- labels: union applied

## Residual risk / follow-ups
- None

## Artifact index
.temp/task-<slug>/
  prompt.txt
  storage.xhtml
  existence-check.md
  publish-plan.md
  diff.txt
  published.md
  report.md

Final URL:
https://acme.atlassian.net/wiki/spaces/ENG/pages/12345/...
```
