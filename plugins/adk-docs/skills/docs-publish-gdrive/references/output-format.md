# `docs-publish-gdrive` — output format

## Per-turn status

```
[adk-docs:docs-publish-gdrive] task=<slug> phase=<0|1|2|3|4|5> folder=<id> format=<gdoc|md|pdf> action=<new|update|defer> mode=<auto|interactive>
```

## Converted artifact

| Format | Path | Notes |
| --- | --- | --- |
| `gdoc` | `.temp/task-<slug>/converted.gdoc.json` | GDoc ops (inserts + paragraphs + bullet lists + code fences) |
| `md` | `.temp/task-<slug>/converted.md` | Frontmatter stripped |
| `pdf` | `.temp/task-<slug>/converted.pdf` | Rendered via pandoc |

## `existence-check.md`

```markdown
# Existence check — <slug>

| Field | Value |
| --- | --- |
| Query | folder=1AbCdEf, name="Exports v1 — design", mime="application/vnd.google-apps.document" |
| Found | yes |
| Item id | 1XyZ123 |
| Revision | 7 |
| Last editor | adk-service@acme.com |
| Is bot | true |
| Last modified | 2026-04-25T09:14:02Z |
| Action | update |
```

## `publish-plan.md`

```markdown
# Publish plan — <slug>

## Target
- Folder: 1AbCdEf (Design Docs)
- Name: Exports v1 — design
- Mime: application/vnd.google-apps.document
- Action: update (item id 1XyZ123, revision 7)

## Content
- Source: docs/design/exports-v1.md
- Converted: converted.gdoc.json (ops: 62)

## Sharing
- Will NOT be changed by this skill.
- Pre-publish permissions: [domain:acme.com:reader] + service account.
```

## `published.md`

```markdown
# Published — <slug>

- item_id: 1XyZ123
- revision: 8
- url: https://docs.google.com/document/d/1XyZ123/edit
- mime: application/vnd.google-apps.document
- size: 14312 bytes
- verified_at: 2026-05-03T13:01:22Z
- verification: name + mime + parent OK
```

## `sharing-snapshot.md`

```markdown
# Sharing snapshot — <slug>

## Pre-publish
| Who | Role |
| --- | --- |
| domain:acme.com | reader |
| user:adk-service@acme.com (service account) | owner |

## Post-publish
| Who | Role |
| --- | --- |
| domain:acme.com | reader |
| user:adk-service@acme.com (service account) | owner |

## Drift
None. Invariant preserved.
```

## Final report

`.temp/task-<slug>/report.md`:

```markdown
# docs-publish-gdrive report — <slug>

## Result
Updated existing GDoc "Exports v1 — design" (id 1XyZ123) to
revision 8 in folder 1AbCdEf.

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | format | gdoc | CLI arg |
| 0 | folder | 1AbCdEf | CLI arg |
| 3 | action | update | existing bot-authored item |
| 4 | publish | yes | user confirmed |
| 5 | sharing | unchanged | snapshot match |

## Validation evidence
- connector: reachable
- existence check: 1 match; last-editor bot
- post-publish re-fetch: metadata matches
- sharing drift: none

## Residual risk / follow-ups
- None

## Artifact index
.temp/task-<slug>/
  prompt.txt
  source.md
  converted.gdoc.json
  existence-check.md
  publish-plan.md
  published.md
  sharing-snapshot.md
  report.md

Final URL:
https://docs.google.com/document/d/1XyZ123/edit
```
