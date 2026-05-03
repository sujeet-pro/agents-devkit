---
title: 'adk-docs:docs-publish-gdrive'
description: '  Publish a markdown document to Google Drive as a Google Doc, plain markdown file, or PDF via the workspace Google Drive connector (NO MCP ships with this plugin). Supports folder placement, format selection, and post-publish re-fetch verification. Idempotent via match-by-name-and-parent: same input converges to the same Drive item rather than multiplying duplicates on retry. NEVER changes sharing permissions automatically — sharing is a human action per policy; the skill publishes into the requested folder and inherits that folder''s sharing. NEVER moves or deletes existing items. Use when the destination is Google Drive. Do NOT use for Confluence (/adk-docs:docs-publish-confluence), for reading an existing GDoc (use the workspace Google Drive connector directly), or for the authoring step itself (/adk-docs:docs-write).'
plugin: 'adk-docs'
skill: 'docs-publish-gdrive'
source: 'plugins/adk-docs/skills/docs-publish-gdrive/SKILL.md'
group: 'docs-skills'
order: 3106
---
# adk-docs:docs-publish-gdrive

## Source

`plugins/adk-docs/skills/docs-publish-gdrive/SKILL.md`

## Skill Body

# docs-publish-gdrive — publish markdown to Google Drive

Idempotent publisher. Same input → same Drive item. Never changes
sharing. Never moves or deletes.

## When to use

- Publish a draft from `/adk-docs:docs-write` to a Google Drive
  folder as a GDoc, .md file, or PDF
- Refresh an existing GDoc from updated markdown
- "Publish the design doc to GDrive folder <folder-id>"

## When NOT to use

| Not this → | Use this |
| --- | --- |
| author the markdown | `/adk-docs:docs-write` |
| read a GDoc for review | `/adk-docs:docs-review` (with the GDoc URL) |
| publish to Confluence | `/adk-docs:docs-publish-confluence` |
| change sharing permissions | **out of scope** — manual per security policy |
| move a file to a different folder | **out of scope** |
| delete a GDoc | **out of scope** |

## Common prompts

- "publish to GDrive"
- "publish to GDrive folder 1AbC…"
- "publish as GDoc"
- "publish as PDF to <folder>"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<md-file>` | yes | local markdown file path |
| `--folder <folder-id>` | no | `docs.md.default_gdrive_folder_id` |
| `--format <gdoc\|md\|pdf>` | no | `gdoc` |
| `-i` / `--interactive` | no | off |

## Workflow

```
Phase 0 — prompt expansion
  - Read <md-file>; resolve slug from filename; create .temp/task-<slug>/.
  - Resolve folder + format from CLI or docs.md defaults.

Phase 1 — preflight
  - adk-info --check (docs topic must parse).
  - Workspace Google Drive connector reachable (`claude mcp list`).
  - Folder exists + is writable by the connector's service account.

Phase 2 — convert
  - --format gdoc: md -> GDoc ops (per references/markdown-to-gdoc.md).
  - --format md:   upload .md verbatim (minor frontmatter strip).
  - --format pdf:  render md to PDF via pandoc (or diagramkit's PDF mode).

Phase 3 — idempotent existence check
  - Query: item with name <basename-for-format> in folder <folder-id>?
  - If found: capture item id, revision, last-editor, last-modified.
    - If last-editor is NOT a bot, flag as human-authored; requires
      explicit opt-in to overwrite.
  - If not found: create path.

Phase 4 — publish (ask-once gate)
  - Ask the user once (even under --auto):
    "Publish <md-file> as <target-name> (<format>) to <folder-id>?
    (new | update | defer)"
  - On confirm: connector create/update.

Phase 5 — verify + sharing-policy enforcement
  - Re-fetch the item's metadata (name, mime, parents, size).
  - Confirm sharing/permissions were NOT changed by the skill
    (per references/sharing-policy.md — read current, compare to
    pre-publish; refuse silently if any drift; surface).
  - Log final URL + metadata.
```

See `references/workflow.md`.

## Persona

> Same as `docs-publish-confluence` — idempotent publisher, match-
> before-create. One extra rule on top: **NEVER changes sharing
> permissions automatically.** Sharing is a human action.

See `references/persona.md`.

## Constitution

**Must do:**

1. Match-by-name-and-parent-folder before creating. Idempotent.
2. Convert markdown to the requested format per
   `references/markdown-to-gdoc.md`.
3. Verify post-publish by re-fetching metadata.
4. Under any mode (including `--auto`), ask once before the first
   publish.
5. Enforce `references/sharing-policy.md` — confirm no sharing
   change occurred; if the connector even *offered* a sharing
   change, refuse.

**Must not do:**

1. Change sharing permissions. Ever. Not even "add myself as
   editor". Sharing is manual.
2. Overwrite a human-authored Drive item without explicit opt-in.
3. Create duplicate items on retry.
4. Move items between folders.
5. Delete items.
6. Batch-publish multiple files in one run (cap: 1 per invocation).

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Calling a sharing endpoint "just to check"; the skill never
  touches sharing.
- Creating a duplicate "foo (1).gdoc" on retry.
- Auto-overwriting a human-authored GDoc.
- Publishing outside the org domain (an org-scoped guardrail in
  `references/sharing-policy.md`).

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/prompt.txt` | Verbatim user prompt + timestamp |
| `.temp/task-<slug>/source.md` | Audit copy of the input |
| `.temp/task-<slug>/converted.<ext>` | Converted artifact (`.gdoc.json` ops, `.md`, or `.pdf`) |
| `.temp/task-<slug>/existence-check.md` | Result of the match-by-name query |
| `.temp/task-<slug>/publish-plan.md` | New or update plan |
| `.temp/task-<slug>/published.md` | Post-publish: item id, URL, revision |
| `.temp/task-<slug>/sharing-snapshot.md` | Pre and post sharing metadata (must match) |
| `.temp/task-<slug>/report.md` | Final consolidated report |

See `references/output-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Idempotent-publisher persona (sharing-never variant) |
| `references/workflow.md` | Phase 0–5 stage detail |
| `references/modes.md` | `--auto / -i` for this skill |
| `references/interaction-contract.md` | Canonical interaction contract (byte-identical) |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | Worked create + update scenarios (gdoc / md / pdf) |
| `references/output-format.md` | Artifact shapes + final report |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase gates (incl. sharing-snapshot check) |
| `references/how-it-works.md` | Mermaid flow |
| `references/clarifying-questions.md` | Questions under `-i`; defaults under `--auto` |
| `references/markdown-to-gdoc.md` | Markdown → GDoc ops / .md upload / .pdf render |
| `references/sharing-policy.md` | Hard rules: never auto-changes sharing |

## Additional links

- The workspace Google Drive connector's documented endpoints for
  create / update / get-metadata. Quoted ≤15 words; linked for the
  rest.
