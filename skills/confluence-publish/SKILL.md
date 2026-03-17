---
name: confluence-publish
description: Publish markdown content to Confluence with images, diagrams, and attachments
user_invocable: true
arguments:
  - name: source
    description: "Path to markdown file to publish"
    required: true
  - name: space
    description: "Confluence space key"
    required: true
  - name: parent
    description: "Parent page title or ID (optional)"
    required: false
  - name: title
    description: "Page title (default: extracted from markdown H1)"
    required: false
  - name: update
    description: "Page ID to update instead of creating new (optional)"
    required: false
---

# Confluence Publishing

Publish markdown content to Confluence with proper formatting, images, diagrams, and attachments. Handles the full conversion pipeline from markdown to Confluence storage format.

## Workflow

### Phase 1: Parse Markdown

Read and parse the source markdown file:

1. Read the file at the provided `source` path.
2. Extract the **title** from the first H1 heading (`# Title`). If the `title` argument is provided, use that instead.
3. Scan the document and identify:
   - **Images**: Both local file paths (e.g., `./diagrams/arch.jpg`) and remote URLs (e.g., `https://example.com/image.png`). Resolve relative paths against the markdown file's directory.
   - **Mermaid/Excalidraw references**: Links to `.mermaid` or `.excalidraw` source files, or inline mermaid code blocks.
   - **Code blocks**: Fenced code blocks with language identifiers.
   - **Tables**: Markdown tables.
   - **Links**: Internal and external links.
   - **Callouts/admonitions**: Blockquotes used as callouts (e.g., `> **Note:** ...`).

### Phase 2: Process Diagrams

For each diagram reference found in the markdown:

1. **Inline mermaid code blocks** (` ```mermaid ... ``` `):
   - Extract the mermaid source.
   - Save to a temporary `.mermaid` file.
   - Render to SVG first: `mmdc -i input.mermaid -o output.svg -b white`
   - Convert SVG to JPEG using the `/image-transform` skill (Confluence needs JPEG, not SVG).
   - If rendering fails, keep the code block as a Confluence code macro instead.

2. **Referenced `.mermaid` files** (linked or as image source):
   - Read the source file.
   - If no rendered image exists alongside it, render to SVG via `mmdc`, then convert to JPEG via `/image-transform`.
   - Prepare both the `.jpg` and `.mermaid` file for upload.

3. **Referenced `.excalidraw` files**:
   - Render to SVG using `npx excalidraw-to-svg <input>.excalidraw <output>.svg`.
   - Convert SVG to JPEG using the `/image-transform` skill.
   - If rendering tools are not available, check if a `.jpg` or `.png` already exists alongside the source.
   - Always upload the `.excalidraw` source as an attachment so readers can edit the diagram.

4. **SVG images** (`.svg`):
   - Convert to JPEG using the `/image-transform` skill before uploading (Confluence SVG rendering is inconsistent).
   - Upload both the JPEG (for display) and original SVG (as attachment).

5. **Raster images** (`.jpg`, `.png`, `.gif`):
   - Verify the file exists.
   - Add to the upload list.

### Phase 3: Convert to Confluence Format

Convert the markdown document to Confluence storage format (XHTML). Apply these conversion rules:

#### Headings
```
# H1       -->  <h1>H1</h1>
## H2      -->  <h2>H2</h2>
### H3     -->  <h3>H3</h3>
#### H4    -->  <h4>H4</h4>
```

#### Text Formatting
```
**bold**        -->  <strong>bold</strong>
*italic*        -->  <em>italic</em>
`inline code`   -->  <code>inline code</code>
~~strikethrough~~ --> <span style="text-decoration: line-through;">strikethrough</span>
```

#### Lists
```markdown
- item          -->  <ul><li>item</li></ul>
1. item         -->  <ol><li>item</li></ol>
- [ ] task      -->  <ac:task-list><ac:task><ac:task-status>incomplete</ac:task-status><ac:task-body>task</ac:task-body></ac:task></ac:task-list>
- [x] task      -->  <ac:task-list><ac:task><ac:task-status>complete</ac:task-status><ac:task-body>task</ac:task-body></ac:task></ac:task-list>
```

#### Code Blocks
````markdown
```python
code
```
````
Converts to:
```xml
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:plain-text-body><![CDATA[code]]></ac:plain-text-body>
</ac:structured-macro>
```

If the code block uses the `file=` property pattern (e.g., ` ```ts file=src/example.ts `), include the filename as a title:
```xml
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">typescript</ac:parameter>
  <ac:parameter ac:name="title">src/example.ts</ac:parameter>
  <ac:plain-text-body><![CDATA[code]]></ac:plain-text-body>
</ac:structured-macro>
```

#### Blockquotes
```markdown
> quote text
```
Converts to:
```xml
<ac:structured-macro ac:name="quote">
  <ac:rich-text-body><p>quote text</p></ac:rich-text-body>
</ac:structured-macro>
```

#### Tables
Convert markdown tables to HTML `<table>` with `<th>` for header cells:
```xml
<table>
  <thead><tr><th>Header 1</th><th>Header 2</th></tr></thead>
  <tbody><tr><td>Cell 1</td><td>Cell 2</td></tr></tbody>
</table>
```

#### Images (Local — uploaded as attachments)
```markdown
![Alt text](./diagrams/arch.jpg)
```
Converts to:
```xml
<ac:image ac:alt="Alt text">
  <ri:attachment ri:filename="arch.jpg"/>
</ac:image>
```

#### Images (Remote URLs)
```markdown
![Alt text](https://example.com/image.png)
```
Converts to:
```xml
<ac:image ac:alt="Alt text">
  <ri:url ri:value="https://example.com/image.png"/>
</ac:image>
```

#### Links
```markdown
[Link text](https://example.com)
```
Converts to:
```xml
<a href="https://example.com">Link text</a>
```

#### Horizontal Rules
```markdown
---
```
Converts to:
```xml
<hr/>
```

#### Diagram Source Attachments
Below each diagram image, add a link to download the source file:
```xml
<p><em>Diagram source: </em>
<ac:link><ri:attachment ri:filename="architecture.mermaid"/>
<ac:plain-text-link-body><![CDATA[architecture.mermaid]]></ac:plain-text-link-body>
</ac:link></p>
```

### Phase 4: Create/Update Page

Publish the converted content to Confluence:

- **If `update` is specified** (page ID provided):
  - Use `mcp__atlassian-confluence__confluence_update_page` to update the existing page.
  - Pass the page ID, new title (if changed), and the converted storage-format body.

- **If `update` is NOT specified** (creating a new page):
  - Use `mcp__atlassian-confluence__confluence_create_page` to create the page.
  - Pass the `space` key, `title`, and the converted storage-format body.
  - If `parent` is specified, set it as the parent page.

### Phase 5: Upload Attachments

After the page is created/updated (so you have the page ID), upload all attachments:

1. **For each local image** (`.jpg`, `.png`, `.gif`, `.svg`):
   - Use `mcp__atlassian-confluence__confluence_upload_attachment` to upload the file to the page.
   - The filename must match what is referenced in the `<ri:attachment ri:filename="..."/>` tags.

2. **For each diagram source file** (`.mermaid`, `.excalidraw`):
   - Use `mcp__atlassian-confluence__confluence_upload_attachment` to upload the source file.
   - This allows readers to download and edit the diagram source.

3. If uploading multiple files, use `mcp__atlassian-confluence__confluence_upload_attachments` (batch upload) if available to reduce API calls.

4. Note any upload failures and report them to the user.

### Phase 6: Verify & Label

After all uploads are complete:

1. **Verify**: Use `mcp__atlassian-confluence__confluence_get_page` to fetch the published page and confirm:
   - The page exists and is accessible.
   - The title is correct.
   - The content rendered without errors (no broken macro references).
   - Images display correctly (attachment references resolve).

2. **Label**: Use `mcp__atlassian-confluence__confluence_add_label` to add the label `published-via-devkit` to the page.

3. **Report** to the user:
   - The page URL.
   - The page ID (for future updates).
   - Number of attachments uploaded.
   - Any warnings or issues encountered.

Example output:
```
Published to Confluence:
  URL: https://yoursite.atlassian.net/wiki/spaces/ENG/pages/123456/My+Document
  Page ID: 123456
  Attachments: 4 uploaded (2 images, 2 diagram sources)
  Label: published-via-devkit

To update this page later, run:
  /confluence-publish --source=./doc.md --space=ENG --update=123456
```

## Important Rules

- Preserve all formatting and structure from the original markdown. Do not drop sections, reorder content, or summarize.
- Images MUST be uploaded as attachments AND referenced in the page body. The `<ri:attachment>` tags will not render unless the corresponding attachment exists.
- Below each diagram image, include a link to download the diagram source file so readers can edit the diagram.
- Always add the `published-via-devkit` label to identify pages managed by this tool.
- If the markdown file references files that do not exist, warn the user and skip those attachments rather than failing the entire publish.
- Handle large documents gracefully — Confluence has a storage format size limit. If the converted content exceeds reasonable limits, warn the user.
