---
title: Markdown Reference
description: Complete reference for every markdown pipeline feature available in @pagesmith/core — syntax, output, and configuration.
---

# Markdown Reference

Every feature listed here is enabled by default in `@pagesmith/core`. No configuration or additional plugins are required unless noted otherwise.

## GitHub Flavored Markdown

Enabled via `remark-gfm`. All GFM extensions are available out of the box.

### Tables

```markdown
| Feature       | Syntax        |
| ------------- | ------------- |
| Bold          | `**bold**`    |
| Italic        | `*italic*`    |
| Strikethrough | `~~deleted~~` |
```

Alignment is controlled by colons in the separator row:

```markdown
| Left | Center | Right |
| :--- | :----: | ----: |
| text |  text  |  text |
```

### Strikethrough

```markdown
~~removed text~~
```

### Task Lists

```markdown
- [x] Completed task
- [ ] Pending task
- [ ] Another todo
```

### Autolinks

Bare URLs are automatically converted to clickable links:

```markdown
Visit https://example.com for details.
```

### Footnotes

```markdown
This claim needs a source[^1].

[^1]: The source for this claim.
```

The footnote content renders at the bottom of the page with a back-link.

## GitHub Alerts

Five alert types are available using blockquote syntax. This is the same format used by GitHub itself.

```markdown
> [!NOTE]
> Useful information the reader should know.

> [!TIP]
> Helpful advice for doing things better.

> [!IMPORTANT]
> Key information the reader must not miss.

> [!WARNING]
> Something that needs immediate attention.

> [!CAUTION]
> Negative potential consequences of an action.
```

| Type           | Color  | Use For                                |
| -------------- | ------ | -------------------------------------- |
| `[!NOTE]`      | Blue   | General supplementary information      |
| `[!TIP]`       | Green  | Helpful suggestions and best practices |
| `[!IMPORTANT]` | Purple | Key details the reader must know       |
| `[!WARNING]`   | Yellow | Things to watch out for                |
| `[!CAUTION]`   | Red    | Dangerous actions or breaking changes  |

## Math

LaTeX math is processed by `remark-math` (parsing) and `rehype-mathjax` (SVG rendering). `remark-math` only runs when `markdown.math` is `true` or when the default `'auto'` mode detects math markers in the page. MathJax runs before the built-in code renderer so math blocks are not mistakenly treated as code.

### Inline Math

Wrap expressions in single dollar signs:

```markdown
The equation $E = mc^2$ changed physics.
```

### Display Math

Wrap expressions in double dollar signs for centered block equations:

```markdown
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

## Smart Typography

ASCII punctuation is automatically upgraded to proper typographic characters by `remark-smartypants`. Code blocks and inline code are never affected.

| Input     | Output            | Description         |
| --------- | ----------------- | ------------------- |
| `"hello"` | \u201chello\u201d | Curly double quotes |
| `'hello'` | \u2018hello\u2019 | Curly single quotes |
| `--`      | \u2013            | En dash             |
| `---`     | \u2014            | Em dash             |
| `...`     | \u2026            | Ellipsis            |

## External Links

Any link pointing to an absolute URL (`http://` or `https://`) automatically receives `target="_blank"` and `rel="noopener noreferrer"`. Internal links (relative paths, anchors) are unaffected.

```markdown
[External](https://example.com) <!-- new tab, noopener -->
[Internal](../../guide/getting-started/README.md) <!-- same tab -->
[Anchor](#math) <!-- same tab -->
```

## Images

All markdown images are automatically wrapped in `<figure class="ps-figure ps-figure-zoomable">` and given a hidden expand button (`<button class="ps-img-zoom-btn" hidden data-ps-img-zoom-btn>`). Raster images (PNG, JPEG, WebP, GIF) also get a `<picture>` element with WebP and AVIF `<source>` variants. SVG images get figure wrapping but no `<picture>` element. Images inside links are not figure-wrapped and do not receive a zoom button. The image carries `data-zoom-src` (raster → `<stem>.zoom.webp`, SVG → original `src`); themed light/dark pairs carry `data-zoom-src-light` / `data-zoom-src-dark`. Pair with `@pagesmith/site/runtime/image-zoom` for the modal.

The title attribute from markdown syntax becomes a `<figcaption>`:

```markdown
![Dashboard metrics](./hero.png "Production monitoring dashboard")
```

Produces:

```html
<figure class="ps-figure ps-figure-zoomable">
  <picture>
    <source srcset="./hero.avif" type="image/avif" />
    <source srcset="./hero.webp" type="image/webp" />
    <img
      src="./hero.webp"
      alt="Dashboard metrics"
      width="..."
      height="..."
      data-zoom-src="./hero.zoom.webp"
      data-zoom-type="image/webp"
    />
  </picture>
  <figcaption>Production monitoring dashboard</figcaption>
  <button type="button" class="ps-img-zoom-btn" hidden data-ps-img-zoom-btn>...</button>
</figure>
```

### Automatic Light/Dark Pair Merging

Consecutive images whose filenames end with `-light` and `-dark` suffixes are automatically merged into a single themed figure. No manual HTML is needed:

```markdown
![Architecture overview](./diagrams/arch-light.svg)
![Architecture overview](./diagrams/arch-dark.svg)
```

Produces a `<figure class="ps-figure ps-figure-themed ps-figure-zoomable">` with `<source media="(prefers-color-scheme: dark)">` so the correct variant displays without JavaScript. The inner `<img>` carries `data-zoom-src-light` and `data-zoom-src-dark` so the zoom modal swaps source on theme change.

## Theme-Aware Images

Images and other elements can respond to the active color scheme. The pipeline handles figure wrapping and light/dark pairing automatically for markdown images (see above). Prefer markdown image syntax over raw HTML for all images.

### Light/dark image pairs

Place light and dark variants consecutively using standard markdown images. The pipeline auto-merges them:

```markdown
![Architecture overview](./diagrams/arch-light.svg "Build pipeline architecture")
![Architecture overview](./diagrams/arch-dark.svg)
```

The title on the first (light) image becomes the `<figcaption>`. In `color-scheme-auto` (the default), the switch follows the OS preference. In explicit light or dark mode, the matching variant is forced.

### Generic show/hide helpers

```html
<span class="show-on-light">Light content</span> <span class="show-on-dark">Dark content</span>
```

Works on any element, not just images.

### Invert on dark

```markdown
![Request path from client through API gateway to database and back](./simple-diagram.invert.svg "Request lifecycle")
```

Images with `.invert.` in their filename receive the `invert-on-dark` class automatically, which applies `invert(1) hue-rotate(180deg)` in dark mode.

## Accessible Emojis

Emoji characters are wrapped in `<span role="img" aria-label="...">` so screen readers announce the emoji name.

```markdown
Build complete! 🎉
```

Produces:

```html
Build complete! <span role="img" aria-label="party popper">🎉</span>
```

## Heading IDs and Anchors

Every heading gets a URL-safe `id` (via `rehype-slug`) and the heading text is wrapped in an anchor link (via `rehype-autolink-headings`).

```markdown
## Getting Started
```

Produces:

```html
<h2 id="getting-started"><a href="#getting-started">Getting Started</a></h2>
```

These IDs power the table-of-contents sidebar and enable deep-linking to any section.

## Code Blocks

Code blocks are rendered by the built-in Pagesmith renderer on top of Shiki with syntax highlighting, dual themes, copy/collapse controls, and shared Pagesmith chrome.

### Basic Highlighting

Use a fenced code block with a language identifier:

````markdown
```ts
const greeting = "Hello, world!";
```
````

Over 100 languages are supported via Shiki.

### File Titles

Add `title="..."` to show a filename or label above the block:

````markdown
```ts title="vite.config.ts"
import { defineConfig } from "vite";
export default defineConfig({});
```
````

### Line Numbers

Line numbers are shown by default. Control them per-block:

````markdown
```bash showLineNumbers=false
npm install @pagesmith/core
```

```ts startLineNumber=42
export function resolve() {
  /* ... */
}
```
````

Configure the site-wide default:

```ts
markdown: {
  shiki: { defaultShowLineNumbers: false },
}
```

### Line Highlighting

Mark, insert, or delete lines to draw attention:

````markdown
```ts mark={2-3}
const name = "Pagesmith";
const version = "0.8.0";
const highlighted = true;
```

```ts ins={2} del={1}
const old = "before";
const updated = "after";
```
````

Range syntax supports individual lines and ranges: `mark={1, 3-5, 8}`.

### Diff Highlighting

Use the `diff` language for unified diff format:

````markdown
```diff
- const port = 3000
+ const port = process.env.PORT || 3000
```
````

### Collapsible Sections

Hide boilerplate that readers can expand on click:

````markdown
```ts collapse={1-5}
import { defineConfig } from "vite";
import { pagesmithContent, pagesmithSsg } from "@pagesmith/site/vite";
import collections from "./content.config";
import path from "node:path";
export default defineConfig({
  plugins: [pagesmithContent(collections), pagesmithSsg()],
});
```
````

### Text Wrapping

Enable word wrapping for long lines:

````markdown
```json wrap
{
  "name": "@pagesmith/core",
  "description": "A very long description that would overflow",
  "version": "0.8.0"
}
```
````

### Frame Styles

Terminal languages (`bash`, `sh`, `zsh`, `shell`, `powershell`) use a terminal frame. Override explicitly:

````markdown
```bash frame="none"
npm install @pagesmith/core
```
````

Values: `"code"` (editor frame), `"terminal"`, or `"plain"` (alias `"none"`). When `frame=` is omitted, terminal-style languages auto-select `"terminal"` and everything else auto-selects `"code"`.

### Meta String Quick Reference

All properties go after the language identifier in the opening fence:

| Property          | Syntax                       | Description                       |
| ----------------- | ---------------------------- | --------------------------------- |
| `title`           | `title="file.ts"`            | Filename or label above the block |
| `showLineNumbers` | `showLineNumbers=false`      | Show or hide line numbers         |
| `startLineNumber` | `startLineNumber=42`         | Start numbering from a given line |
| `mark`            | `mark={3}` or `mark={1,3-5}` | Highlight lines (neutral)         |
| `ins`             | `ins={2-3}`                  | Mark lines as inserted (green)    |
| `del`             | `del={1}`                    | Mark lines as deleted (red)       |
| `collapse`        | `collapse={1-5}`             | Collapse a range of lines         |
| `wrap`            | `wrap`                       | Enable word wrapping              |
| `frame`           | `frame="terminal"`           | Override the frame style          |

Combine multiple properties on the same fence:

````markdown
```ts title="example.ts" mark={3} ins={5} collapse={1-2}
import { z } from "zod";
import { defineCollection } from "@pagesmith/core";
const posts = defineCollection({
  loader: "markdown",
  directory: "content/posts",
  schema: z.object({ title: z.string() }),
});
```
````

## Code Tabs

Consecutive titled code blocks are automatically grouped into a tabbed interface. Write titled fenced blocks one after another with no other content between them:

````markdown
```bash title="npm"
npm install @pagesmith/core
```

```bash title="pnpm"
pnpm add @pagesmith/core
```

```bash title="yarn"
yarn add @pagesmith/core
```

```bash title="bun"
bun add @pagesmith/core
```
````

Rendered sample:

```bash title="npm"
npm install @pagesmith/core
```

```bash title="pnpm"
pnpm add @pagesmith/core
```

```bash title="yarn"
yarn add @pagesmith/core
```

```bash title="bun"
bun add @pagesmith/core
```

The `title` value becomes the tab label. The first tab is active by default.

### Rules

- Every block in the group must have a `title` — an untitled block breaks the group.
- Any non-code content (paragraph, heading, list) between titled blocks breaks the group.
- Each group is independent; a page can have multiple tab groups.
- Without JavaScript, all blocks stack vertically as a no-JS fallback.

### Multi-Language Example

````markdown
```ts title="TypeScript"
interface Config {
  host: string;
  port: number;
}
```

```python title="Python"
@dataclass
class Config:
    host: str = "localhost"
    port: int = 3000
```

```go title="Go"
type Config struct {
    Host string
    Port int
}
```
````

Rendered sample:

```ts title="TypeScript"
interface Config {
  host: string;
  port: number;
}
```

```python title="Python"
@dataclass
class Config:
    host: str = "localhost"
    port: int = 3000
```

```go title="Go"
type Config struct {
    Host string
    Port int
}
```

## Language Aliases

Some languages that Shiki does not recognize natively are aliased to a supported language for highlighting:

| Alias        | Highlighted As |
| ------------ | -------------- |
| `dot`        | `text`         |
| `mermaid`    | `text`         |
| `plantuml`   | `text`         |
| `excalidraw` | `json`         |
| `drawio`     | `xml`          |
| `proto`      | `protobuf`     |
| `ejs`        | `html`         |
| `hbs`        | `handlebars`   |

Add custom aliases via `markdown.shiki.langAlias`:

```ts
markdown: {
  shiki: {
    langAlias: {
      myLang: 'typescript',
    },
  },
}
```

User aliases take precedence over the defaults.

## Dual Themes

Code blocks support light and dark themes simultaneously. The default pair is `github-light` / `github-dark`. A `prefers-color-scheme` media query switches between them automatically.

Configure custom theme pairs:

```ts
markdown: {
  shiki: {
    themes: {
      light: 'catppuccin-latte',
      dark: 'catppuccin-mocha',
    },
  },
}
```

Pagesmith maps themes to `.color-scheme-light` and `.color-scheme-dark` CSS classes on `<html>`, so theme switching integrates with the site-wide color scheme toggle.

## Custom Plugins

Extend the pipeline with your own remark or rehype plugins:

```ts
import remarkToc from "remark-toc";
import rehypeFigure from "rehype-figure";

const config = defineConfig({
  collections: { posts },
  markdown: {
    remarkPlugins: [remarkToc],
    rehypePlugins: [[rehypeFigure, { className: "figure" }]],
  },
});
```

Tuple form `[plugin, options]` is supported for both remark and rehype.

**Injection points:**

- **Remark plugins** run after the built-in remark plugins (GFM, frontmatter, alerts, smartypants, and conditional math) but before `remark-rehype`.
- **Rehype plugins** run after the built-in rehype plugins (built-in code renderer, code tabs, scrollable tables, slug, autolink, external links, emojis, local images) and after the separate heading-extraction pass, but before `rehype-stringify`.

Content plugins (`ContentPlugin.remarkPlugin` / `ContentPlugin.rehypePlugin`) are appended after the config-level plugins.

`allowDangerousHtml` defaults to `true`, so raw HTML is preserved unless you explicitly disable it. `math` defaults to `'auto'`, which enables `remark-math` and `rehype-mathjax` only for content that contains math markers.

## Pipeline Order

The full unified pipeline, in execution order:

```text
remark-parse              Parse markdown to MDAST
remark-gfm                Tables, strikethrough, task lists, autolinks, footnotes
remark-frontmatter        Strip YAML frontmatter from AST
remark-github-alerts      > [!NOTE], > [!TIP], etc.
remark-smartypants        Smart quotes, dashes, ellipses
remark-math               Math syntax ($...$, $$...$$) when enabled or auto-detected
[user remark plugins]     From MarkdownConfig.remarkPlugins
lang-alias transform      Map fenced-code language tags via shiki.langAlias
remark-rehype             Markdown AST → HTML AST
rehype-mathjax            Render math to SVG (before the built-in code renderer)
applyPagesmithCodeRenderer Syntax highlighting, code frames, copy button
rehype-code-tabs          Group consecutive titled blocks into tabs
rehype-scrollable-tables  Wrap markdown tables for horizontal scrolling
rehype-slug               Add id="" to headings
rehype-autolink-headings  Wrap heading text in anchor links
rehype-external-links     target="_blank" on external URLs
rehype-accessible-emojis  aria-label on emoji characters
rehype-local-images       Figure wrapping, picture element for raster images, light/dark pair merging
heading extraction        Collect headings for TOC data
[user rehype plugins]     From MarkdownConfig.rehypePlugins
rehype-stringify          HTML AST → HTML string
```
