# Markdown → GDoc / markdown upload / PDF

`docs-publish-gdrive` supports 3 output formats. Conversion rules
per format.

## Format 1: `gdoc` (default)

Target: Google Doc (mime `application/vnd.google-apps.document`).
The Google Drive API accepts a *structured document body* composed
of `insertText`, `updateParagraphStyle`, `insertTable`, etc.
operations. The skill builds this ops list into `converted.gdoc.json`
and sends it via `documents.batchUpdate` after the initial
`files.create` (or `files.update` for existing items).

### Mechanical mappings

| Markdown | GDoc op |
| --- | --- |
| `# H1` | `insertText` + `updateParagraphStyle: HEADING_1` |
| `## H2` | `updateParagraphStyle: HEADING_2` |
| `paragraph` | `insertText` + `NORMAL_TEXT` |
| `**bold**` | `insertText` + `updateTextStyle: bold=true` |
| `*italic*` | `insertText` + `updateTextStyle: italic=true` |
| `` `inline` `` | `updateTextStyle: weightedFontFamily: Courier New` |
| `[text](url)` | `insertText` + `updateTextStyle: link.url` |
| `unordered list` | `insertText` + `createParagraphBullets` |
| `ordered list` | `insertText` + `createParagraphBullets: NUMBERED_DECIMAL` |
| `blockquote` | `updateParagraphStyle: indentStart + italic true` |
| `hr` | `insertPageBreak` (no true HR in GDoc) OR a separator line |
| table | `insertTable` with rows/columns |

### Code fences

GDoc doesn't have a first-class "code block". The convention:

- Insert the code as text with font family `Courier New` (or
  `Roboto Mono` if available).
- Wrap in a table with 1 row × 1 column, gray background, so it
  visually reads as a block.

For languages: noted in a caption line above the table, `*(bash)*`.

### Mermaid fences

GDoc can't render Mermaid natively. Two strategies:

1. Render Mermaid to SVG via diagramkit (same as `docs-diagram`),
   then `insertInlineImage` with the SVG URL (requires the SVG to
   be accessible to the doc — upload to the same Drive folder
   first).
2. Fallback: insert the raw Mermaid source as a code block with
   a caption "Mermaid source (render externally)".

Default strategy is (2) unless diagramkit is available AND the SVG
upload succeeds.

### Frontmatter

Stripped; its `title:` drives the GDoc's `name`. Other keys
(`labels:` etc.) are ignored for GDoc (there's no native label
concept in GDoc; Drive labels exist but are out of scope).

## Format 2: `md` — upload as markdown file

- Mime: `text/markdown` (if the workspace supports it) or
  `text/plain`.
- Strip the leading frontmatter block only; leave the rest
  verbatim.
- Preserve line endings as LF.
- No structural conversion — the file is just stored in Drive as
  a text blob.

## Format 3: `pdf` — render PDF

- Requires `pandoc` on the local machine.
- Command:
  `pandoc <source.md> -o <converted.pdf> --toc --standalone --pdf-engine=xelatex`.
- Fallback `--pdf-engine=pdflatex` if xelatex isn't present.
- Mermaid fences: pandoc doesn't render Mermaid natively. The
  skill pre-processes:
  - For each mermaid fence, render via diagramkit to SVG, then
    replace the fence with `![caption](svg-path)`.
  - If diagramkit is missing, leave the fence as a plain code
    block (readable; not visual).

### PDF metadata

- Title: from frontmatter `title:` or H1.
- Author: from `~/.config/adk/info.md.name` (operator name).
- Subject: "adk-published".

## Conversion validator

Every converted artifact is checked by the skill's validator:

- For `gdoc`: ops JSON parses; every op is one of the allowed
  types.
- For `md`: no frontmatter block in the output; file is non-empty.
- For `pdf`: file is non-empty and starts with the `%PDF-` magic
  bytes.

## Errors during conversion

- Unknown code-fence language: upload as plain monospaced (not an
  error).
- Unsupported markdown feature (e.g. task lists inside tables for
  GDoc): surface as a warning in the report; convert to the closest
  supported equivalent.
- Conversion fails entirely: stop with the exact error + the
  markdown line that caused it.
