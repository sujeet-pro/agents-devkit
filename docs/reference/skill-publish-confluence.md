---
title: 'publish-confluence'
description: 'Publish a markdown document as a Confluence page (create or update) via the atlassian-confluence MCP server, with parent-page placement, label management, and post-publish verification.'
artifact_kind: skill
skill_name: publish-confluence
category: publish
---
# publish-confluence

Publish a markdown document as a Confluence page (create or update) via the atlassian-confluence MCP server, with parent-page placement, label management, and post-publish verification. Use when the destination is Confluence and the source is markdown produced by adk-docs-write or by hand. Do not use to author the markdown source (use adk-docs-write) or to publish to Google Drive (use adk-publish-gdrive).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-publish-confluence` form via `agents-skills/`.

```text
/adk:publish-confluence            # interactive run (Claude Code)
/adk:publish-confluence --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-publish-confluence` (resolved through the
`agents-skills/adk-publish-confluence/` symlink).

## Source

Direct from `skills/publish-confluence/SKILL.md` — this page is auto-generated.

Standalone task skill under the `@adk:publish` (a.k.a. `adk-publish`) category router. Publishes markdown to Confluence via the `atlassian-confluence` MCP server (preferred) or REST API, then verifies the page landed correctly.

## When to use

- Publishing a markdown doc as a new Confluence page.
- Updating an existing Confluence page from a markdown source.
- Adding or replacing labels on a Confluence page.
- Moving a page under a different parent in the same space.

## When NOT to use

- Authoring the markdown source -> `@adk:docs-write` (a.k.a. `adk-docs-write`)
- Publishing to Google Drive -> `@adk:publish-gdrive` (a.k.a. `adk-publish-gdrive`)
- Internal repo doc only -> just `adk-docs-write` to a tracked path
- Confluence Server / Data Center (different API surface) - this skill targets Confluence Cloud

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<action>` | yes | `page-create` / `page-update` / `page-move` / `label-set` |
| `<source>` | yes for page actions | Path to markdown file |
| `<space>` | yes for `page-create` | Confluence space key |
| `<parent>` | optional | Parent page id or title for `page-create` / `page-move` |
| `<page-id>` | yes for `page-update` / `page-move` / `label-set` | Existing Confluence page id |
| `<title>` | optional | Override the page title (default: first H1 in markdown) |
| `<labels>` | optional | Comma-separated labels |
| `--auto` | optional | Skip confirmations on non-destructive actions |

## Workflow

1. **Confirm intent** - restate action, source path, target space/parent/page id, title, labels. Approval gate unless `--auto`.
2. **Check tooling** - verify `atlassian-confluence` MCP is configured. If not, fall back to REST with `CONFLUENCE_BASE_URL`, `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN` from env. Stop with a clear install/config message if neither is available.
3. **Read source** - load the markdown. Extract title from the first `# H1` if none was supplied.
4. **Convert** - convert markdown -> Confluence storage format (or ADF, depending on MCP). Preserve:
   - headings (mapped 1:1)
   - lists (ordered + unordered, nested)
   - tables (with header row)
   - fenced code blocks (with language tag)
   - links (absolute URLs preserved; intra-doc anchors mapped where possible)
   - inline code, emphasis, strong
   - images (uploaded as attachments and referenced - flag if the source path is missing)
5. **Apply action** - create or update the page; place under parent if specified; set labels.
6. **Verify (per `publish-confluence-validator.md`)** - re-fetch the page and confirm: title matches, body content present, parent matches, labels present, version incremented.
7. **Report** - lead with the page URL; include action, version, verification status.

## Action playbooks

### page-create

```
POST /wiki/api/v2/pages
{
  "spaceId": "<numeric space id>",
  "title": "<title>",
  "parentId": "<parent id, optional>",
  "body": { "representation": "storage", "value": "<storage format>" }
}
```

### page-update

Always pass the current `version.number + 1`:

```
PUT /wiki/api/v2/pages/{id}
{
  "id": "<page-id>",
  "status": "current",
  "title": "<title>",
  "version": { "number": <current+1> },
  "body": { "representation": "storage", "value": "<storage format>" }
}
```

### page-move

```
PUT /wiki/api/v2/pages/{id}/move
{ "parentId": "<new parent id>", "position": "append" }
```

### label-set

```
PUT /wiki/api/v1/content/{id}/label   # add
{ "prefix": "global", "name": "<label>" }

DELETE /wiki/api/v1/content/{id}/label/{name}   # remove
```

## Output format

```
## Confluence action: <action>
- Page URL: <url>
- Page id: <id>
- Space: <space key>
- Parent: <parent title or id>
- Version: <new version>
- Tool used: <atlassian-confluence MCP | REST>

## Verification
- Title matches: <YES>
- Body landed: <YES> (length: <chars>)
- Labels: <list>

## Follow-up
- <e.g. "share with @alice", "update related runbook">
```

## Hard rules

- Always increment `version.number` for `page-update`. Stale versions cause silent failures.
- Never delete a page from this skill. Page deletion is an explicit, separate action.
- Always verify after publishing - Confluence accepts malformed storage format and renders blanks.
- Title comes from the H1 unless overridden; never silently re-title an existing page.
- Image attachments must be uploaded before the page references them; otherwise the page renders broken images.

## Markdown -> Confluence quirks

- Confluence storage format does not support nested code fences inside list items in some renderers. If a list item must contain code, prefer a code-block macro.
- Mermaid diagrams render via the Mermaid macro on Confluence Cloud; fall back to embedded SVG if the macro is unavailable.
- Anchor links are page-scoped; cross-page anchors require absolute URLs.

## Anti-patterns

- Updating without re-fetching the current version - causes 409s and silent overwrites.
- Pasting raw markdown when the API expects storage format / ADF.
- Publishing without verifying the rendered output.
- Re-titling an existing page without coordinating with watchers (it changes the URL slug).
- Hard-coding a parent page title; ids are stable, titles are not.

## Examples

```
adk-publish-confluence page-create \
  --source .temp/drafts/runbook-deploy.md \
  --space ENG --parent "Runbooks" --labels runbook,deploy
```

```
adk-publish-confluence page-update \
  --source .temp/drafts/runbook-deploy.md \
  --page-id 123456789
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/publish-confluence-clarifying-questions.md`) and reports the choices.

1. **What is the source markdown (path)?** — _How to pick:_ Required. Should already be authored via adk-docs-write or `@adk:plan-spec` (a.k.a. `adk-plan-spec`).
2. **What space and parent page?** — _How to pick:_ Space = required. Parent = pick the existing topical parent; create one only with explicit approval.
3. **New page or update existing?** — _How to pick:_ If a same-titled page exists under the parent, default to update (with version bump) rather than duplicate.

**Default report:** Page URL + create/update verdict + version number + verification (title/body match expected).

**Detailed report (on request or `--verbose`):** Add: storage-format diff vs prior version, attachment list, links from the new page that resolve.

**Artifact:** `confluence-page` — The Confluence page is the artifact. Conversion log + diff in .temp/.

**Artifact path:** .temp/notes/publish-confluence-<slug>.md (conversion + diff log)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/publish-confluence-clarifying-questions.md`) and reports the choices.

1. **What is the source markdown (path)?** — _How to pick:_ Required. Should already be authored via adk-docs-write or adk-plan-spec.
2. **What space and parent page?** — _How to pick:_ Space = required. Parent = pick the existing topical parent; create one only with explicit approval.
3. **New page or update existing?** — _How to pick:_ If a same-titled page exists under the parent, default to update (with version bump) rather than duplicate.

## Default vs detailed output

**Default report:** Page URL + create/update verdict + version number + verification (title/body match expected).

**Detailed report (on request or `--verbose`):** Add: storage-format diff vs prior version, attachment list, links from the new page that resolve.

**Artifact:** `confluence-page` — The Confluence page is the artifact. Conversion log + diff in .temp/.

**Artifact path:** .temp/notes/publish-confluence-<slug>.md (conversion + diff log)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/publish-confluence-anti-patterns.md` | Things to avoid when running this skill. |
| `references/publish-confluence-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/publish-confluence-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/publish-confluence-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/publish-confluence-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/publish-confluence-mcp-fallback.md` | Preferred MCP server and the manual fallback when it is missing. |
| `references/publish-confluence-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/publish-confluence-persona.md` | The agent persona that drives this skill. |
| `references/publish-confluence-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/publish-confluence-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-publish, post-publish) this skill MUST run. |

<!-- adk:references:end -->


## Related skills

- [`docs-write`](./skill-docs-write.md) — `@adk:docs-write` (a.k.a. `adk-docs-write`)
- [`plan-spec`](./skill-plan-spec.md) — `@adk:plan-spec` (a.k.a. `adk-plan-spec`)
- [`publish`](./skill-publish.md) — `@adk:publish` (a.k.a. `adk-publish`)
- [`publish-gdrive`](./skill-publish-gdrive.md) — `@adk:publish-gdrive` (a.k.a. `adk-publish-gdrive`)
