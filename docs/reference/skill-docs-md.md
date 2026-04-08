---
title: "docs-md"
description: Markdown feature detection and formatting guidelines — pagesmith, GitHub, and plain markdown
skill_name: docs-md
category: helper
workflow_tier: helper
user_invocable: false
---

# docs-md

Detects the markdown rendering target for the current repository and loads the appropriate formatting guidelines. Other skills invoke this before writing or reviewing markdown content to ensure output uses only supported features.

## Purpose

- Detect the markdown rendering target (pagesmith, GitHub, or plain) from project configuration
- Load feature-specific formatting guidelines for the detected target
- Provide a feature inventory so calling skills know which markdown features are safe to use
- Prevent use of unsupported features (e.g., expressive code on GitHub, math on plain markdown)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--target` | `pagesmith` \| `github` \| `plain` | auto-detect | Force a specific rendering target |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Auto-detect (default)** | Infers target from project configuration files and git remote. Detection order: pagesmith → GitHub → plain (first match wins) |
| **`--target pagesmith`** | Loads full pagesmith feature set (GFM, alerts, math, expressive code, smart typography, frontmatter) |
| **`--target github`** | Loads GitHub-Flavored Markdown features (GFM, alerts, mermaid, math, standard code blocks) |
| **`--target plain`** | Loads CommonMark with minimal GFM extensions. No alerts, math, mermaid, or expressive code |

## Target Detection Logic

Checks run in order; first match wins:

1. **Pagesmith**: `pagesmith.config.json5` or `pagesmith.config.json` in the repo root or any parent directory
2. **GitHub**: `.github/` directory OR a git remote URL containing `github.com`
3. **Plain**: default when neither pagesmith nor GitHub is detected

## Feature Reference by Target

### Pagesmith

Full feature set provided by `@pagesmith/core`:

| Feature | Syntax | Notes |
|---------|--------|-------|
| GFM tables | Pipe-delimited with header separator | Standard |
| Strikethrough | `~~deleted text~~` | Standard |
| Task lists | `- [ ]` / `- [x]` | Standard |
| Autolinks | Bare URLs and emails | Standard |
| Footnotes | `[^1]` reference / `[^1]: definition` | Standard |
| GitHub alerts | `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]` | Five types |
| Math (inline) | `$E = mc^2$` | Via remark-math + rehype-mathjax |
| Math (display) | `$$\sum_{i=1}^{n} x_i$$` | Via remark-math + rehype-mathjax |
| Expressive Code | `title`, `showLineNumbers`, `mark`, `ins`, `del`, `collapse` | Dual-theme syntax highlighting |
| Smart typography | Standard quotes/dashes → curly quotes, em dashes, ellipses | Automatic |
| External links | Auto `target="_blank"` and `rel="noopener noreferrer"` | Automatic |
| Heading IDs | Auto-generated slug-based IDs | Anchor links via `#heading-slug` |
| Accessible emoji | `role="img"` + `aria-label` wrapping | Automatic |
| Frontmatter | `title`, `description`, `navLabel`, `sidebarLabel`, `order`, `draft`, `socialImage`, `layout` | Only with pagesmith config |
| Content structure | `folder/README.md` as section index, `meta.json5` for ordering | Pagesmith convention |

### GitHub

Standard GitHub-Flavored Markdown:

| Feature | Syntax | Notes |
|---------|--------|-------|
| GFM tables | Pipe-delimited with header separator | Standard |
| Strikethrough | `~~deleted text~~` | Standard |
| Task lists | `- [ ]` / `- [x]` | Standard |
| Autolinks | Bare URLs | Standard |
| Footnotes | `[^1]` reference / `[^1]: definition` | Standard |
| GitHub alerts | `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]` | Natively rendered |
| Mermaid diagrams | `` ```mermaid `` code blocks | Natively rendered |
| Math (inline) | `$E = mc^2$` | Via MathJax |
| Math (display) | `$$\sum_{i=1}^{n} x_i$$` | Via MathJax |
| Syntax highlighting | Fenced code blocks with language tags | No titles, line marks, or line numbers |
| Frontmatter | Not recommended | Renders as a table at the top |

### Plain Markdown

Standard CommonMark with minimal GFM:

| Feature | Syntax | Notes |
|---------|--------|-------|
| Headings | ATX-style `#` through `######` | Standard |
| Emphasis | `*italic*`, `**bold**`, `***bold italic***` | Standard |
| Lists | Ordered and unordered with nesting | Standard |
| Links | Inline `[text](url)` and reference-style | Standard |
| Images | `![alt](url)` | Standard |
| Blockquotes | `> quoted text` | Standard |
| Code | Inline `` `code` `` and fenced blocks | Standard |
| Tables | Pipe-delimited GFM tables | Widely supported |
| Strikethrough | `~~text~~` | Widely supported |
| No alerts | Use `> **Note:** ...` as fallback | Not supported |
| No math | Unless invoking skill confirms MathJax/KaTeX | Not supported |
| No mermaid | Not supported | Not supported |
| No expressive code | Not supported | Not supported |

## Key Behaviors

- **Ordered detection**: checks for pagesmith config first, then GitHub markers, then falls back to plain
- **Feature inventory**: provides a clear list of available features so calling skills constrain their output
- **Minimal token usage**: only loads the feature reference for the detected target
- **No workflow ownership**: this is a helper skill — the invoking skill owns the 6-phase workflow

## Output Format

Produces a summary for the calling skill:

```
## Markdown Guidelines Loaded

Target: pagesmith (detected via pagesmith.config.json5)

Available features:
- GFM: tables, strikethrough, task lists, autolinks, footnotes
- Alerts: NOTE, TIP, IMPORTANT, WARNING, CAUTION
- Math: inline ($) and display ($$)
- Expressive Code: titles, line numbers, mark/ins/del, collapse
- Smart typography: curly quotes, em dashes, ellipses
- Frontmatter: title, description, navLabel, sidebarLabel, order, draft, socialImage, layout
```

## Invoked By

| Skill | Context |
|-------|---------|
| `/adk:docs-write` | Before writing any document, to determine available markdown features |
| `/adk:docs-review` | Before reviewing markdown content, to validate feature usage |
| `/adk:docs-confluence` | When converting between Confluence storage format and markdown |
| `/adk:spec` | Before writing specifications in markdown |

## Examples

```
(invoked automatically by /adk:docs-write, /adk:docs-review, /adk:docs-confluence, /adk:spec)
/adk:docs-md --target pagesmith
/adk:docs-md --target github
```
