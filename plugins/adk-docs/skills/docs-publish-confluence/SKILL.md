---
name: docs-publish-confluence
description: |
  Publish an existing markdown document as a Confluence page (create or update) via the workspace Atlassian connector — NO MCP ships with this plugin. Supports parent-page placement, label management, and post-publish re-fetch verification. Idempotent: match-by-title-and-parent before creating; same input always converges to the same page rather than multiplying duplicates on retry. NEVER overwrites a page authored by a human (checks page metadata; refuses if non-bot last-editor unless the user explicitly opts in). NEVER auto-changes restrictions or sharing (read-only and view-restriction changes are human decisions). Use when the destination is Confluence and you already have the markdown. Do NOT use for the authoring step itself (/adk-docs:docs-write), for reading an existing Confluence page (use the workspace Atlassian connector directly), or for publishing to Google Drive (/adk-docs:docs-publish-gdrive).
metadata:
  category: docs
  kind: task
  layer: 5
  modes: [auto, interactive]
  needs_mcp: [atlassian-workspace]
  needs_meta_info: [docs]
argument-hint: "<md-file> [--space <space>] [--parent <page-title>] [-i]"
---

# docs-publish-confluence — publish markdown to Confluence

Idempotent publisher. Same input → same page. Never overwrites a human-
authored page. Never changes sharing or restrictions.

## When to use

- Publish a draft from `/adk-docs:docs-write` to a Confluence space
- Refresh an existing Confluence page from updated markdown
- "Publish the runbook to Confluence space ENG under 'Runbooks' parent"

## When NOT to use

| Not this → | Use this |
| --- | --- |
| author the markdown | `/adk-docs:docs-write` |
| read a Confluence page for review | `/adk-docs:docs-review` (with the page URL) |
| publish to Google Drive | `/adk-docs:docs-publish-gdrive` |
| change page restrictions / sharing | **out of scope** — manual |

## Common prompts

- "publish to Confluence space ENG"
- "create a page under Engineering Home"
- "publish this runbook to Confluence"
- "publish the ADR to the ADR parent page"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<md-file>` | yes | local markdown file path |
| `--space <space>` | no | `docs.md.default_confluence_space` |
| `--parent <page-title>` | no | `docs.md.default_confluence_parent` |
| `-i` / `--interactive` | no | off |

## Workflow

```
Phase 0 — prompt expansion
  - Read <md-file>; resolve slug from filename; create .temp/task-<slug>/.
  - Resolve space + parent from CLI or docs.md defaults.

Phase 1 — preflight
  - adk-info --check (docs topic must parse).
  - Workspace Atlassian connector reachable (`claude mcp list`).
  - Space exists (connector query).
  - Parent page exists in the space (connector query by title).

Phase 2 — convert
  - Markdown -> Confluence storage format (XHTML).
    See references/markdown-to-confluence.md.
  - Extract frontmatter labels -> label list.
  - Write converted content to .temp/task-<slug>/storage.xhtml.

Phase 3 — idempotent existence check
  - Query Confluence: "page with title <title-from-frontmatter-or-H1>
    under parent <parent> in space <space>?"
  - If found: capture page id, version, last-editor.
    - If last-editor is NOT a bot (adk- or atlassian-user-*), flag as
      human-authored — requires user opt-in to overwrite.
  - If not found: new-page path.

Phase 4 — publish (ask-once gate)
  - Ask the user once (even under --auto):
    "Publish <md-file> as <title> in <space> / <parent>? (new | update | abort)"
  - On confirm:
    - New page: connector create-page with storage.xhtml + labels + parent.
    - Update: connector update-page with storage.xhtml + labels (new version).

Phase 5 — verify
  - Re-fetch the page (by id).
  - Compare rendered storage with storage.xhtml (modulo connector
    normalization).
  - Confirm labels applied.
  - Log the final page URL + version in the report.
```

See `references/workflow.md`.

## Persona

> "Idempotent publisher. Same input → same Confluence page." Never
> creates a duplicate page on retry. Never overwrites a page authored
> by a human without explicit opt-in.

See `references/persona.md`.

## Constitution

**Must do:**

1. Match-by-title-and-parent BEFORE creating. If the match exists,
   update; don't create a duplicate.
2. Convert markdown to Confluence storage format (XHTML) per
   `references/markdown-to-confluence.md` — not paste-in raw
   markdown.
3. Verify post-publish by re-fetching the page and comparing.
4. Preserve existing labels; add the skill's own labels on top.
5. Under any mode (including `--auto`), ask once before the first
   publish — this is a shared-state write.

**Must not do:**

1. Overwrite a page whose `lastEditor` is a human user, unless the
   user explicitly opts in this run.
2. Change page restrictions or sharing. Those are human decisions.
3. Create a duplicate page on retry.
4. Auto-publish multiple pages in one run (hard cap: 1 page per
   invocation; for batches, loop with user approval).
5. Delete pages (out of scope; manual).
6. Move pages to a different parent (out of scope unless explicitly
   requested — that's a separate --parent change with confirmation).

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Creating a duplicate page on retry because we didn't query first.
- Overwriting a human-authored page without confirmation.
- Pasting raw markdown as Confluence storage (it partly works,
  partly doesn't — the converter catches the gaps).
- Auto-setting restrictions to "anyone" or "space-only".

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/prompt.txt` | Verbatim user prompt + timestamp |
| `.temp/task-<slug>/storage.xhtml` | Converted Confluence storage format |
| `.temp/task-<slug>/existence-check.md` | Result of the match-by-title-and-parent query |
| `.temp/task-<slug>/publish-plan.md` | New or update plan (shown before the ask-once gate) |
| `.temp/task-<slug>/published.md` | Post-publish: page id, URL, version, labels |
| `.temp/task-<slug>/report.md` | Final consolidated report |

See `references/output-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Idempotent-publisher persona |
| `references/workflow.md` | Phase 0–5 stage detail |
| `references/modes.md` | `--auto / -i` for this skill |
| `references/interaction-contract.md` | Canonical interaction contract (byte-identical) |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | Worked create + update scenarios |
| `references/output-format.md` | Artifact shapes + final report |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase gates (incl. post-publish verify) |
| `references/how-it-works.md` | Mermaid flow |
| `references/clarifying-questions.md` | Questions under `-i`; defaults under `--auto` |
| `references/markdown-to-confluence.md` | Markdown → XHTML storage format conversion rules |
| `references/idempotent-publish.md` | Match-by-title-and-parent; human-editor safeguard; labels |

## Additional links

- The workspace Atlassian connector's documented endpoints for create-page, update-page, set-labels, get-page-by-title.
- Atlassian's storage-format spec (quoted ≤15 words; linked for the rest).
