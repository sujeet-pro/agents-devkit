---
name: markdown
description: Generate well-structured GFM markdown documents as folder-based units with diagrams, code blocks, and proper file organization
user_invocable: true
arguments:
  - name: title
    description: "Document title"
    required: true
  - name: output-dir
    description: "Output directory (default: current directory)"
    required: false
  - name: frontmatter
    description: "Include YAML frontmatter: yes, no (default: no)"
    required: false
  - name: confluence-sync
    description: "Prepare for Confluence sync: yes, no (default: no)"
    required: false
  - name: doc-type
    description: "Document type for guideline loading: tdd, hld, lld, prd, blog, article, project, etc. (default: none)"
    required: false
---

# Markdown Document Generation

Generate well-structured GFM markdown documents as self-contained folder-based units with diagrams, code blocks, and proper file organization.

## Output Structure

Every document is a folder, not a single file:

```
<title-kebab-case>/
├── README.md                  # The document
├── diagrams/
│   ├── overview.excalidraw    # Source files
│   ├── overview.svg           # Rendered
│   ├── flow.mermaid
│   └── flow.svg
└── images/                    # Any other images
```

- The document folder name is the title converted to kebab-case.
- `README.md` is the main document file.
- `diagrams/` holds all diagram source files and their rendered SVGs.
- `images/` holds any non-diagram images (screenshots, photos, etc.).

## Workflow

### Step 1 — Guideline Loading

1. Check if the current directory is a git repository.
2. If yes, look for project-level markdown guidelines in this priority order:
   - `.markdown-guidelines.md` in the repo root
   - `MARKDOWN.md` in the repo root
   - A `## Markdown` or `## Documentation` section in the repo's `CLAUDE.md`
3. If any of the above are found, load them as **high-priority** guidelines (they override defaults).
4. **Always** load `guidelines/document/general.md` as the baseline guideline.
5. If `doc-type` is specified, load the type-specific guideline (e.g., `guidelines/document/blog.md` for `doc-type=blog`).

### Step 2 — Document Creation

1. Create the output folder at `<output-dir>/<title-kebab-case>/`.
2. Create `diagrams/` and `images/` subdirectories.
3. Generate `README.md` with the document content.

### Step 3 — Markdown Conventions

Follow these GFM conventions strictly:

- **GFM features**: tables, task lists (`- [ ]`), strikethrough (`~~text~~`), footnotes (`[^1]`), autolinks.
- **Admonitions**: Use GitHub-style callouts:
  ```markdown
  > [!NOTE]
  > Useful information that users should know.

  > [!WARNING]
  > Critical information demanding immediate attention.

  > [!TIP]
  > Helpful advice for doing things better or more easily.

  > [!IMPORTANT]
  > Key information users need to know to achieve their goal.

  > [!CAUTION]
  > Advises about risks or negative outcomes of certain actions.
  ```
- **Frontmatter**: No frontmatter by default. If `frontmatter=yes`, add a YAML frontmatter block with `title`, `date`, `description`, and any fields appropriate for the doc type.
- **Heading hierarchy**: Exactly one H1 (the document title). Sequential H2 → H3 → H4. Never skip levels.
- **Mermaid diagrams**: Include inline in the markdown as fenced code blocks AND save as separate `.mermaid` files in `diagrams/`.
- **Image references**: Always use relative paths: `![Alt text](./diagrams/overview.svg)`.

### Step 4 — Diagram Delegation

Delegate all diagram creation to the `/diagram` skill:

- **Overview / architecture diagrams** → Excalidraw (hand-drawn aesthetic, better for high-level views).
- **Detailed flow / sequence / state diagrams** → Mermaid (text-based, version-controllable).
- Save both the source file (`.excalidraw` or `.mermaid`) and the rendered `.svg` in the `diagrams/` directory.
- Reference rendered SVGs from the markdown document.

### Step 5 — Code Block Delegation

Delegate code block creation to the **code-snippet-agent**:

- Apply expressive-code features:
  - `title="filename.ts"` — file name labels on code blocks
  - `collapse={1-5}` — collapse import blocks or boilerplate
  - `{3,7-9}` — highlight key lines
- Ensure code blocks are realistic, runnable, and copy-pasteable where possible.

### Step 6 — Confluence Sync Mode

When `confluence-sync=yes`:

- All diagram source files (`.excalidraw`, `.mermaid`) are saved alongside rendered images.
- When published via `/confluence-publish`, source files are uploaded as attachments BELOW the rendered image so editors can download and modify them.
- Use **JPEG** for rendered images (better Confluence compatibility) via `/image-transform`.
- Structure paths for easy `/confluence-publish` consumption:
  ```
  <title-kebab-case>/
  ├── README.md
  ├── diagrams/
  │   ├── overview.excalidraw     # Source — uploaded as attachment
  │   ├── overview.jpg            # Rendered — embedded in page
  │   ├── flow.mermaid            # Source — uploaded as attachment
  │   └── flow.jpg                # Rendered — embedded in page
  └── images/
      └── screenshot.jpg          # Converted to JPEG
  ```

### Step 7 — Project Frontmatter

When `frontmatter=yes`, add a YAML frontmatter block at the top of `README.md`:

```yaml
---
title: "Document Title"
date: YYYY-MM-DD
description: "Brief description of the document"
author: ""
tags: []
status: draft
---
```

Add additional fields appropriate for the doc type (e.g., `version` for project docs, `category` for blog posts).

## Conventions Summary

| Convention | Rule |
|---|---|
| One H1 | Title only |
| Heading sequence | H2 → H3 → H4, never skip |
| Admonitions | `> [!NOTE]`, `> [!WARNING]`, etc. |
| Diagrams | Inline mermaid + separate source files |
| Images | Relative paths from document root |
| Code blocks | Expressive-code features via code-snippet-agent |
| Folder structure | Always folder-based, never a single loose file |
