---
name: adk-publish-gdrive
description: Publish a markdown document to Google Drive as a Google Doc, plain markdown file, or PDF - via the google-drive MCP server, with folder placement, sharing settings, and post-publish verification. Use when the destination is Google Drive / Google Docs and the source is markdown produced by adk-docs-write or by hand. Do not use to author the markdown source (use adk-docs-write) or to publish to Confluence (use adk-publish-confluence).
---

# ADK Publish / Google Drive

Standalone task skill under the `adk-publish` category router. Publishes markdown to Google Drive via the `google-drive` MCP server, then verifies the file landed correctly.

## When to use

- Sharing a markdown doc as a Google Doc with a team or external reviewer.
- Updating an existing Google Doc from a markdown source.
- Uploading a markdown file or PDF to a specific Drive folder.
- Adjusting sharing permissions on a Drive item.

## When NOT to use

- Authoring the markdown source -> `adk-docs-write`
- Publishing to Confluence -> `adk-publish-confluence`
- Internal repo doc only -> just `adk-docs-write` to a tracked path
- Real-time collaborative editing of a Doc - use Google Docs directly

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<action>` | yes | `doc-create` / `doc-update` / `file-upload` / `share` |
| `<source>` | yes for create / update / upload | Path to markdown file (or PDF / other for upload) |
| `<folder>` | optional | Drive folder id (default: My Drive root) |
| `<file-id>` | yes for `doc-update` / `share` | Existing Drive file id |
| `<title>` | optional | Override the doc title (default: first H1 in markdown) |
| `<format>` | optional | `gdoc` (default) / `markdown` / `pdf` |
| `<share-with>` | optional | Email(s) for `share` action |
| `<role>` | optional for `share` | `reader` (default) / `commenter` / `writer` |
| `--auto` | optional | Skip confirmations on non-destructive actions |

## Workflow

1. **Confirm intent** - restate action, source, target folder/file, format, sharing. Approval gate unless `--auto`.
2. **Check tooling** - verify `google-drive` MCP is configured and authenticated. Stop with a clear install/config message if not.
3. **Read source** - load the markdown. Extract title from the first `# H1` if none was supplied.
4. **Convert** - depending on format:
   - `gdoc`: convert markdown -> Google Docs format (the MCP performs this; preserve headings, lists, tables, code blocks, links, inline formatting). Tables of contents and footnotes pass through where supported.
   - `markdown`: upload as-is with `text/markdown` MIME.
   - `pdf`: render markdown -> PDF (via the MCP or a local renderer) and upload.
5. **Apply action** - create the new file in the chosen folder, update the existing file, or set permissions.
6. **Verify** - re-fetch metadata to confirm: title matches, MIME correct, parent folder correct, version newer (for update), permissions present (for share).
7. **Report** - lead with the Drive URL; include action, format, verification status.

## Action playbooks

### doc-create

- Convert markdown -> gdoc.
- Create the file in the chosen folder.
- Capture `fileId`, `webViewLink`.

### doc-update

- Re-fetch the existing doc's metadata; capture current `modifiedTime`.
- Convert markdown -> gdoc.
- Update the existing file (replace body).
- Capture new `modifiedTime`; verify it is newer.

### file-upload

- Upload the source file as-is in the chosen MIME (`text/markdown`, `application/pdf`, etc.).
- Useful when the doc must remain pure markdown or be a PDF render.

### share

- Set the permission via the MCP:
  - reader: view only
  - commenter: view + comment
  - writer: edit
- For each email, return whether the permission was newly added or already existed.

## Output format

```
## Drive action: <action>
- Drive URL: <webViewLink>
- File id: <fileId>
- Title: <title>
- Folder: <folder name or root>
- Format: <gdoc | markdown | pdf>
- Tool used: google-drive MCP

## Verification
- Title matches: <YES>
- Body landed: <YES> (size: <bytes>)
- Permissions: <list of email -> role>

## Follow-up
- <e.g. "shared with @alice as commenter", "linked from runbook page">
```

## Hard rules

- Never delete or trash a Drive file from this skill. Deletion is an explicit, separate action.
- Always verify after publishing - the API can succeed and still produce empty bodies under some edge cases.
- Title comes from the H1 unless overridden; do not silently re-title an existing doc.
- Sharing changes are explicit; do not enable "anyone with link" without an explicit user request.
- Respect domain sharing policies - if the workspace blocks external sharing, surface the policy error rather than retrying with a different role.

## Markdown -> Google Doc quirks

- Tables convert to native Doc tables; merged cells are not preserved.
- Code blocks become monospaced paragraphs; language tags are not visually rendered.
- Image links require pre-uploaded Drive images or absolute public URLs.
- Footnote syntax may not survive; convert to inline references when needed.

## Anti-patterns

- Updating without first reading current `modifiedTime` (you cannot detect overwrite collisions).
- Pasting raw markdown into a Google Doc; convert first.
- Publishing without verifying the rendered output.
- Sharing publicly when the user only asked to share with one email.
- Hard-coding folder names; folder ids are stable, names collide.

## Examples

```
adk-publish-gdrive doc-create \
  --source .temp/drafts/proposal-q3-roadmap.md \
  --folder <folder-id> --share-with alice@example.com --role commenter
```

```
adk-publish-gdrive doc-update \
  --source .temp/drafts/proposal-q3-roadmap.md \
  --file-id <file-id>
```

```
adk-publish-gdrive file-upload \
  --source .temp/reports/audit-site-shop.md \
  --folder <folder-id> --format markdown
```

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/mcp-fallback.md` | Preferred MCP server and the manual fallback when it is missing. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |

<!-- adk:references:end -->
